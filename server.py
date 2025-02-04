import psycopg2
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug: print loaded environment variables
print("POSTGRES_HOST:", os.getenv('POSTGRES_HOST'))
print("POSTGRES_USER:", os.getenv('POSTGRES_USER'))
print("POSTGRES_PASSWORD:", os.getenv('POSTGRES_PASSWORD'))
print("POSTGRES_DB:", os.getenv('POSTGRES_DB'))
print("POSTGRES_PORT:", os.getenv('POSTGRES_PORT'))

# Create Flask app instance
app = Flask(__name__, static_folder='ui')

# PostgreSQL Config (using environment variables)
app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER')
app.config['POSTGRES_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')
app.config['POSTGRES_DB'] = os.getenv('POSTGRES_DB')
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT', 5432)

# Secret key for sessions
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Create PostgreSQL connection function
def get_postgres_connection():
    try:
        return psycopg2.connect(
            host=app.config['POSTGRES_HOST'],
            user=app.config['POSTGRES_USER'],
            password=app.config['POSTGRES_PASSWORD'],
            database=app.config['POSTGRES_DB'],
            port=app.config['POSTGRES_PORT']
        )
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

# Password strength validation
def validate_password_strength(password):
    if len(password) < 8:
        return "Password should be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return "Password should contain at least one letter"
    if not re.search(r'\d', password):
        return "Password should contain at least one digit"
    return None

# Routes for user signup
@app.route('/signup', methods=['POST'])
def signup():
    cursor = None
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        email = data.get('email')

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match!'}), 400
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'error': 'Invalid email format!'}), 400

        password_error = validate_password_strength(password)
        if password_error:
            return jsonify({'error': password_error}), 400

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({'error': 'Username or Email already exists!'}), 409

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                       (username, hashed_password, email))
        conn.commit()
        return jsonify({'message': 'Signup successful!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Routes for login
@app.route('/login', methods=['POST'])
def login():
    cursor = None
    conn = None
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return jsonify({'message': 'Login successful!'}), 200
        else:
            return jsonify({'error': 'Invalid credentials!'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Run the application
if __name__ == "__main__":
    print("Starting Python Flask Server For Grocery Store Management System")
    app.run(port=5000, debug=True)
