from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from middleware.require_api_key import require_api_key
from models.plugins_pair import PluginsPair
from models.user import User
from utils import log

plugins_bp = Blueprint('plugins', __name__)

@plugins_bp.route('/word', methods=['GET'])
def word():
    return render_template('word.html')

@plugins_bp.route('/word-login', methods=['GET'])
def word_login():
    return render_template('word-login.html')

@plugins_bp.route('/list', methods=['GET'])
@require_api_key()
@jwt_required()
def list():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()
    
    if not user:
        return jsonify(
            {
                'code': 404,
                'status': 'not found',
                'message': 'user not found'
            }
        ), 404
    
    plugins = PluginsPair.objects(user_id=user.id)
    
    if not plugins:
        return jsonify(
            {
                'code': 200,
                'status': 'ok',
                'message': 'no paired plugins',
                'data' : []
            }
        ), 200
    
    plugin_list = []
    for plugin in plugins:
        plugin_list.append({
            'id': str(plugin.id),
            'device': plugin.device,
        })
    
    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'paired plugins list',
            'data': plugin_list
        }
    ), 200

@plugins_bp.route('/pair', methods=['POST'])
def pair():
    data = request.get_json()
    if 'device' not in data or data['device'] == "":
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': f'field device can\'t be empty'
            }
        ), 400
    
    plugin = PluginsPair(device=data['device'])
    plugin.save()

    return jsonify(
        {
            'code': 201,
            'status': 'created',
            'message': 'plugin created successfully',
            'plugin_id': str(plugin.id)
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
    
    user = User.objects(id = plugin.user_id.id).first()
    if not user:
        return jsonify(
            {
                'code': 404,
                'status': 'not found',
                'message': 'user not found'
            }
        ), 404
    
    token = create_access_token(identity=str(user.id))
    
    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'plugin paired',
            'api_key': user.api_key,
            'access_token': token
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
    
    if user.category != 'pro':
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'upgrade to pro to pair plugins'
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
    
    plugin.user_id = user.id
    plugin.save()

    log(user.id, 'successfully pair plugin', plugin.device)
    
    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'plugin pair success',
        }
    ), 200

@plugins_bp.route('/unpair', methods=['POST'])
@require_api_key()
@jwt_required()
def unpair():
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
    
    plugin = PluginsPair.objects(id = data['plugin_id'], user_id = user.id).first()
    if not plugin:
        return jsonify(
            {
                'code': 400,
                'status': 'bad request',
                'message': 'invalid plugin id'
            }
        ), 400
    
    plugin.delete()
    log(get_jwt_identity(), 'successfully unpair plugin', plugin.device)
    
    return jsonify(
        {
            'code': 200,
            'status': 'ok',
            'message': 'plugin unpaired successfully'
        }
    )