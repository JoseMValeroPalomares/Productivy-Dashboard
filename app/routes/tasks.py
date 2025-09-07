from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Task, Subtask
from flask_login import current_user, login_required
from datetime import datetime, date

tasks_api = Blueprint('tasks_api', __name__)
tasks_page = Blueprint('tasks_page', __name__)

# ---------------------------
# SERIALIZADORES
# ---------------------------
def serialize_subtask(subtask):
    return {
        'id': subtask.id,
        'text': subtask.text,      # 👈 mismo nombre que frontend espera
        'done': subtask.done       # 👈 mismo nombre que frontend espera
    }

def serialize_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'start': task.start.strftime('%Y-%m-%d'),
        'end': task.end.strftime('%Y-%m-%d') if task.end else None,
        'priority': task.priority,
        'tag': task.tag,
        'tagColor': task.tag_color,               # 👈 mapear tag_color → tagColor
        'completed': task.completed,
        'rruleText': task.rrule_text,             # 👈 mapear rrule_text → rruleText
        'subtasks': [serialize_subtask(st) for st in task.subtasks_rel.all()]
    }

# ---------------------------
# RUTA HTML
# ---------------------------
@tasks_page.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks_view():
    if request.method == 'POST':
        title = request.form.get('title')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')
        tag = request.form.get('tag')

        if not title:
            return redirect(url_for('tasks_page.tasks_view'))

        new_task = Task(
            title=title,
            start=date.fromisoformat(due_date) if due_date else date.today(),
            priority=int(priority) if priority else 2,
            tag=tag if tag else None,
            completed=False,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks_page.tasks_view'))

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks)

# ---------------------------
# API - LISTAR EVENTOS
# ---------------------------
@tasks_api.route('/api/events', methods=['GET'])
@login_required
def get_events():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    query = Task.query.filter_by(user_id=current_user.id)

    if start_str and end_str:
        try:
            start = datetime.fromisoformat(start_str.replace('Z', '')).date()
            end = datetime.fromisoformat(end_str.replace('Z', '')).date()
            query = query.filter(Task.start >= start, Task.start <= end)
        except Exception:
            return jsonify({"error": "Formato de fecha inválido"}), 400

    tasks = query.all()
    return jsonify([serialize_task(task) for task in tasks])

