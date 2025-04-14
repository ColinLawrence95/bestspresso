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
CORS(app) 


app.register_blueprint(authentication_blueprint, url_prefix="/auth")
app.register_blueprint(products_blueprint, url_prefix="/products")
app.register_blueprint(cart_blueprint, url_prefix="/cart")
app.register_blueprint(user_blueprint, url_prefix="/user")

if __name__ == '__main__':
    app.run()
