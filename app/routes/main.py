from flask import Blueprint, render_template
from flask_login import login_required, current_user
from collections import defaultdict
from datetime import datetime

from sqlalchemy import and_
from app.models import Goal, Category, Task, Event  # ⬅️ Importar Event
from app.utils.tips import get_random_tip

from flask import request, jsonify, redirect, url_for, flash
import string, random
from app.models import PasswordEntry
from app import db
from flask import abort
from flask import request
from app.models import DiarioCategoria, DiarioSubcategoria, DiarioTema, DiarioApartado
from flask import make_response


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def home():
    resumen = (
        "Se mejoró el estilo general de la aplicación, incorporando animaciones suaves "
        "para una mejor experiencia de usuario."
        " Además, se crearon nuevas páginas funcionales para Herramientas y Juegos, ampliando la funcionalidad disponible."
    )

    cambios = [
        {'fecha': '2025-08-01', 'desc': 'Se añadió nueva sección de tareas'},
        {'fecha': '2025-08-02', 'desc': 'Mejoras de rendimiento implementadas'},
        {'fecha': '2025-08-04', 'desc': 'Finalizada la sección de metas con funcionalidades completas'},
        {'fecha': '2025-08-04', 'desc': 'Páginas de Herramientas y Juegos creadas y estilizadas con nuevas animaciones'},
        {'fecha': '2025-08-09', 'desc': 'Página de Tareas creada y estilizada con animaciones suaves'},
        {'fecha': '2025-08-10', 'desc': 'Asistente de notificaciones implementado para tareas y metas pendientes'}
    ]

    consejo = get_random_tip()

    # 📌 Tareas
    total_tareas = Task.query.filter_by(user_id=current_user.id).count()
    tareas_pendientes = Task.query.filter_by(user_id=current_user.id, completed=False).count()
    tareas_completadas = total_tareas - tareas_pendientes

    # 📌 Metas
    total_metas = Goal.query.filter_by(user_id=current_user.id).count()
    metas_alcanzadas = Goal.query.filter_by(user_id=current_user.id, completed=True).count()

    tareas_info = f"{tareas_completadas}/{total_tareas}" if total_tareas > 0 else "0/0"
    metas_info = f"{metas_alcanzadas}/{total_metas}" if total_metas > 0 else "0/0"

    # 📌 Próximos eventos
    proximos_eventos = Event.query.filter(
        Event.user_id == current_user.id,
        Event.start >= datetime.utcnow()
    ).count()

    # 📌 Mini-asistente de notificaciones
    notificaciones = []
    if tareas_pendientes > 0:
        notificaciones.append(f"Tienes {tareas_pendientes} tarea(s) pendiente(s).")
    if proximos_eventos > 0:
        notificaciones.append(f"Tienes {proximos_eventos} evento(s) próximamente.")
    if total_metas > 0 and metas_alcanzadas < total_metas:
        notificaciones.append(f"Has completado {metas_alcanzadas}/{total_metas} metas.")
    if not notificaciones:
        notificaciones.append("Todo al día. ¡Buen trabajo!")

    return render_template(
    'home.html',
    resumen=resumen,
    cambios=cambios,
    consejo=consejo,
    tareas_pendientes=tareas_pendientes,
    proximos_eventos=proximos_eventos,
    metas_alcanzadas=metas_alcanzadas,
    total_tareas=total_tareas,
    tareas_completadas=tareas_completadas,
    total_metas=total_metas,
    tareas_info=tareas_info,
    metas_info=metas_info
)



@main_bp.app_context_processor
def inject_notificaciones():
    from flask_login import current_user
    from datetime import datetime
    if not current_user.is_authenticated:
        return dict(notificaciones_asistente=[])
    
    tareas_pendientes = Task.query.filter_by(user_id=current_user.id, completed=False).count()
    proximos_eventos = Event.query.filter(Event.user_id == current_user.id, Event.start >= datetime.utcnow()).count()
    total_metas = Goal.query.filter_by(user_id=current_user.id).count()
    metas_alcanzadas = Goal.query.filter_by(user_id=current_user.id, completed=True).count()

    notificaciones = []
    if tareas_pendientes > 0:
        notificaciones.append(f"Tienes {tareas_pendientes} tarea(s) pendiente(s).")
    if proximos_eventos > 0:
        notificaciones.append(f"Tienes {proximos_eventos} evento(s) próximamente.")
    if total_metas > 0 and metas_alcanzadas < total_metas:
        notificaciones.append(f"Has completado {metas_alcanzadas}/{total_metas} metas.")
    if not notificaciones:
        notificaciones.append("Todo al día. ¡Buen trabajo!")

    return dict(notificaciones_asistente=notificaciones)

