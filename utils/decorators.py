# utils/decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(*roles):
    """Decorator: chỉ cho phép các user có role trong roles."""
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            # Bắt buộc phải có token
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in roles:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return fn(*args, **kwargs)
        return decorated
    return wrapper
