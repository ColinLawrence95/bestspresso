from flask import Flask
from dotenv import load_dotenv
from auth_blueprint import authentication_blueprint
from products_blueprint import products_blueprint
from cart_blueprint import cart_blueprint
from user_blueprint import user_blueprint


load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
  return "Hello, world!"

app.register_blueprint(authentication_blueprint, url_prefix="/auth")
app.register_blueprint(products_blueprint, url_prefix="/products")
app.register_blueprint(cart_blueprint, url_prefix="/cart")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.run()




