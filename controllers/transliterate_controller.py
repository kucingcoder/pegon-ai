import hashlib
import os
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import Blueprint, request, jsonify, send_from_directory
from middleware.require_api_key import require_api_key
from datetime import date, datetime, timezone
from models.free_usage import FreeUsage
from models.user import User
from utils import log, to_webp
from models.history import History

transliterate_bp = Blueprint('transliterate', __name__)

APP_URL = os.environ.get('APP_URL')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@transliterate_bp.route('/history', methods=['GET'])
@require_api_key()
@jwt_required()
def get_image_history():
    from flask import request

    current_user = get_jwt_identity()

    page = int(request.args.get('page', 1))
    if page < 1:
        return jsonify({
        'code': 400,
        'status': 'error',
        'message': 'Invalid page number'
    }), 400
        

    limit = 10
    skip = (page - 1) * limit

    total_transliterate = History.objects(user_id=current_user).count()
    history = (
        History.objects(user_id=current_user)
        .order_by('-created_at')
        .skip(skip)
        .limit(limit)
    )

    data = []
    for item in history:
        doc = item.to_mongo().to_dict()
        data.append({
            "id": str(doc.get("_id")),
            "image": APP_URL + "/api/transliterate/image/" + doc.get("image"),
            "date": item.updated_at.strftime("%d %b %Y") if item.updated_at else None,
        })

    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'history retrieved successfully',
        'data': data,
        'pagination': {
            'page': page,
            'limit': limit,
            'total_items': total_transliterate,
            'total_pages': (total_transliterate + limit - 1) // limit
        }
    }), 200

@transliterate_bp.route('/history/<id>', methods=['GET'])
@require_api_key()
@jwt_required()
def get_image_history_by_id(id):
    current_user = get_jwt_identity()
    history = History.objects(user_id=current_user, id=id).first()
    if not history:
        return jsonify({
            'code': 404,
            'status': 'not found',
            'message': 'history not found'
        }), 404

    doc = history.to_mongo().to_dict()
    data = {
        "id": str(doc.get("_id")),
        "image": APP_URL + "/api/transliterate/image/" + doc.get("image"),
        "text": doc.get("text"),
        "date": history.updated_at.strftime("%d %b %Y") if history.updated_at else None,
    }
    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'history retrieved successfully',
        'data': data
    }), 200

@transliterate_bp.route('/image/<filename>', methods=['GET'])
def get_thumbnail(filename):
    directory = os.path.abspath('storage/images/histories')
    return send_from_directory(directory, filename, mimetype='image/webp')

@transliterate_bp.route('/history/<id>', methods=['DELETE'])
@require_api_key()
@jwt_required()
def delete_image_history_by_id(id):
    current_user = get_jwt_identity()
    history = History.objects(user_id=current_user, id=id).first()
    if not history:
        return jsonify({
            'code': 404,
            'status': 'not found',
            'message': 'history not found'
        }), 404

    history.delete()
    if os.path.exists(os.path.join('storage/images/histories', history.image)):
        os.remove(os.path.join('storage/images/histories', history.image))

    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'history deleted successfully'
    }), 200

@transliterate_bp.route('/image-to-text', methods=['POST'])
@require_api_key()
@jwt_required()
def image_to_text():    
    if 'image' not in request.files or request.files['image'].filename == '':
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'field image can\'t be empty'
        }), 400
    
    file = request.files['image']
    
    if not allowed_file(file.filename):
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'image must be an image (png, jpg, jpeg)'
        }), 400
    
    ext = file.filename.rsplit('.', 1)[1].lower()

    user = User.objects(id=get_jwt_identity()).first()
    print(user)
    if user.category != 'pro':
        usage = FreeUsage(user_id=user)
        usage.save()

    today = date.today()
    usage_count = FreeUsage.objects(user_id=user.id, created_at=today).count()

    print(usage_count)

    if usage_count > 3:
        return jsonify({
            'code': 403,
            'status': 'forbidden',
            'message': 'free usage limit reached'
        }), 403


    now_str = str(datetime.now())
    md5_hash = hashlib.md5(now_str.encode()).hexdigest()
    input_filename = f'temp-{md5_hash}.{ext}'
    input_path = os.path.join('storage/images/histories', input_filename)

    file.save(input_path)

    # nanti lakukan image transliteration disini

    output_filename = f'{md5_hash}.webp'
    output_path = os.path.join('storage/images/histories', output_filename)

    to_webp(input_path, output_path)

    history = History(
        user_id=get_jwt_identity(),
        image=output_filename,
        text='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed felis dui, accumsan sit amet ornare aliquam, convallis at nunc. Suspendisse nibh elit, molestie ac mi et, ullamcorper sagittis elit. Maecenas et lacinia lectus. Aliquam sodales accumsan massa, nec sodales urna euismod quis. Pellentesque quis dolor id ex egestas porttitor tristique quis massa. Nam et quam congue, scelerisque urna ut, faucibus urna. Nam dignissim libero quis quam suscipit porta. Sed suscipit interdum ligula, at tempus metus condimentum non. Pellentesque dolor ex, varius quis nunc at, dapibus dictum turpis. Ut vehicula scelerisque quam, sed convallis elit. Duis ut venenatis augue, a auctor leo. Ut bibendum mi eu magna malesuada, sit amet interdum tortor accumsan.',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    history.save()

    device = request.headers.get('Device') or 'Unknown'
    log(get_jwt_identity(), 'success image transliteration', device)

    return jsonify(
        {
            'code': 201,
            'status': 'created',
            'message': 'transliteration done successfully',
            'data': {'id': str(history.id)}
        }
    ), 201

@transliterate_bp.route('/text-to-text', methods=['POST'])
@require_api_key()
@jwt_required()
def text_to_text():
    data = request.get_json()
    text = data.get('text')

    if not text or text == "":
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'field text can\'t be empty'
        }), 400
    
    # nanti lakukan text transliteration disini

    result = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque ultrices, sem at tristique dignissim, velit metus.'

    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'text transliteration done successfully',
        'data': {'text': result}
    }), 200