import os
import midtransclient
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request
from middleware.require_api_key import require_api_key
from bson import ObjectId
from models.payment import Payment
from models.user import User
from utils import log

MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY')
MIDTRANS_SERVER_TYPE = os.environ.get('MIDTRANS_SERVER_TYPE')

production = False

if MIDTRANS_SERVER_TYPE == 'production':
    production = True

snap = midtransclient.Snap(
    is_production = production,
    server_key = MIDTRANS_SERVER_KEY
)

print(f'Payment Settings {MIDTRANS_SERVER_TYPE}')

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

    if user.category == 'pro':
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'user already pro'
        }), 400

    new_id = str(ObjectId())

    device = request.headers.get('Device') or 'Unknown'

    param = {
        "transaction_details": {
            "order_id": str(new_id),
            "gross_amount": 19000
        },
        "item_details": [
            {
                "id": "1",
                "price": 17000,
                "quantity": 1,
                "name": "Pegon AI Pro 1 Month"
            },
            {
                "id": "2",
                "price": 2000,
                "quantity": 1,
                "name": "Admin Fee"
            },
        ],
        "metadata": {
            "device": device,
            "user": str(user.id)
        }
    }

    try:
        transaction = snap.create_transaction(param)

        return jsonify({
            'code': 201,
            'status': 'created',
            'message': 'transaction created',
            'data': {
                'snap_token': str(transaction['token'])
            }
        }), 201
    except Exception as e:
        return jsonify({
            'code': 400,
            'status': 'bad request',
            'message': 'can\'t create transaction'
        }), 400
    
@payment_bp.route('/history', methods=['GET'])
@require_api_key()
@jwt_required()
def history():
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

        payments_query = Payment.objects(user_id=user.id).order_by('-updated_at')
        total = payments_query.count()
        payments = payments_query.skip(skip).limit(limit)

        data = []
        for item in payments:
            doc = item.to_mongo().to_dict()
            data.append({
                "product": doc.get("product"),
                "price": "Rp. " + "{:,}".format(int(doc.get("price") or 0)).replace(",", "."),
                "status": doc.get("status"),
                "updated_at": item.updated_at.strftime("%d %b %Y") if item.updated_at else None,
            })

        return jsonify({
            'code': 200,
            'status': 'ok',
            'message': 'payments retrieved successfully',
            'data': data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200

    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Internal server error',
        }), 500

# KUHUSUS UNTUK MIDTRANS (WEBHOOK)
@payment_bp.route('/notification', methods=['POST'])
def notif():
    data = request.get_json()
        
    transaction_status = data['transaction_status']
    order_id = data['order_id']
    user_id = data['metadata']['user']
    device = data['metadata']['device']

    payment = Payment.objects(id=order_id).first()
    if not payment:
        if transaction_status == 'pending':
            payment = Payment(
                id = order_id,
                product = 'Pegon AI Pro 1 Month',
                price = 19000,
                status = transaction_status,
                user_id = user_id
            )
            payment.save()
            log(user.id, 'create payment for upgrade to pro', device)
            
        return jsonify(data), 200

    
    user = User.objects(id=payment.user_id.id).first()
    if not user:
        return jsonify(data), 200

    if transaction_status == 'pending' or transaction_status == 'settlement':
        if transaction_status == 'settlement':
            user.category = 'pro'
            user.expired_at = datetime.now(timezone.utc).date() + timedelta(days=30)
            log(user.id, 'account upgraded to pro', 'System')
        payment.status = transaction_status
    else:
        log(user.id, 'cancel payment for upgrade to pro', 'System')
        payment.status = 'cancel'

    user.save()
    payment.save()
    return jsonify(data), 200

# KUHUSUS UNTUK MIDTRANS (WEBHOOK)
@payment_bp.route('/error', methods=['POST'])
def error():
    data = request.get_json()
    return jsonify(data), 200

# KUHUSUS UNTUK MIDTRANS (HALAMAN SETELAH BERHASIL MEMBAYAR)
@payment_bp.route('/finish', methods=['GET'])
def finish():
    return 'arigatou'