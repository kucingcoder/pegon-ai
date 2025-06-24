import random
import threading
from flask_jwt_extended import create_access_token
from flask import Blueprint, request, jsonify
from middleware.require_api_key import require_api_key
from models.user import User
from models.otp import Otp
from datetime import datetime, timezone
from utils import send_wa, log

otp_bp = Blueprint('otp', __name__)
@otp_bp.route('/resent', methods=['GET'])
@require_api_key()
def resend():
    api_key = request.headers.get('X-API-Key')
    user = User.objects(api_key=api_key).first()

    otp = Otp.objects(user_id = user, status = 'active').first()

    if not otp:
        otp = Otp(
            user_id = user,
            code = str(random.randint(1000, 9999)),
            status = 'active',
            created_at = datetime.now(timezone.utc),
            updated_at = datetime.now(timezone.utc)
        )
        otp.save()

    threading.Thread(target=send_wa, args=(user.phone_number, otp.code)).start()

    return jsonify(
            {
                'code': 200,
                'status': 'ok',
                'message': 'verification code resent successfully'
            }
        ), 200

@otp_bp.route('/verification', methods=['POST'])
@require_api_key()
def verification():
    data = request.get_json()

    code = data["code"]

    if not code or code == "":
            return jsonify(
                {
                    'code': 400,
                    'status': 'bad request',
                    'message': f'field code can\'t be empty'
                }
            ), 400
    
    api_key = request.headers.get('X-API-Key')
    user = User.objects(api_key=api_key).first()
    otp = Otp.objects(user_id = user, code = code, status = 'active').first()

    if not otp:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': f'invalid verification code'
            }
        ), 400
    
    otp.status = 'expired'
    otp.save()

    token = create_access_token(identity=str(user.id))

    device = request.headers.get('Device') or 'Unknown'
    log(user.id, 'successfully logged in via whatsapp', device)

    return jsonify(
            {
                'code': 200,
                'status': 'ok',
                'message': 'phone number verification successfully',
                'access_token': token
            }
        ), 200