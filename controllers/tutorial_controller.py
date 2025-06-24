import os
from flask import Blueprint, jsonify, send_from_directory
from models.tutorial import Tutorial

tutorial_bp = Blueprint('tutorial', __name__)

APP_URL = os.environ.get('APP_URL')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@tutorial_bp.route('/list', methods=['GET'])
def get_tutorials():
    tutorials = Tutorial.objects()
    data = []
    for tutorial in tutorials:
        doc = tutorial.to_mongo().to_dict()
        data.append({
            "id": str(doc.get("_id")),
            "name": doc.get("name"),
            "thumbnail": APP_URL + "/api/tutorial/thumbnail/" + doc.get("thumbnail"),
            "date": tutorial.updated_at.strftime("%d %b %Y") if tutorial.updated_at else None,
        })
    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'tutorials retrieved successfully',
        'data': data
    }), 200

@tutorial_bp.route('/thumbnail/<filename>', methods=['GET'])
def get_thumbnail(filename):
    directory = os.path.abspath('storage/images/thumbnails')
    return send_from_directory(directory, filename, mimetype='image/webp')

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
        "thumbnail": APP_URL + "/api/tutorial/thumbnail/" + doc.get("thumbnail"),
        "date": tutorial.updated_at.strftime("%d %b %Y") if tutorial.updated_at else None,
    }
    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'tutorial retrieved successfully',
        'data': data
    }), 200