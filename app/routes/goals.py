from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Goal, Category

goals_bp = Blueprint('goals_api', __name__, url_prefix='/api/goals')


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


@goals_bp.route('', methods=['GET'])
@login_required
def get_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.order.asc(), Goal.created_at.desc()).all()
    goals_data = []
    for g in goals:
        goals_data.append({
            'id': g.id,
            'description': g.description,
            'category_id': g.category_id,
            'category_name': g.category.name if g.category else None,
            'completed': g.completed,
            'created_at': g.created_at.isoformat(),
            'due_date': g.due_date.isoformat() if g.due_date else None,
            'order': g.order,
        })
    return jsonify(goals_data)


@goals_bp.route('', methods=['POST'])
@login_required
def create_goal():
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({'error': 'Descripción requerida'}), 400

    description = data['description'].strip()
    category_id = data.get('category')
    due_date = parse_date(data.get('due_date'))

    category = None
    if category_id:
        category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        category = Category.query.filter_by(user_id=current_user.id).first()

    last_order = db.session.query(db.func.max(Goal.order)).filter_by(user_id=current_user.id).scalar() or 0
    new_goal = Goal(
        description=description,
        category_id=category.id if category else None,
        user_id=current_user.id,
        completed=False,
        created_at=datetime.utcnow(),
        due_date=due_date,
        order=last_order + 1
    )

    db.session.add(new_goal)
    db.session.commit()

    return jsonify({
        'id': new_goal.id,
        'description': new_goal.description,
        'category_id': new_goal.category_id,
        'category_name': new_goal.category.name if new_goal.category else None,
        'completed': new_goal.completed,
        'created_at': new_goal.created_at.isoformat(),
        'due_date': new_goal.due_date.isoformat() if new_goal.due_date else None,
        'order': new_goal.order,
    }), 201





@goals_bp.route('/<int:goal_id>', methods=['PUT', 'PATCH'])
@login_required
def update_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        return jsonify({'error': 'Meta no encontrada'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos inválidos'}), 400

    description = data.get('description')
    if description is not None:
        goal.description = description.strip()

    category_id = data.get('category')
    if category_id is not None:
        category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
        goal.category_id = category.id if category else None

    if 'completed' in data:
        goal.completed = bool(data['completed'])

    due_date_str = data.get('due_date')
    goal.due_date = parse_date(due_date_str)

    order = data.get('order')
    if order is not None:
        try:
            goal.order = int(order)
        except (TypeError, ValueError):
            pass

    db.session.commit()

    return jsonify({
        'id': goal.id,
        'description': goal.description,
        'category_id': goal.category_id,
        'category_name': goal.category.name if goal.category else None,
        'completed': goal.completed,
        'created_at': goal.created_at.isoformat(),
        'due_date': goal.due_date.isoformat() if goal.due_date else None,
        'order': goal.order,
    })


@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        return jsonify({'error': 'Meta no encontrada'}), 404

    # Comentado para evitar borrado de categoría vacía
    # category = goal.category

    db.session.delete(goal)
    db.session.commit()

    # No borrar categorías vacías, por eso eliminamos este bloque:
    # if category and category.name.lower() != 'general':
    #     restantes = Goal.query.filter_by(category_id=category.id, user_id=current_user.id).count()
    #     if restantes == 0:
    #         db.session.delete(category)
    #         db.session.commit()

    return jsonify({'message': 'Meta eliminada'}), 200


@goals_bp.route('/reorder', methods=['POST'])
@login_required
def reorder_goals():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Datos inválidos, se esperaba lista'}), 400
    for item in data:
        goal_id = item.get('id')
        order = item.get('order')
        if goal_id is None or order is None:
            continue
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        if goal:
            goal.order = order
    db.session.commit()
    return jsonify({'message': 'Orden actualizado'}), 200

