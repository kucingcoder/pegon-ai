from flask import jsonify
from flask_jwt_extended import get_jwt

def admin_only():
    def decorator(fn):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims["role"]
            if role != 'admin':
                return jsonify(
                    {
                        'code': 403,
                        'status': 'forbidden',
                        'message': 'admin only'
                    }
                ), 403
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator