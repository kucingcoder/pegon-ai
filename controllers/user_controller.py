import secrets
import random
import threading
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token
from flask import Blueprint, request, jsonify
from middleware.require_api_key import require_api_key
from models.user import User
from models.otp import Otp
from datetime import datetime, timezone
from utils import send_wa

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

@user_bp.route('/login-with-google', methods=['POST'])
def login_with_google():
    data = request.get_json()

    required_fields = ['name', 'email', 'google_id']
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
    email = data['email']
    google_id = data['google_id']

    user = User.objects(google_id=google_id).first()

    if not user:
        user = User(
            name = name,
            email = email,
            google_id = google_id,
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

    return jsonify(
            {
                'code': 200,
                'status': '0k',
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
    
    data = {}

    if user.google_id != None:
        data = {
            'email': user.email,
            'name': user.name,
            'sex': user.sex,
            'date_of_birth': user.date_of_birth.strftime("%Y-%m-%d") if user.date_of_birth else None
        }
    else:
        data = {
            'phone_code': user.phone_code,
            'phone_number': user.phone_number,
            'name': user.name,
            'sex': user.sex,
            'date_of_birth': user.date_of_birth.strftime("%Y-%m-%d") if user.date_of_birth else None,
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

    user.update(set__name=name, set__sex=sex, set__date_of_birth=date_of_birth)
    user.save()

    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'profile updated successfully'
        }
    ), 200