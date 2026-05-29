from flask import Blueprint, request, jsonify
import jwt
import datetime
from functools import wraps
from config import SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            return jsonify({"error": "Token invalid"}), 401
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = jwt.encode(
            {'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
            SECRET_KEY, algorithm='HS256'
        )
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401
