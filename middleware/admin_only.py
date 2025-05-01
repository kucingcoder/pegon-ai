from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User

def admin_only():
    def decorator(fn):
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user = User.objects(id=current_user, role='admin').first()
            if not user:
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