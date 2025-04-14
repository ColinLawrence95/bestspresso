from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from auth_blueprint import authentication_blueprint
from products_blueprint import products_blueprint
from cart_blueprint import cart_blueprint
from user_blueprint import user_blueprint


load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET') 
CORS(app, resources={
    r"/*": {
        "origins": ["https://bestpresso.netlify.app"],
        "supports_credentials": True,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.register_blueprint(authentication_blueprint, url_prefix="/auth")
app.register_blueprint(products_blueprint, url_prefix="/products")
app.register_blueprint(cart_blueprint, url_prefix="/cart")
app.register_blueprint(user_blueprint, url_prefix="/user")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)