from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required
from flask_principal import Permission, RoleNeed

from src.models import User
from src.validators.auth_validator import validate_login
from src.validators.user_validator import validate_user_data

user_api_blueprint = Blueprint('user_api_blueprint', __name__)

admin_permission = Permission(RoleNeed('administrator'))


@user_api_blueprint.route('/users', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def get_users():
    users = User.query.all()
    user_dicts = [user.to_dict() for user in users]
    return jsonify(user_dicts)


@user_api_blueprint.route('/users/<id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def get_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


@user_api_blueprint.route('/users', methods=['POST'])
@validate_user_data('POST')
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request data'}), 400

    existing_user = User.query.filter_by(username=data.get('username')).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    user = User.create(data.get('username'), data.get('password'), data.get('date_of_birth'))
    return jsonify(user.to_dict()), 201


@user_api_blueprint.route('/users/<id>', methods=['PUT'])
@login_required
@validate_user_data('PUT')
def update_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request data'}), 400

    user.update(data.get('username'), data.get('password'), data.get('date_of_birth'))
    return jsonify(user.to_dict()), 200


@user_api_blueprint.route('/users/<id>', methods=['DELETE'])
@login_required
@admin_permission.require(http_exception=403)
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    User.delete(user)
    return jsonify({'message': 'User deleted'}), 200


@user_api_blueprint.route('/login', methods=['POST'])
@validate_login
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    login_user(user)

    if user.role == 'administrator':
        session['admin'] = True

    return jsonify(user.to_dict()), 200


@user_api_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    if 'admin' in session:
        session.pop('admin')

    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200