from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from app import db
from app.models import ScheduleTask, Template

schedule_bp = Blueprint('schedule', __name__, url_prefix='/api')

# --- Utilidades ---
def parse_date(date_str):
    """Convierte 'YYYY-MM-DD' a datetime.date."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None

# --- Rutas de tareas ---
@schedule_bp.route('/week')
@login_required
def get_week():
    start_str = request.args.get('start')
    start_date = parse_date(start_str)
    if not start_date:
        return jsonify({"error": "Fecha inválida"}), 400

    end_date = start_date + timedelta(days=6)

    tasks = ScheduleTask.query.filter(
        ScheduleTask.user_id == current_user.id,
        ScheduleTask.date <= end_date  # obtén al menos las tareas cuyo start date es ≤ fin semana
    ).all()

    tasks_list = []
    for t in tasks:
        # Si es recurrente y tiene fecha fin definida, crear instancias expandidas para la semana
        if t.recurrence != 'none' and t.end_date:
            current = max(t.date, start_date)
            final_date = min(t.end_date, end_date)
            while current <= final_date:
                matches = (
                    t.recurrence == 'daily' or
                    (t.recurrence == 'weekly' and current.weekday() == t.date.weekday()) or
                    (t.recurrence == 'monthly' and current.day == t.date.day)
                )
                if matches:
                    tasks_list.append({
                        "id": f"{t.id}-{current.strftime('%Y%m%d')}",  # id único por ocurrencia
                        "title": t.title,
                        "description": t.description,
                        "date": current.isoformat(),
                        "startHour": t.start_hour,
                        "duration": t.duration,
                        "completed": t.completed,
                        "inProgress": t.in_progress,
                        "color": t.color,
                        "recurrence": "none",  # ya no recurrente para cliente
                        "endDate": t.end_date.isoformat() if t.end_date else None
                    })
                current += timedelta(days=1)
        else:
            # tarea sin recurrencia: sólo la original
            if start_date <= t.date <= end_date:
                tasks_list.append({
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "date": t.date.isoformat(),
                    "startHour": t.start_hour,
                    "duration": t.duration,
                    "completed": t.completed,
                    "inProgress": t.in_progress,
                    "color": t.color,
                    "recurrence": t.recurrence,
                    "endDate": t.end_date.isoformat() if t.end_date else None
                })

    return jsonify({
        "start": start_date.isoformat(),
        "tasks": tasks_list
    })



@schedule_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    date = parse_date(data.get('date'))
    start_hour = data.get('startHour')
    duration = data.get('duration')
    title = (data.get('title') or '').strip()

    if not date:
        return jsonify({"error": "Fecha inválida"}), 400
    if start_hour is None or duration is None:
        return jsonify({"error": "Hora de inicio y duración requeridas"}), 400
    if not title:
        return jsonify({"error": "Título requerido"}), 400

    end_date = parse_date(data.get('endDate')) if data.get('endDate') else None

    task = ScheduleTask(
        user_id=current_user.id,
        title=title,
        description=data.get('description', ''),
        date=date,
        end_date=end_date,
        start_hour=float(start_hour),
        duration=float(duration),
        completed=bool(data.get('completed', False)),
        in_progress=bool(data.get('inProgress', False)),
        color=data.get('color'),
        recurrence=data.get('recurrence', 'none')
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "date": task.date.isoformat(),
        "endDate": task.end_date.isoformat() if task.end_date else None,
        "startHour": task.start_hour,
        "duration": task.duration,
        "completed": task.completed,
        "inProgress": task.in_progress,
        "color": task.color,
        "recurrence": task.recurrence
    })

from flask import request, jsonify

@schedule_bp.route('/tasks/<task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    # Detectar si es instancia recurrente expandida
    occ_date = None
    if '-' in task_id:
        base_id_str, date_str = task_id.split('-', 1)
        try:
            base_id = int(base_id_str)
        except ValueError:
            return jsonify({"error": "ID inválido"}), 400
        occ_date = parse_date(date_str)  # fecha de la ocurrencia
        if not occ_date:
            return jsonify({"error": "Fecha de instancia inválida"}), 400
    else:
        try:
            base_id = int(task_id)
        except ValueError:
            return jsonify({"error": "ID inválido"}), 400

    task = ScheduleTask.query.filter_by(id=base_id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    # Si quieres permitir mover solo esa ocurrencia:
    if occ_date:
        # Guardar como tarea independiente
        new_task = ScheduleTask(
            user_id=current_user.id,
            title=data.get('title', task.title),
            description=data.get('description', task.description),
            date=parse_date(data['date']) if 'date' in data else occ_date,
            start_hour=float(data.get('startHour', task.start_hour)),
            duration=float(data.get('duration', task.duration)),
            completed=bool(data.get('completed', False)),
            in_progress=bool(data.get('inProgress', False)),
            color=data.get('color', task.color),
            recurrence='none'
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"message": "Instancia creada", "id": new_task.id})

    # Si es tarea base, actualizar normal
    if 'title' in data: task.title = data['title'].strip()
    if 'description' in data: task.description = data['description']
    if 'date' in data:
        parsed_date = parse_date(data['date'])
        if not parsed_date:
            return jsonify({"error": "Fecha inválida"}), 400
        task.date = parsed_date
    if 'endDate' in data:
        task.end_date = parse_date(data['endDate']) if data['endDate'] else None
    if 'startHour' in data: task.start_hour = float(data['startHour'])
    if 'duration' in data: task.duration = float(data['duration'])
    if 'completed' in data: task.completed = bool(data['completed'])
    if 'inProgress' in data: task.in_progress = bool(data['inProgress'])
    if 'color' in data: task.color = data['color']
    if 'recurrence' in data: task.recurrence = data['recurrence']

    db.session.commit()
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "date": task.date.isoformat(),
        "endDate": task.end_date.isoformat() if task.end_date else None,
        "startHour": task.start_hour,
        "duration": task.duration,
        "completed": task.completed,
        "inProgress": task.in_progress,
        "color": task.color,
        "recurrence": task.recurrence
    })


@schedule_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = ScheduleTask.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({"deleted": True})

# --- Templates ---
@schedule_bp.route('/templates', methods=['GET'])
@login_required
def get_templates():
    templates = Template.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        "templates": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "duration": t.duration,
                "color": t.color,
                "recurrence": t.recurrence
            }
            for t in templates
        ]
    })

@schedule_bp.route('/templates', methods=['POST'])
@login_required
def create_template():
    data = request.get_json()
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({"error": "Título requerido"}), 400

    tpl = Template(
        user_id=current_user.id,
        title=title,
        description=data.get('description', ''),
        duration=float(data.get('duration', 1)),
        color=data.get('color'),
        recurrence=data.get('recurrence', 'none')
    )
    db.session.add(tpl)
    db.session.commit()
    return jsonify({
        "id": tpl.id,
        "title": tpl.title,
        "description": tpl.description,
        "duration": tpl.duration,
        "color": tpl.color,
        "recurrence": tpl.recurrence
    })

@schedule_bp.route('/templates/<int:tpl_id>', methods=['PUT'])
@login_required
def update_template(tpl_id):
    tpl = Template.query.filter_by(id=tpl_id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    if 'title' in data:
        tpl.title = data['title'].strip()
    if 'description' in data:
        tpl.description = data['description']
    if 'duration' in data:
        tpl.duration = float(data['duration'])
    if 'color' in data:
        tpl.color = data['color']
    if 'recurrence' in data:
        tpl.recurrence = data['recurrence']

    db.session.commit()
    return jsonify({
        "id": tpl.id,
        "title": tpl.title,
        "description": tpl.description,
        "duration": tpl.duration,
        "color": tpl.color,
        "recurrence": tpl.recurrence
    })

@schedule_bp.route('/templates/<int:tpl_id>', methods=['DELETE'])
@login_required
def delete_template(tpl_id):
    tpl = Template.query.filter_by(id=tpl_id, user_id=current_user.id).first_or_404()
    db.session.delete(tpl)
    db.session.commit()
    return jsonify({"deleted": True})