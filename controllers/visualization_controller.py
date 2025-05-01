from flask_jwt_extended import jwt_required
from flask import Blueprint, request, jsonify
from middleware.require_api_key import require_api_key
from middleware.admin_only import admin_only
from models.statistik_satuan_pendidikan import StatistikSatuanPendidikan

visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/', methods=['GET'])
@require_api_key()
@jwt_required()
@admin_only()
def get_visualization():
    latest_data = StatistikSatuanPendidikan.objects.order_by('-year').first()

    data_dict = latest_data.to_mongo().to_dict()
    data_dict.pop('_id', None)
    data_dict.pop('created_at', None)
    data_dict.pop('updated_at', None)
    data_dict.pop('year', None)
    data_dict.pop('total', None)

    top_5 = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    top_5_data = [{'name': k, 'value': v} for k, v in top_5]

    total = sum(data_dict.values())
    pie_data = [{'name': k, 'value': round((v / total) * 360, 2)} for k, v in data_dict.items()]

    table_data = [{'name': k, 'value': v} for k, v in data_dict.items()]

    return jsonify(
        {
            'code': 200,
            'status': 'success',
            'message': 'Data retrieved successfully',
            'data': {
                'top_5': top_5_data,
                'pie': pie_data,
                'table': table_data,
                'year': latest_data.year
            }
        }
    ), 200