@main_bp.route('/tasks')
@login_required
def tasks():
    # Obtener todas las tareas del usuario
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()

    # Calcular estadísticas de tareas
    total_tasks = len(user_tasks)
    done_tasks = sum(1 for t in user_tasks if getattr(t, 'completed', False))
    percent_tasks = round((done_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0

    # Calcular estadísticas de metas
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    total_goals = len(user_goals)
    done_goals = sum(1 for g in user_goals if g.completed)
    percent_goals = round((done_goals / total_goals * 100), 2) if total_goals > 0 else 0

    # Reunir todas las etiquetas existentes
    all_tags = set()
    for t in user_tasks:
        if getattr(t, 'tag', None):
            all_tags.add(t.tag)

    # Diccionario de estadísticas para la plantilla
    stats = {
        'total_tasks': total_tasks,
        'done_tasks': done_tasks,
        'percent_tasks': percent_tasks,
        'total_goals': total_goals,
        'done_goals': done_goals,
        'percent_goals': percent_goals,
    }

    return render_template(
        'tasks.html',
        tasks=user_tasks,
        stats=stats,
        all_tags=sorted(all_tags)
    )


@main_bp.route('/schedule')
@login_required
def schedule():
    return render_template('schedule.html')

@main_bp.route('/schedule-movil')
def schedule_movil():
    return render_template('schedule-movil.html')


@main_bp.route('/goals')
@login_required
def goals():
    # Obtener todas las metas del usuario ordenadas
    user_goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.order.asc(), Goal.created_at.desc()).all()

    # Obtener todas las categorías del usuario
    categories = Category.query.filter_by(user_id=current_user.id).all()
    # Filtrar categorías inválidas
    categories = [c for c in categories if c.name and c.name.strip() and c.name.strip().lower() not in ['sin categoría', 'undefined']]

    # Inicializar dict para metas agrupadas
    goals_by_category = {c.name: [] for c in categories}

    GENERAL_NAME = 'General'  # Categoría fallback
    for goal in user_goals:
        category_name = goal.category.name if goal.category else None
        if not category_name or category_name.strip().lower() in ['sin categoría', 'undefined']:
            category_name = GENERAL_NAME
            if GENERAL_NAME not in goals_by_category:
                goals_by_category[GENERAL_NAME] = []
        if category_name not in goals_by_category:
            goals_by_category[category_name] = []
        goals_by_category[category_name].append(goal)

    # Asegurar que "General" existe
    if GENERAL_NAME not in goals_by_category:
        goals_by_category[GENERAL_NAME] = []

    total_goals = len(user_goals)
    completed_goals = sum(1 for g in user_goals if g.completed)
    completion_percent = int((completed_goals / total_goals) * 100) if total_goals > 0 else 0

    default_category_id = categories[0].id if categories else None

    return render_template(
        'goals.html',
        goals_by_category=goals_by_category,
        total_goals=total_goals,
        completed_goals=completed_goals,
        completion_percent=completion_percent,
        categories=categories,
        default_category_id=default_category_id
    )


@main_bp.route('/juegos')
@login_required
def juegos():
    juegos = [
        {"nombre": "Cálculo Mental", "ruta": url_for('main.calculo_mental')},
        {"nombre": "Memoria", "ruta": url_for('main.memoria')},
        {"nombre": "Reacción", "ruta": url_for('main.reaccion')},
        {"nombre": "Secuencia Inversa", "ruta": url_for('main.secuencia_inversa')}
    ]
    return render_template('juegos/index.html', juegos=juegos)

@main_bp.route('/juegos/calculo_mental')
@login_required
def calculo_mental():
    return render_template('juegos/calculo_mental.html')

@main_bp.route('/juegos/memoria')
@login_required
def memoria():
    return render_template('juegos/memoria.html')

@main_bp.route('/juegos/reaccion')
@login_required
def reaccion():
    return render_template('juegos/reaccion.html')

@main_bp.route('/juegos/secuencia_inversa')
@login_required
def secuencia_inversa():
    return render_template('juegos/secuencia_inversa.html')




@main_bp.route('/herramientas')
@login_required
def herramientas():
    return render_template('herramientas/index.html')


@main_bp.route('/herramientas/gestor_contrasenas', methods=['GET', 'POST'])
@login_required
def gestor_contrasenas():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not password:
            flash("Nombre y contraseña son obligatorios.", "error")
        else:
            entry = PasswordEntry(user_id=current_user.id, name=name, password=password)
            db.session.add(entry)
            db.session.commit()
            flash("Contraseña guardada correctamente.", "success")
            return redirect(url_for('main.gestor_contrasenas'))

    passwords = PasswordEntry.query.filter_by(user_id=current_user.id) \
                                   .order_by(PasswordEntry.created_at.desc()) \
                                   .all()
    resp = make_response(render_template('herramientas/gestor_contrasenas.html', passwords=passwords))

    # Evitar caché del navegador
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'

    return resp

@main_bp.route('/herramientas/gestor_contrasenas/generar', methods=['GET'])
@login_required
def generate_password():
    length = int(request.args.get('length', 16))
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    generated = ''.join(random.choice(alphabet) for _ in range(length))
    return jsonify({'password': generated})


# EDITAR contraseña por AJAX (POST JSON)
@main_bp.route('/update_password/<int:entry_id>', methods=['POST'])
@login_required
def update_password(entry_id):
    data = request.get_json()
    if not data or 'name' not in data or 'password' not in data:
        abort(400, description="Solicitud inválida")

    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    entry.name = data.get('name', entry.name)
    entry.password = data.get('password', entry.password)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Contraseña actualizada'})

@main_bp.route('/delete_password/<int:entry_id>', methods=['POST'])
@login_required
def delete_password(entry_id):
    entry = PasswordEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'status': 'deleted', 'message': 'Contraseña eliminada'})


