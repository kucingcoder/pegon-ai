import os
import secrets
import random
import threading
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token
from flask import Blueprint, request, jsonify
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from middleware.require_api_key import require_api_key
from models.log_activity import LogActivity
from models.user import User
from models.otp import Otp
from datetime import datetime, timezone
from utils import send_wa, log

GOOGLE_WEB_CLIENT_ID = os.environ.get('GOOGLE_WEB_CLIENT_ID')

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['name', 'sex', 'date_of_birth', 'phone_code', 'phone_number']
    for field in required_fields:
        if field not in data or data[field] == "":
            return jsonify(
                {
                    'code': 400,
                    'status': 'bad request',
                    'message': f'field {field} can\'t be empty'
                }
            ), 400


    if len(data['name']) > 64:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'name too long'
            }
        ), 400
    
    if len(data['phone_number']) > 16:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'whatsapp number too long'
            }
        ), 400

    name = data['name'].title()
    sex = data['sex']
    date_of_birth = data['date_of_birth']
    phone_code = data['phone_code']
    phone_number = data['phone_number']

    if User.objects(name=name).first():
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'name already exists'
            }
        ), 400

    if User.objects(phone_number=phone_number).first():
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'whatsapp number already exists'
            }
        ), 400

    user = User(
        name = name,
        sex = sex,
        date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d"),
        phone_code = phone_code,
        phone_number = phone_number,
        api_key = secrets.token_hex(32),
        created_at = datetime.now(timezone.utc),
        updated_at = datetime.now(timezone.utc)
    )
    user.save()

    otp = Otp.objects(user_id = user, status = 'active').first()

    if not otp:
        otp = Otp(
            user_id = user,
            code = str(random.randint(1000, 9999)),
            created_at = datetime.now(timezone.utc),
            updated_at = datetime.now(timezone.utc)
        )
        otp.save()

    threading.Thread(target=send_wa, args=(phone_number, otp.code)).start()

    device = request.headers.get('Device') or 'Unknown'
    log(user.id, 'successfully registered via whatsapp', device)

    return jsonify(
        {
            'code': 201,
            'status': 'created',
            'message': 'registered successfully, please verify your whatsapp number',
            'api_key': user.api_key
        }
    ), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number or phone_number == "":
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'whatsapp number cant be empty'
            }
        ), 400

    user = User.objects(phone_number=phone_number).first()

    if not user:
        return jsonify(
            {
                'code': 404,
                'status': 'not found',
                'message': 'whatsapp number not registered'
            }
        ), 404

    if user.status != 'active':
        return jsonify(
            {
                'code': 403,
                'status': 'forbidden',
                'message': 'user suspended'
            }
        ), 403
    
    otp = Otp.objects(user_id = user, status = 'active').first()

    if not otp:
        otp = Otp(
            user_id = user,
            code = str(random.randint(1000, 9999)),
            created_at = datetime.now(timezone.utc),
            updated_at = datetime.now(timezone.utc)
        )
        otp.save()

    threading.Thread(target=send_wa, args=(phone_number, otp.code)).start()

    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'login successfully, please verify your whatsapp number',
            'api_key': user.api_key
        }
    ), 200

@user_bp.route('/continue-with-google', methods=['POST'])
def continue_with_google():
    data = request.get_json()

    if 'token_id' not in data or data['token_id'] == '':
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': f'field token_id can\'t be empty'
            }
        ), 400

    token_id = data['token_id']

    try:
        idinfo = id_token.verify_oauth2_token(token_id, Request(), GOOGLE_WEB_CLIENT_ID)
    except Exception as e:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'invalid token'
            }
        ), 400

    email = idinfo.get('email')
    name = idinfo.get('name')

    user = User.objects(email=email).first()

    if not user:
        user = User(
            name = name,
            email = email,
            api_key = secrets.token_hex(32),
            created_at = datetime.now(timezone.utc),
            updated_at = datetime.now(timezone.utc)
        )
        user.save()

    if user.status != 'active':
        return jsonify(
            {
                'code': 403,
                'status': 'forbidden',
                'message': 'user suspended'
            }
        ), 403
    
    token = create_access_token(identity=str(user.id))

    device = request.headers.get('Device') or 'Unknown'
    log(user.id, 'successfully logged in via google', device)

    return jsonify(
            {
                'code': 200,
                'status': 'ok',
                'message': 'continue with google successfully',
                'api_key': user.api_key,
                'access_token': token
            }
        ), 200

@user_bp.route('/profile', methods=['GET'])
@require_api_key()
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = User.objects(id=current_user).first()

    if not user:
        return jsonify(
            {
                'code': 404,
                'status': 'not found',
                'message': 'user not found'
            }
        ), 404

    data = {
            'id': str(user.id),
            'name': user.name,
            'sex': user.sex,
            'date_of_birth': user.date_of_birth.strftime("%Y-%m-%d") if user.date_of_birth else None,
            'category': user.category,
            'expired': 'has no expiration date' if user.category == 'free' else user.expired_at.strftime("%d/%m/%Y")
        }

    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'data': data,
            'api_key': user.api_key
        }
    ), 200

@user_bp.route('/profile-update', methods=['POST'])
@require_api_key()
@jwt_required()
def profile_update():
    data = request.get_json()

    required_fields = ['name', 'sex', 'date_of_birth']
    for field in required_fields:
        if field not in data or data[field] == "":
            return jsonify(
                {
                    'code': 400,
                    'status': 'bad request',
                    'message': f'field {field} can\'t be empty'
                }
            ), 400


    if len(data['name']) > 64:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'name too long'
            }
        ), 400
    
    name = data['name'].title()
    sex = data['sex']
    date_of_birth = data['date_of_birth']
    
    current_user = get_jwt_identity()
    
    check_name = User.objects(name=data['name'].title(), id__ne=current_user).first()

    if check_name and check_name.id != current_user:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'name already exists'
            }
        ), 400
    
    user = User.objects(id=current_user).first()

    if not user:
        return jsonify(
            {
                'code': 404,
                'status': 'not found',
                'message': 'user not found'
            }
        ), 404

    user.name = name
    user.sex = sex
    user.date_of_birth = date_of_birth
    user.save()

    device = request.headers.get('Device') or 'Unknown'
    log(user.id, 'successfully updated profile', device)

    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'profile updated successfully'
        }
    ), 200

@user_bp.route('/activity', methods=['GET'])
@require_api_key()
@jwt_required()
def activity():
    current_user = get_jwt_identity()
    user = User.objects(id=current_user).first()

    if not user:
        return jsonify({
            'code': 404,
            'status': 'not found',
            'message': 'user not found'
        }), 404

    try:
        page = int(request.args.get('page', 1))
        limit = 10
        skip = (page - 1) * limit

        total_logs = LogActivity.objects(user_id=user.id).count()

        logs = LogActivity.objects(user_id=user.id).order_by('-timestamp').skip(skip).limit(limit)

        data = [{
            'activity': log.activity,
            'device': log.device,
            'timestamp': log.timestamp.strftime("%d/%m/%Y - %H:%M") if log.timestamp else None
        } for log in logs]

        return jsonify({
            'code': 200,
            'status': 'success',
            'data': data,
            'pagination': {
                'total': total_logs,
                'page': page,
                'limit': limit,
                'pages': (total_logs + limit - 1) // limit
            }
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'internal server error',
        }), 500