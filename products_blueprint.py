from flask import Blueprint, jsonify
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras

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