# --------------------------------------------------------------
# 📌 API: Obtener toda la estructura del diario del usuario
# --------------------------------------------------------------
@main_bp.route("/api/diario", methods=["GET"])
@login_required
def api_get_diario():
    """
    Devuelve toda la estructura del diario para el usuario actual
    """
    # Obtenemos directamente las notas del usuario actual con filtro user_id
    apartados = DiarioApartado.query.filter_by(user_id=current_user.id).all()

    temas = DiarioTema.query.filter_by(user_id=current_user.id).all()
    categorias = (
        DiarioCategoria.query
        .join(DiarioTema)
        .filter(DiarioTema.user_id == current_user.id)
        .all()
    )
    subcategorias = (
        DiarioSubcategoria.query
        .join(DiarioCategoria).join(DiarioTema)
        .filter(DiarioTema.user_id == current_user.id)
        .all()
    )

    data = {
        "temas": [
            {"id": t.id, "name": t.titulo, "createdAt": t.fecha_creacion.isoformat()}
            for t in temas
        ],
        "categorias": [
            {"id": c.id, "name": c.nombre, "temaId": c.tema_id}
            for c in categorias
        ],
        "subcategorias": [
            {"id": s.id, "name": s.nombre, "categoriaId": s.categoria_id}
            for s in subcategorias
        ],
        "notas": [
            {
                "id": a.id,
                "title": (a.contenido.split("\n")[0][:50]) if a.contenido else "",
                "content": a.contenido,
                "createdAt": a.fecha_creacion.isoformat(),
                "place": (
                    f"tema:{a.tema_id}" if a.tema_id else
                    f"categoria:{a.categoria_id}" if a.categoria_id else
                    f"subcategoria:{a.subcategoria_id}" if a.subcategoria_id else
                    "root"
                ),
                "tags": []  # Aquí puedes mapear etiquetas si las manejas
            }
            for a in apartados
        ]
    }
    return jsonify(data)



