from flask import Blueprint, jsonify, request

payment_bp = Blueprint('payment', __name__)
@payment_bp.route('/notification', methods=['POST'])
def notif():
    data = request.get_json()
    print(data)
    return jsonify(data), 200

@payment_bp.route('/error', methods=['POST'])
def error():
    data = request.get_json()
    print(data)
    return jsonify(data), 200

@payment_bp.route('/finish', methods=['GET'])
def finish():
    return 'Hello world'