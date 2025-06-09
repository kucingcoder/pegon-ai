from flask import Blueprint, request

payment_bp = Blueprint('payment', __name__)
@payment_bp.route('/notification', methods=['GET'])
def notif():
    data = request.get_json()
    print(data)
    return 200

@payment_bp.route('/error', methods=['GET'])
def error():
    data = request.get_json()
    print(data)
    return 200

@payment_bp.route('/finish', methods=['GET'])
def finish():
    data = request.get_json()
    print(data)
    return 'Hello world'