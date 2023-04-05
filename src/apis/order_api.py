import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import login_required

from src.apis.user_api import admin_permission
from src.models import Order

order_api_blueprint = Blueprint('order_api_blueprint', __name__)


@order_api_blueprint.route('/orders', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def get_orders():
    orders = Order.query.all()
    orders_dict = [order.to_dict() for order in orders]
    return jsonify(orders_dict)


@order_api_blueprint.route('/orders/<id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def get_order(id):
    order = Order.query.filter_by(id=id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(order.to_dict())


@order_api_blueprint.route('/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request data'}), 400

    orders = []
    for order_data in data:
        order_items = order_data.get('order_items')
        if not order_items:
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            order = Order.create(id=uuid.uuid4(), created_at=datetime.utcnow(), order_items=order_items)
            orders.append(order)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    return jsonify([order.to_dict() for order in orders]), 201


@order_api_blueprint.route('/orders/<id>', methods=['PUT'])
@login_required
@admin_permission.require(http_exception=403)
def update_order(id):
    order = Order.query.filter_by(id=id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request data'}), 400

    order_items = data.get('order_items')
    if not order_items:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        order.update(order_items)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(order.to_dict())


@order_api_blueprint.route('/orders/<id>', methods=['DELETE'])
@login_required
@admin_permission.require(http_exception=403)
def delete_order(id):
    order = Order.query.filter_by(id=id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    order.delete()
    return jsonify({'message': 'Order deleted successfully'})