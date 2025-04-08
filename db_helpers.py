import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USERNAME'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    return connection

def get_user_balance(user_id):
    """Fetch the user's balance from the users table"""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
    balance = cursor.fetchone()
    cursor.close()
    connection.close()
    return balance[0] if balance else 0.0