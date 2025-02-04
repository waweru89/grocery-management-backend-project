import psycopg2
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure all required environment variables are set
required_env_vars = ['POSTGRES_HOST', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_PORT', 'SECRET_KEY']
if not all(os.getenv(var) for var in required_env_vars):
    raise ValueError("One or more environment variables are missing.")

# Create Flask app instance
app = Flask(__name__, static_folder='ui', static_url_path='')

# Serve index.html for root URL
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# PostgreSQL connection function
def get_postgres_connection():
    try:
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            port=os.getenv('POSTGRES_PORT')
        )
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
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

# User signup route
@app.route('/signup', methods=['POST'])
def signup():
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
    
    try:
        with conn.cursor() as cursor:
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
        conn.close()

# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = get_postgres_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                return jsonify({'message': 'Login successful!'}), 200
            return jsonify({'error': 'Invalid credentials!'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Run the application
if __name__ == "__main__":
    print("Starting Python Flask Server For Grocery Store Management System")
    app.run(port=5000, debug=True)
