from flask import Blueprint, jsonify
from db_helpers import get_db_connection

products_blueprint = Blueprint("products" , __name__)

@products_blueprint.route("", methods=["GET"])
def get_all_products():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, description, price, stock, created_at FROM products")
        products = cursor.fetchall()
        
        if not products:
            return jsonify ({"message": "No Products Found", "products": []}), 200
        
        product_list = [{
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': float(row[3]),
            'stock': row[4],
            'created_at': row[5].isoformat()
        } for row in products]
        
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
            SELECT id, name, description, price, stock, created_at 
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
            'created_at': product[5].isoformat()
        }

        cursor.close()
        connection.close()
        return jsonify(product_detail)
    except Exception as e:
        if 'connection' in locals():
            connection.close()
        return jsonify({'error': f'Failed to fetch product: {str(e)}'}), 500
    
    