# --------------------------------------------------------------
# 📌 API: Guardar toda la estructura del diario
# --------------------------------------------------------------
@main_bp.route("/api/diario", methods=["POST"])
@login_required
def api_save_diario():
    payload = request.get_json()

    # Primero actualizar o crear temas
    tema_map = {}
    for t in payload.get("temas", []):
        tema = None
        if "id" in t:
            tema = DiarioTema.query.filter_by(id=t["id"], user_id=current_user.id).first()
        if tema:
            tema.titulo = t["name"]
            tema.fecha_creacion = datetime.fromisoformat(t["createdAt"]) if "createdAt" in t else tema.fecha_creacion
        else:
            tema = DiarioTema(
                titulo=t["name"],
                fecha_creacion=datetime.fromisoformat(t["createdAt"]) if "createdAt" in t else datetime.utcnow(),
                user_id=current_user.id
            )
            db.session.add(tema)
        db.session.flush()
        tema_map[t.get("id")] = tema.id

    # Actualizar o crear categorías
    cat_map = {}
    # En api_save_diario
    for c in payload.get("categorias", []):
        temaId_raw = c.get("temaId")
        if temaId_raw is None:
            abort(400, "Cada categoría debe tener un tema padre válido (temaId)")
        try:
            # convierte el id a int para asegurar coincidencia con claves en tema_map
            tema_id = tema_map.get(int(temaId_raw))
        except (ValueError, TypeError):
            abort(400, "temaId inválido")
        if not tema_id:
            abort(400, f"Tema padre con id {temaId_raw} no encontrado")

        categoria = None
        if "id" in c:
            categoria = DiarioCategoria.query.filter_by(id=c["id"]).first()
        if categoria:
            categoria.nombre = c["name"]
            categoria.tema_id = tema_id
        else:
            categoria = DiarioCategoria(
                nombre=c["name"],
                tema_id=tema_id
            )
            db.session.add(categoria)
        db.session.flush()
        cat_map[c.get("id")] = categoria.id


    # Actualizar o crear subcategorías
    sub_map = {}
    for s in payload.get("subcategorias", []):
        subcategoria = None
        if "id" in s:
            subcategoria = DiarioSubcategoria.query.filter_by(id=s["id"]).first()
        if subcategoria:
            subcategoria.nombre = s["name"]
            subcategoria.categoria_id = cat_map.get(s.get("categoriaId"))
        else:
            subcategoria = DiarioSubcategoria(
                nombre=s["name"],
                categoria_id=cat_map.get(s.get("categoriaId"))
            )
            db.session.add(subcategoria)
        db.session.flush()
        sub_map[s.get("id")] = subcategoria.id

    # Actualizar o crear notas sin eliminar las demás
    # Obtener IDs existentes para no duplicar
    existing_apartados = {a.id: a for a in DiarioApartado.query.filter_by(user_id=current_user.id).all()}
    incoming_ids = set()

    for n in payload.get("notas", []):
        apartado = None
        if "id" in n and n["id"] in existing_apartados:
            apartado = existing_apartados[n["id"]]
        else:
            apartado = DiarioApartado(user_id=current_user.id)
            db.session.add(apartado)

        apartado.contenido = n.get("content", "")
        apartado.fecha_creacion = datetime.fromisoformat(n["createdAt"]) if "createdAt" in n else datetime.utcnow()

        place = n.get("place")
        apartado.tema_id = None
        apartado.categoria_id = None
        apartado.subcategoria_id = None

        if place and place.startswith("tema:"):
            apartado.tema_id = tema_map.get(place.split(":")[1])
        elif place and place.startswith("categoria:"):
            apartado.categoria_id = cat_map.get(place.split(":")[1])
        elif place and place.startswith("subcategoria:"):
            apartado.subcategoria_id = sub_map.get(place.split(":")[1])

        incoming_ids.add(apartado.id)

    # Borrar notas que no están en el incoming payload (opcional)
    for apartado_id in existing_apartados.keys():
        if apartado_id not in incoming_ids:
            db.session.delete(existing_apartados[apartado_id])

    db.session.commit()
    return jsonify({"status": "ok"})





