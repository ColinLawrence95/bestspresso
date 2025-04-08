from flask import Blueprint, g, jsonify
from db_helpers import get_user_balance
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
        return jsonify({"Balance": float(balance)}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch balance: {str(e)}'}), 500
    

     