# ---------------------------
# API - CREAR EVENTO
# ---------------------------
@tasks_api.route('/api/events', methods=['POST'])
@login_required
def create_event():
    data = request.get_json() or {}

    # --- Validaciones básicas ---
    title = data.get('title')
    start_str = data.get('start')
    end_str = data.get('end')

    if not title:
        return jsonify({"error": "El título es obligatorio"}), 400
    if not start_str:
        return jsonify({"error": "La fecha de inicio es obligatoria"}), 400

    try:
        start = datetime.strptime(start_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Formato de fecha de inicio inválido"}), 400

    end = None
    if end_str:
        try:
            end = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Formato de fecha de fin inválido"}), 400

    if end and end < start:
        return jsonify({"error": "La fecha de fin no puede ser anterior a la de inicio"}), 400

    # --- Crear la tarea ---
    task = Task(
        title=title,
        start=start,
        end=end,
        priority=int(data.get('priority', 2)),
        tag=data.get('tag'),
        tag_color=data.get('tagColor'),        # 💡 nuevo: color etiqueta
        completed=bool(data.get('completed', False)),
        rrule_text=data.get('rruleText'),      # 💡 nuevo: recurrencia
        user_id=current_user.id
    )

    db.session.add(task)
    db.session.commit()  # commit para que tenga ID

    # --- Crear subtareas si vienen en el payload ---
    if 'subtasks' in data and isinstance(data['subtasks'], list):
        for st in data['subtasks']:
            new_st = Subtask(
                task_id=task.id,
                text=st.get('text', ''),
                done=st.get('done', False)
            )
            db.session.add(new_st)
        db.session.commit()

    return jsonify(serialize_task(task)), 201


# ---------------------------
# API - ACTUALIZAR EVENTO (también completa/incompleta)
# ---------------------------
@tasks_api.route('/api/events/<int:event_id>', methods=['PUT'])
@login_required
def edit_event(event_id):
    data = request.get_json() or {}
    task = Task.query.get_or_404(event_id)

    # Seguridad: solo el dueño puede editar
    if task.user_id != current_user.id:
        return jsonify({"error": "No autorizado"}), 403

    # ----- Campos básicos -----
    if 'title' in data:
        task.title = data['title']

    if 'start' in data:
        start_str = data.get('start')
        if start_str:
            try:
                task.start = datetime.strptime(start_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Formato de fecha de inicio inválido"}), 400
        else:
            task.start = None

    if 'end' in data:
        end_str = data.get('end')
        if end_str:
            try:
                task.end = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Formato de fecha de fin inválido"}), 400
        else:
            task.end = None

    if task.start and task.end and task.end < task.start:
        return jsonify({"error": "La fecha de fin no puede ser anterior a la de inicio"}), 400

    if 'priority' in data:
        task.priority = int(data['priority'])

    if 'tag' in data:
        task.tag = data['tag']

    if 'tagColor' in data:
        task.tag_color = data['tagColor']

    if 'completed' in data:
        task.completed = bool(data['completed'])

    if 'rruleText' in data:  # 💡 nombre igual que en frontend
        task.rrule_text = data['rruleText']

    # ----- Subtareas -----
    if 'subtasks' in data and isinstance(data['subtasks'], list):
        current_subtasks = {st.id: st for st in task.subtasks_rel.all()}
        handled_ids = set()

        for st_data in data['subtasks']:
            st_id = st_data.get('id')
            st_text = st_data.get('text', '')
            st_done = st_data.get('done', False)

            if st_id and st_id in current_subtasks:
                # Editar subtarea existente
                sub = current_subtasks[st_id]
                sub.text = st_text
                sub.done = st_done
                handled_ids.add(st_id)
            else:
                # Crear subtarea nueva
                new_st = Subtask(
                    task_id=task.id,
                    text=st_text,
                    done=st_done
                )
                db.session.add(new_st)

        # Eliminar las subtareas que ya no vienen
        for st_id, st in current_subtasks.items():
            if st_id not in handled_ids:
                db.session.delete(st)

    db.session.commit()
    return jsonify(serialize_task(task)), 200

# ---------------------------
# API - ELIMINAR EVENTO
# ---------------------------
@tasks_api.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    task = Task.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True, 'id': event_id})

# ---------------------------
# API - SUBTAREAS
# ---------------------------
@tasks_api.route('/api/events/<int:task_id>/subtasks', methods=['POST'])
@login_required
def create_subtask(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    title = data.get('title')
    if not title:
        return jsonify({"error": "El título es obligatorio"}), 400

    subtask = Subtask(text=title, done=False, task_id=task.id)
    db.session.add(subtask)
    db.session.commit()
    return jsonify(serialize_task(task)), 201

@tasks_api.route('/api/subtasks/<int:subtask_id>', methods=['PUT'])
@login_required
def update_subtask(subtask_id):
    subtask = Subtask.query.join(Task).filter(
        Subtask.id == subtask_id,
        Task.user_id == current_user.id
    ).first_or_404()
    data = request.get_json()

    if 'title' in data:
        subtask.text = data['title']
    if 'completed' in data:
        subtask.done = bool(data['completed'])

    db.session.commit()
    return jsonify(serialize_task(subtask.task))

@tasks_api.route('/api/subtasks/<int:subtask_id>', methods=['DELETE'])
@login_required
def delete_subtask(subtask_id):
    subtask = Subtask.query.join(Task).filter(
        Subtask.id == subtask_id,
        Task.user_id == current_user.id
    ).first_or_404()
    task = subtask.task
    db.session.delete(subtask)
    db.session.commit()
    return jsonify(serialize_task(task))


# API - COMPLETAR / DESCOMPLETAR EVENTO
@tasks_api.route('/api/events/<int:event_id>/complete', methods=['PUT'])
@login_required
def complete_event(event_id):
    task = Task.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()

    # Alterna el estado de completado
    task.completed = not task.completed
    db.session.commit()

    return jsonify(serialize_task(task)), 200
