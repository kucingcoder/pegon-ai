from flask import jsonify, request
from models.user import User

def require_api_key():
    def decorator(fn):
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            user = User.objects(api_key=api_key).first()
            if not user:
                return jsonify(
                    {
                        'code': 403,
                        'status': 'forbidden',
                        'message': 'invalid api key'
                    }
                ), 403
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator