from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

bcrypt = Bcrypt()
# IMPORTANT: In a real production app, this secret key should be stored securely
# and not hardcoded, e.g., in an environment variable.
SECRET_KEY = "your-super-secret-key-for-jwt"

def hash_password(password):
    """Hashes a password for storing."""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(password_hash, password):
    """Checks a password against a stored hash."""
    return bcrypt.check_password_hash(password_hash, password)

def create_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': str(user_id)   
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        # DEBUG (you can remove later)
        print("AUTH HEADER:", auth_header)

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'message': 'Authorization header missing or invalid'}), 401

        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user_id = int(data['sub'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            print("JWT ERROR:", str(e))
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated



