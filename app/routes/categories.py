from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Category, Goal

categories_bp = Blueprint('categories_api', __name__, url_prefix='/api/categories')

@categories_bp.route('', methods=['GET'])
@login_required
def get_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    data = [{'id': c.id, 'name': c.name} for c in categories]
    return jsonify(data)

@categories_bp.route('', methods=['POST'])
@login_required
def create_category():
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Nombre de categoría requerido'}), 400

    existing = Category.query.filter_by(user_id=current_user.id, name=name).first()
    if existing:
        return jsonify({'error': 'Categoría ya existe'}), 409

    new_cat = Category(name=name, user_id=current_user.id)
    db.session.add(new_cat)
    db.session.commit()
    return jsonify({'id': new_cat.id, 'name': new_cat.name}), 201

@categories_bp.route('/<int:category_id>', methods=['PUT', 'PATCH'])
@login_required
def update_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404

    data = request.get_json()
    name = data.get('name')
    if not name or not name.strip():
        return jsonify({'error': 'Nombre no válido'}), 400
    category.name = name.strip()
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name})

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404

    goals_count = Goal.query.filter_by(category_id=category.id, user_id=current_user.id).count()
    if goals_count > 0:
        return jsonify({'error': 'La categoría no está vacía'}), 400

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Categoría eliminada'}), 200
