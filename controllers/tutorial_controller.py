import hashlib
import os
from flask_jwt_extended import jwt_required
from flask import Blueprint, request, jsonify
from middleware.require_api_key import require_api_key
from middleware.admin_only import admin_only
from models.tutorial import Tutorial
from datetime import datetime, timezone
from utils import to_webp

tutorial_bp = Blueprint('tutorial', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@tutorial_bp.route('/list', methods=['GET'])
def get_tutorials():
    tutorials = Tutorial.objects()
    data = []
    for tutorial in tutorials:
        doc = tutorial.to_mongo().to_dict()
        data.append({
            "id": str(doc.get("_id")),
            "name": doc.get("name"),
            "thumbnail": doc.get("thumbnail"),
            "date": tutorial.updated_at.strftime("%d %b %Y") if tutorial.updated_at else None,
        })
    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'tutorials retrieved successfully',
        'data': data
    }), 200

@tutorial_bp.route('/detail/<id>', methods=['GET'])
def get_tutorial(id):
    tutorial = Tutorial.objects(id=id).first()
    if not tutorial:
        return jsonify({
            'code': 404,
            'status': 'not found',
            'message': 'tutorial not found'
        }), 404

    doc = tutorial.to_mongo().to_dict()
    data = {
        "id": str(doc.get("_id")),
        "name": doc.get("name"),
        "description": doc.get("description"),
        "link": doc.get("link"),
        "thumbnail": doc.get("thumbnail"),
        "date": tutorial.updated_at.strftime("%d %b %Y") if tutorial.updated_at else None,
    }
    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'tutorial retrieved successfully',
        'data': data
    }), 200

@tutorial_bp.route('/create', methods=['POST'])
@require_api_key()
@jwt_required()
@admin_only()
def create_tutorial():
    required_fields = ['name', 'description', 'link']
    data = request.form

    for field in required_fields:
        if field not in data or data[field].strip() == '':
            return jsonify({
                'code': 400,
                'status': 'bad request',
                'message': f'field {field} can\'t be empty'
            }), 400
        
    name = data['name'].title()
    description = data['description']
    link = data['link']

    if Tutorial.objects(name=name).first():
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'name already exists'
            }
        ), 400

    if len(name) > 64:
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'name too long'
        }), 400
        
    if 'thumbnail' not in request.files or request.files['thumbnail'].filename == '':
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'field thumbnail can\'t be empty'
        }), 400
    
    file = request.files['thumbnail']
    
    if not allowed_file(file.filename):
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'thumbnail must be an image (png, jpg, jpeg)'
        }), 400
    
    ext = file.filename.rsplit('.', 1)[1].lower()

    now_str = str(datetime.now())
    md5_hash = hashlib.md5(now_str.encode()).hexdigest()
    input_filename = f'temp-{md5_hash}.{ext}'
    input_path = os.path.join('storage/images/thumbnails', input_filename)

    file.save(input_path)

    output_filename = f'{md5_hash}.webp'
    output_path = os.path.join('storage/images/thumbnails', output_filename)

    to_webp(input_path, output_path)

    tutorial = Tutorial(
        name=name,
        description=description,
        link=link,
        thumbnail=output_filename,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    tutorial.save()

    return jsonify(
        {
            'code': 201,
            'status': 'created',
            'message': 'tutorial created successfully',
        }
    ), 201

@tutorial_bp.route('/edit/<id>', methods=['PUT'])
@require_api_key()
@jwt_required()
@admin_only()
def edit_tutorial(id):
    tutorial = Tutorial.objects(id=id).first()
    if not tutorial:
        return jsonify(
            {
                'code': 404,
                'status': 'not found',
                'message': 'tutorial not found'
            }
        ), 404

    required_fields = ['name', 'description', 'link']
    data = request.form

    for field in required_fields:
        if field not in data or data[field].strip() == '':
            return jsonify({
                'code': 400,
                'status': 'bad request',
                'message': f'field {field} can\'t be empty'
            }), 400
        
    name = data['name'].title()
    description = data['description']
    link = data['link']

    if Tutorial.objects(name=name, id__ne=id).first():
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'name already exists'
            }
        ), 400

    if len(name) > 64:
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'name too long'
        }), 400
        
    if 'thumbnail' not in request.files or request.files['thumbnail'].filename == '':
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'field thumbnail can\'t be empty'
        }), 400
    
    file = request.files['thumbnail']
    
    if not allowed_file(file.filename):
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'thumbnail must be an image (png, jpg, jpeg)'
        }), 400
        
    ext = file.filename.rsplit('.', 1)[1].lower()

    now_str = str(datetime.now())
    md5_hash = hashlib.md5(now_str.encode()).hexdigest()
    input_filename = f'temp-{md5_hash}.{ext}'
    input_path = os.path.join('storage/images/thumbnails', input_filename)

    file.save(input_path)

    output_filename = f'{md5_hash}.webp'
    output_path = os.path.join('storage/images/thumbnails', output_filename)

    to_webp(input_path, output_path)

    old_thumbnail = os.path.join('storage/images/thumbnails', tutorial.thumbnail)
    if os.path.exists(old_thumbnail):
        os.remove(old_thumbnail)

    tutorial.update(set__name=name, set__description=description, set__link=link, set__thumbnail=output_filename)
    tutorial.save()

    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'tutorial updated successfully',
        }
    ), 200

@tutorial_bp.route('/delete/<id>', methods=['DELETE'])
@require_api_key()
@jwt_required()
@admin_only()
def delete_tutorial(id):
    tutorial = Tutorial.objects(id=id).first()
    if not tutorial:
        return jsonify(
            {
                'code': 404,
                'status': 'not found',
                'message': 'tutorial not found'
            }
        ), 404

    thumbnail = os.path.join('storage/images/thumbnails', tutorial.thumbnail)
    if os.path.exists(thumbnail):
        os.remove(thumbnail)

    tutorial.delete()

    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'tutorial deleted successfully',
        }
    ), 200