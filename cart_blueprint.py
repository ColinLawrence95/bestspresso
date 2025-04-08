from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection, get_user_balance
from auth_middleware import token_required
from decimal import Decimal

cart_blueprint = Blueprint("cart", __name__)

@cart_blueprint.route("/add", methods=["POST"])
@token_required
def add_to_cart():
    user_id = g.user.get("id")
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401
    
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id or quantity < 1:
        return jsonify({'error': 'Invalid product_id or quantity'}), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if not product or product[0] < quantity:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Product not found or out of stock'}), 400
        
        cursor.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
        cart = cursor.fetchone()
        if not cart:
            cursor.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING id", (user_id,))
            cart_id = cursor.fetchone()[0]
        else:
            cart_id = cart[0]

        cursor.execute("SELECT id, quantity FROM cart_items WHERE cart_id = %s AND product_id = %s", (cart_id, product_id))
        cart_item = cursor.fetchone()
        if cart_item:
            new_quantity = cart_item[1] + quantity
            cursor.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_quantity, cart_item[0]))
        else:
            cursor.execute("INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (%s, %s, %s)", 
                        (cart_id, product_id, quantity))

        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Item added to cart'}), 201
    except Exception as e:
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        return jsonify({'error': f'Failed to add to cart: {str(e)}'}), 500

@cart_blueprint.route('', methods=['GET'])
@token_required 
def view_cart():
    user_id = g.user.get('id')  
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT ci.id, ci.product_id, p.name, p.price, ci.quantity
            FROM carts c
            JOIN cart_items ci ON c.id = ci.cart_id
            JOIN products p ON ci.product_id = p.id
            WHERE c.user_id = %s
        """, (user_id,))
        items = cursor.fetchall()

        balance = get_user_balance(user_id)

        if not items:
            cursor.close()
            connection.close()
            return jsonify({'items': [], 'total': 0.0, "balance": float(balance)}), 200

        cart_items = [{
            'id': row[0],
            'product_id': row[1],
            'name': row[2],
            'price': float(row[3]),
            'quantity': row[4],
            'subtotal': float(row[3]) * row[4]
        } for row in items]

        total = sum(item['subtotal'] for item in cart_items)
        cursor.close()
        connection.close()
        return jsonify({'items': cart_items, 'total': total, "balance": float(balance)}), 200
    except Exception as e:
        if 'connection' in locals():
            connection.close()
        return jsonify({'error': f'Failed to fetch cart: {str(e)}'}), 500
        
@cart_blueprint.route('/item/<int:id>', methods=['DELETE'])
@token_required
def remove_cart_item(id):
    user_id = g.user.get('id')
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT ci.id 
            FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.id
            WHERE ci.id = %s AND c.user_id = %s
        """, (id, user_id))
        cart_item = cursor.fetchone()

        if not cart_item:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Cart item not found or not authorized'}), 404

      
        cursor.execute("DELETE FROM cart_items WHERE id = %s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Item removed from cart'}), 200
    except Exception as e:
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        return jsonify({'error': f'Failed to remove item: {str(e)}'}), 500
    
@cart_blueprint.route('/item/<int:id>', methods=['PUT'])
@token_required
def update_cart_item(id):
    user_id = g.user.get('id')
    print(f"Updating cart item: id={id}, user_id={user_id}")
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401

    data = request.get_json()
    quantity = data.get('quantity')
    print(f"Request data: {data}, quantity={quantity}")

    if not quantity or quantity < 1:
        return jsonify({'error': 'Invalid quantity'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT ci.quantity, p.stock
            FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.id
            JOIN products p ON ci.product_id = p.id
            WHERE ci.id = %s AND c.user_id = %s
        """, (id, user_id))
        result = cur.fetchone()
        print(f"Query result: {result}")

        if not result:
            cur.close()
            conn.close()
            return jsonify({'error': 'Cart item not found'}), 404

        current_quantity, stock = result
        print(f"Current quantity: {current_quantity}, Stock: {stock}")
        if quantity > stock:
            cur.close()
            conn.close()
            return jsonify({'error': 'Insufficient stock'}), 400

        cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (quantity, id))
        conn.commit()
        print("Update successful")
        cur.close()
        conn.close()
        return jsonify({'message': 'Cart item updated'}), 200
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print(f"Error updating cart item: {str(e)}")
        return jsonify({'error': f'Failed to update cart item: {str(e)}'}), 500
    
@cart_blueprint.route('/purchase', methods=['POST'])
@token_required
def purchase_cart():
    user_id = g.user.get('id')
    if not user_id:
        return jsonify({'error': 'User ID not found in token'}), 401
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ci.id, ci.product_id, p.name, p.price, ci.quantity, p.stock
            FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.id
            JOIN products p ON ci.product_id = p.id
            WHERE c.user_id = %s
        """, (user_id,))
        items = cursor.fetchall()
        if not items:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Cart is empty'}), 400

        total = sum(float(row[3]) * row[4] for row in items) 
        balance = get_user_balance(user_id)
        balance_float = float(balance)
        if total > balance:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Insufficient balance'}), 400

        cursor.execute("""
            INSERT INTO purchases (user_id, total)
            VALUES (%s, %s) RETURNING id
        """, (user_id, total))
        purchase_id = cursor.fetchone()[0]

        for item in items:
            _, product_id, name, price, quantity, stock = item
            subtotal = float(price) * quantity
            cursor.execute("""
                INSERT INTO purchase_items (purchase_id, product_id, name, price, quantity, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (purchase_id, product_id, name, price, quantity, subtotal))
        
            cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (stock - quantity, product_id))

        new_balance = balance_float - total
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, user_id))

        cursor.execute("DELETE FROM cart_items WHERE cart_id = (SELECT id FROM carts WHERE user_id = %s)", (user_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Purchase successful', 'new_balance': new_balance}), 200
    except Exception as e:
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        return jsonify({'error': f'Failed to purchase: {str(e)}'}), 500