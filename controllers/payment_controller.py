import os
import midtransclient
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request
from middleware.require_api_key import require_api_key
from models.payment import Payment
from models.user import User
from utils import log

MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY')
MIDTRANS_SERVER_TYPE = os.environ.get('MIDTRANS_SERVER_TYPE')

production = False

if MIDTRANS_SERVER_TYPE == 'production':
    production = False

snap = midtransclient.Snap(
    is_production = production,
    server_key = MIDTRANS_SERVER_KEY
)

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment', methods=['POST'])
@require_api_key()
@jwt_required()
def payment():    
    current_user = get_jwt_identity()
    user = User.objects(id=current_user).first()

    if not user:
        return jsonify({
            'code': 404,
            'status': 'not found',
            'message': 'user not found'
        }), 404

    payment = Payment(user_id=user.id, product='Pegon AI Pro 1 Bulan', price=15000)
    payment.save()

    param = {
        "transaction_details": {
            "order_id": str(payment.id),
            "gross_amount": 1000
        }, "credit_card":{
            "secure" : True
        },
        "item_details": [
            {
                "id": "1",
                "price": 1000,
                "quantity": 1,
                "name": "Pegon AI Pro 1 Bulan"
            }
        ]
    }

    try:
        transaction = snap.create_transaction(param)

        device = request.headers.get('Device') or 'Unknown'
        log(get_jwt_identity(), 'success create payment', device)

        return jsonify({
            'code': 201,
            'status': 'created',
            'message': 'transaction created',
            'data': {
                'payment_id': str(payment.id),
                'snap_token': str(transaction['token'])
            }
        }), 201
    except Exception as e:
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'can\'t create transaction'
        }), 400
    
@payment_bp.route('/payment-check', methods=['POST'])
@require_api_key()
@jwt_required()
def payment_check():
    data = request.get_json()
    if 'payment_id' not in data or data['payment_id'] == "":
            return jsonify({
                'code': 400,
                'status': 'bad request',
                'message': f'field payment_id can\'t be empty'
            }), 400
    
    payment_id = data['payment_id']
    payment = Payment.objects(id=payment_id).first()

    if not payment:
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'payment not found'
        }), 400

    return jsonify({
        'code': 200,
        'status': 'ok',
        'message': 'success check payment',
        'data': {
            'status': payment.status
        }
    }), 200

@payment_bp.route('/notification', methods=['POST'])
def notif():
    data = request.get_json()

    required_fields = ['transaction_status', 'order_id']
    for field in required_fields:
        if field not in data or data[field] == "":
            return jsonify(data), 200
        
    transaction_status = data['transaction_status']
    order_id = data['order_id']

    payment = Payment.objects(id=order_id).first()
    if not payment:
        return jsonify(data), 200
    
    user = User.objects(id=payment.user_id.id).first()
    if not user:
        return jsonify(data), 200

    if transaction_status == 'pending' or transaction_status == 'settlement':
        if transaction_status == 'settlement':
            user.category = 'pro'
            user.expired_at = datetime.now(timezone.utc).date() + timedelta(days=30)
        payment.status = transaction_status
    else:
        payment.status = 'cancel'

    user.save()
    payment.save()
    return jsonify(data), 200

@payment_bp.route('/error', methods=['POST'])
def error():
    data = request.get_json()
    return jsonify(data), 200

@payment_bp.route('/finish', methods=['GET'])
def finish():
    return 'Hello world'