# --------------------------------------------------------------
# 📌 API: Borrar elemento individual
# --------------------------------------------------------------
@main_bp.route("/api/diario/apartado/<int:item_id>", methods=["DELETE"])
@login_required
def delete_apartado(item_id):
    try:
        apartado = DiarioApartado.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
        db.session.delete(apartado)
        db.session.commit()
        return jsonify({"status": "deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/diario/tema/<int:item_id>", methods=["DELETE"])
@login_required
def delete_tema(item_id):
    try:
        tema = DiarioTema.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
        db.session.delete(tema)
        db.session.commit()
        return jsonify({"status": "deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/diario/categoria/<int:item_id>", methods=["DELETE"])
@login_required
def delete_categoria(item_id):
    try:
        categoria = DiarioCategoria.query.join(DiarioTema) \
            .filter(DiarioCategoria.id == item_id, DiarioTema.user_id == current_user.id).first_or_404()
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({"status": "deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/diario/subcategoria/<int:item_id>", methods=["DELETE"])
@login_required
def delete_subcategoria(item_id):
    try:
        subcategoria = DiarioSubcategoria.query.join(DiarioCategoria).join(DiarioTema) \
            .filter(DiarioSubcategoria.id == item_id, DiarioTema.user_id == current_user.id).first_or_404()
        db.session.delete(subcategoria)
        db.session.commit()
        return jsonify({"status": "deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500



# --------------------------------------------------------------
# 📌 API: Borrar todos los elementos de un tipo
# --------------------------------------------------------------
@main_bp.route("/api/diario/apartado/delete_all", methods=["POST"])
@login_required
def delete_all_apartados():
    try:
        count = DiarioApartado.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({"status": "deleted", "count": count})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/diario/tema/delete_all", methods=["POST"])
@login_required
def delete_all_temas():
    try:
        count = DiarioTema.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({"status": "deleted", "count": count})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/diario/categoria/delete_all", methods=["POST"])
@login_required
def delete_all_categorias():
    try:
        count = DiarioCategoria.query.join(DiarioTema).filter(DiarioTema.user_id == current_user.id).delete()
        db.session.commit()
        return jsonify({"status": "deleted", "count": count})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/diario/subcategoria/delete_all", methods=["POST"])
@login_required
def delete_all_subcategorias():
    try:
        count = DiarioSubcategoria.query.join(DiarioCategoria).join(DiarioTema) \
            .filter(DiarioTema.user_id == current_user.id).delete()
        db.session.commit()
        return jsonify({"status": "deleted", "count": count})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500



# --------------------------------------------------------------
# 📌 API: Editar elemento individual
# --------------------------------------------------------------
@main_bp.route("/api/diario/<string:tipo>/<int:item_id>", methods=["PUT"])
@login_required
def api_update_diario_item(tipo, item_id):
    data = request.get_json() or {}
    nuevo_titulo = data.get("titulo")
    nuevo_contenido = data.get("contenido")

    modelo_map = {
        "tema": DiarioTema,
        "apartado": DiarioApartado,
        "categoria": DiarioCategoria,
        "subcategoria": DiarioSubcategoria
    }
    modelo = modelo_map.get(tipo)
    if not modelo:
        abort(400, "Tipo inválido")

    if tipo == "tema":
        item = modelo.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
        if nuevo_titulo:
            item.titulo = nuevo_titulo
    elif tipo == "apartado":
        item = modelo.query.join(DiarioTema, isouter=True) \
            .filter(modelo.id == item_id, DiarioTema.user_id == current_user.id).first_or_404()
        if nuevo_contenido:
            item.contenido = nuevo_contenido
    elif tipo == "categoria":
        item = modelo.query.join(DiarioTema) \
            .filter(modelo.id == item_id, DiarioTema.user_id == current_user.id).first_or_404()
        if nuevo_titulo:
            item.nombre = nuevo_titulo
    elif tipo == "subcategoria":
        item = modelo.query.join(DiarioCategoria).join(DiarioTema) \
            .filter(modelo.id == item_id, DiarioTema.user_id == current_user.id).first_or_404()
        if nuevo_titulo:
            item.nombre = nuevo_titulo

    db.session.commit()
    return jsonify({"status": "updated"})


# --------------------------------------------------------------
# 📌 API: Ordenar elementos
# --------------------------------------------------------------
@main_bp.route("/api/diario/ordenar/<string:tipo>", methods=["POST"])
@login_required
def api_ordenar_diario_items(tipo):
    """
    Guarda el orden de elementos según tipo.
    El modelo debe tener un campo 'order' definido para que funcione.
    """
    orden = request.get_json().get("orden", [])
    modelo_map = {
        "tema": DiarioTema,
        "apartado": DiarioApartado,
        "categoria": DiarioCategoria,
        "subcategoria": DiarioSubcategoria
    }
    modelo = modelo_map.get(tipo)
    if not modelo:
        abort(400, "Tipo inválido")

    for index, item_id in enumerate(orden):
        item = None
        if tipo == "tema":
            item = modelo.query.filter_by(id=item_id, user_id=current_user.id).first()
        elif tipo == "categoria":
            item = modelo.query.join(DiarioTema) \
                .filter(modelo.id == item_id, DiarioTema.user_id == current_user.id).first()
        elif tipo == "subcategoria":
            item = modelo.query.join(DiarioCategoria).join(DiarioTema) \
                .filter(modelo.id == item_id, DiarioTema.user_id == current_user.id).first()
        elif tipo == "apartado":
            item = modelo.query.join(DiarioTema, isouter=True) \
                .filter(modelo.id == item_id, DiarioTema.user_id == current_user.id).first()

        if item and hasattr(item, "order"):
            item.order = index

    db.session.commit()
    return jsonify({"status": "ok"})

