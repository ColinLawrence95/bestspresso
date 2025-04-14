from flask import Blueprint, jsonify, g
from db_helpers import get_db_connection
from flask import request
from auth_middleware import token_required
import random

COFFEE_PHOTOS = [
    "/static/images/coffee1.jpg",
    "/static/images/coffee2.jpg",
    "/static/images/coffee3.jpg",
    "/static/images/coffee4.jpg",
    "/static/images/coffee5.jpg",
    "/static/images/coffee6.jpg",
    "/static/images/coffee7.jpg",
    "/static/images/coffee8.jpg",
    "/static/images/coffee9.jpg",
    "/static/images/coffee10.jpg",
]

products_blueprint = Blueprint("products" , __name__)

@products_blueprint.route("", methods=["GET"])
def get_all_products():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, description, price, stock, rating, photo_url FROM products")
        products = cursor.fetchall()

        for product in products:
            if product[6] is None:  # photo_url
                random_photo = random.choice(COFFEE_PHOTOS)
                cursor.execute('UPDATE products SET photo_url = %s WHERE id = %s', (random_photo, product[0]))
                connection.commit()
        
        # Re-fetch to include updated photo_url
        cursor.execute("SELECT id, name, description, price, stock, rating, photo_url FROM products")
        products = cursor.fetchall()

        if not products:
            cursor.close()
            connection.close()
            return jsonify({"message": "No Products Found", "products": []}), 200
        
        
        product_list = [{
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': float(row[3]),
            'stock': row[4],
            'rating': float(row[5]) if row[5] is not None else 0.0,
            'photo_url': row[6]
        } for row in products]
        print(product_list[6])
        
        cursor.close()
        connection.close()
        return jsonify({'products': product_list}), 200
        
    except Exception as e:
        if 'connection' in locals():
            connection.close()
        return jsonify({'error': f'Failed to fetch products: {str(e)}'}), 500
    
@products_blueprint.route("/<int:id>", methods=["GET"])
def get_product_detail(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, name, description, price, stock, rating, photo_url
            FROM products 
            WHERE id = %s
        """, (id,))
        product = cursor.fetchone()

        if not product:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Product not found'}), 404
        
        product_detail = {
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'price': float(product[3]),
            'stock': product[4],
            'rating': float(product[5]) if product[5] is not None else 0.0,
            'photo_url': product[6]
        }

        cursor.close()
        connection.close()
        return jsonify(product_detail)
    except Exception as e:
        if 'connection' in locals():
            connection.close()
        return jsonify({'error': f'Failed to fetch product: {str(e)}'}), 500
    
@products_blueprint.route('/<int:id>/rate', methods=['POST'])
@token_required
def rate_product(id):
    user_id = g.user.get('id')
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401

    data = request.get_json()
    rating = data.get('rating')

    if rating is None or not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
        return jsonify({'error': 'Rating must be a number between 0 and 5'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM products WHERE id = %s", (id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'error': 'Product not found'}), 404

        cur.execute("""
            INSERT INTO product_ratings (user_id, product_id, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, product_id) 
            DO UPDATE SET rating = EXCLUDED.rating, created_at = CURRENT_TIMESTAMP
        """, (user_id, id, float(rating)))

        cur.execute("""
            UPDATE products 
            SET rating = (
                SELECT AVG(rating) 
                FROM product_ratings 
                WHERE product_id = %s
            )
            WHERE id = %s
        """, (id, id))

        conn.commit()
        
        cur.execute("SELECT rating FROM products WHERE id = %s", (id,))
        new_avg = cur.fetchone()[0]
        print(f"New average rating for product ID {id}: {new_avg}")

        cur.close()
        conn.close()
        return jsonify({'message': 'Rating updated successfully'}), 200
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print(f"Error: {str(e)}")
        return jsonify({'error': f'Failed to update rating: {str(e)}'}), 500
    

