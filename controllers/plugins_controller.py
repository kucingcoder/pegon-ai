from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from middleware.require_api_key import require_api_key
from models.plugins_pair import PluginsPair
from models.user import User
from utils import log

plugins_bp = Blueprint('plugins', __name__)

@plugins_bp.route('/pair', methods=['GET'])
def pair():
    plugin = PluginsPair()
    plugin.save()

    return jsonify(
        {
            'code': 201,
            'status': 'created',
            'plugin_id': plugin.id
        }
    ), 201

@plugins_bp.route('/check', methods=['POST'])
def check():
    data = request.get_json()

    if 'plugin_id' not in data or data['plugin_id'] == "":
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': f'field plugin_id can\'t be empty'
            }
        ), 400
    
    plugin = PluginsPair.objects(id = data['plugin_id']).first()
    if not plugin:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'invalid plugin id'
            }
        ), 400
    
    if plugin.user_id == None or plugin.user_id == "":
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'plugin not paired'
            }
        ), 400
    
    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'plugin paired',
            'user_id': plugin.user_id
        }
    ), 200

@plugins_bp.route('/verify', methods=['POST'])
@require_api_key()
@jwt_required()
def payment():
    data = request.get_json()

    if 'plugin_id' not in data or data['plugin_id'] == "":
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': f'field plugin_id can\'t be empty'
            }
        ), 400
    
    user = User.objects(id = get_jwt_identity()).first()
    if not user:
        return jsonify(
            {
                'code': 404,
                'status': 'not found',
                'message': 'user not found'
            }
        ), 404
    
    plugin = PluginsPair.objects(id = data['plugin_id']).first()
    if not plugin:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'invalid plugin id'
            }
        ), 400
    
    plugin.user_id = user.id
    plugin.save()
    
    token = create_access_token(identity=str(user.id))

    device = request.headers.get('Device') or 'Unknown'
    log(user.id, 'plugin pair success', device)
    
    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'plugin pair success',
            'api_key': user.api_key,
            'access_token': token
        }
    ), 200