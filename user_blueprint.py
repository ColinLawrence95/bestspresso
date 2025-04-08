from flask import Blueprint, g, jsonify
from db_helpers import get_user_balance, get_db_connection
from auth_middleware import token_required

user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route("/balance", methods=["GET"])
@token_required
def check_balance():
    user_id = g.user.get("id")
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401
    
    try:
        balance = get_user_balance(user_id)
        return jsonify({"balance": float(balance)}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch balance: {str(e)}'}), 500
    
@user_blueprint.route('/purchases', methods=['GET'])
@token_required
def get_purchases():
    user_id = g.user.get('id')
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT p.id, p.purchase_date, p.total,
                   pi.id, pi.product_id, pi.name, pi.price, pi.quantity, pi.subtotal
            FROM purchases p
            LEFT JOIN purchase_items pi ON p.id = pi.purchase_id
            WHERE p.user_id = %s
            ORDER BY p.purchase_date DESC
        """, (user_id,))
        rows = cursor.fetchall()

        purchases = {}
        for row in rows:
            purchase_id, date, total, item_id, product_id, name, price, quantity, subtotal = row
            if purchase_id not in purchases:
                purchases[purchase_id] = {
                    'id': purchase_id,
                    'date': date.isoformat(),
                    'total': float(total),
                    'items': []
                }
            if item_id:  # If there’s an item
                purchases[purchase_id]['items'].append({
                    'id': item_id,
                    'product_id': product_id,
                    'name': name,
                    'price': float(price),
                    'quantity': quantity,
                    'subtotal': float(subtotal)
                })

        cursor.close()
        connection.close()
        return jsonify({'purchases': list(purchases.values())}), 200
    except Exception as e:
        if 'connection' in locals():
            connection.close()
        return jsonify({'error': f'Failed to fetch purchases: {str(e)}'}), 500
     
