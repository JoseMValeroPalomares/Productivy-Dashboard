
from sqlalchemy import JSON
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from app.db import db
from datetime import timezone



# =======================
# MODELO DE USUARIO
# =======================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    passwords = db.relationship('PasswordEntry', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# =======================
# CATEGORÍAS
# =======================
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('categories', lazy=True))

    def __repr__(self):
        return f"<Category {self.name}>"


# =======================
# METAS
# =======================
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('goals', lazy=True))
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('goals', lazy=True))

    def __repr__(self):
        return f"<Goal {self.description[:20]} {'(done)' if self.completed else ''}>"


# =======================
# TAREAS
# =======================
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)

    # Etiquetas
    tag = db.Column(db.String(50), nullable=True)
    tag_color = db.Column(db.String(20), nullable=True)

    # Repetición
    rrule_text = db.Column(db.Text, nullable=True)

    # Subtareas (JSON: lista de dicts)
    subtasks = db.Column(JSON, nullable=True)

    # Fechas
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date, nullable=True)

    # Datos de control
    priority = db.Column(db.Integer, default=2)  # 1=Alta, 2=Media, 3=Baja
    completed = db.Column(db.Boolean, default=False)

    # Relación con usuario
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

    @property
    def due_date(self):
        return self.start

    def __repr__(self):
        return f"<Task {self.title}>"

    def to_fullcalendar(self):
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start.strftime('%Y-%m-%d'),
            "end": self.end.strftime('%Y-%m-%d') if self.end else None,
            "priority": self.priority,
            "tag": self.tag,
            "tag_color": self.tag_color,
            "completed": self.completed,
            "rrule_text": self.rrule_text,
            "subtasks": self.subtasks or []
        }


# =======================
# EVENTOS (para calendario avanzado)
# =======================
class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=True)

    # Estado y prioridad
    priority = db.Column(db.Integer, default=2)  # 1=Alta, 2=Media, 3=Baja
    status = db.Column(db.String(20), default="pending")  # pending / completed / archived

    # Etiquetas
    tag = db.Column(db.String(50), nullable=True)
    tag_color = db.Column(db.String(20), nullable=True)

    # Recurrentes
    recurrence_rule = db.Column(db.String(200), nullable=True)

    # Relación con usuario
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))

    # Marcas de tiempo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Event {self.title} - {self.start}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None,
            "priority": self.priority,
            "status": self.status,
            "tag": self.tag,
            "tag_color": self.tag_color,
            "recurrence_rule": self.recurrence_rule
        }


# =======================
# SUBTAREAS (relación 1:N con Task)
# =======================
class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    text = db.Column(db.String(250), nullable=False)
    done = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)

    task = db.relationship('Task', backref=db.backref('subtasks_rel', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Subtask {self.text}>"

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "text": self.text,
            "done": self.done,
            "order": self.order
        }

# =======================
# CALENDARIO 
# =======================

class ScheduleTask(db.Model):
    __tablename__ = 'schedule_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_scheduletasks_user_id'), nullable=False)

    # Datos básicos
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Fecha y horario
    date = db.Column(db.Date, nullable=False)            # Día de la tarea
    end_date = db.Column(db.Date, nullable=True)         # <-- NUEVO: fecha fin para recurrencia
    start_hour = db.Column(db.Float, nullable=False)     # Ej: 9.5 = 09:30
    duration = db.Column(db.Float, nullable=False)       # Horas decimales

    # Estado
    completed = db.Column(db.Boolean, default=False)
    in_progress = db.Column(db.Boolean, default=False)

    # Apariencia y repetición
    color = db.Column(db.String(20), nullable=True)
    recurrence = db.Column(db.String(20), default='none')  # none / daily / weekly / monthly

    user = db.relationship(
        'User',
        backref=db.backref('schedule_tasks', lazy=True, cascade='all, delete-orphan')
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "date": self.date.isoformat(),
            "endDate": self.end_date.isoformat() if self.end_date else None,  # <-- incluir end_date
            "startHour": self.start_hour,
            "duration": self.duration,
            "completed": self.completed,
            "inProgress": self.in_progress,
            "color": self.color,
            "recurrence": self.recurrence
        }

class Template(db.Model):
    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_templates_user_id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Float, nullable=False, default=1.0)
    color = db.Column(db.String(20), nullable=True)
    recurrence = db.Column(db.String(20), default='none')  # none / daily / weekly / monthly

    user = db.relationship(
        'User',
        backref=db.backref('templates', lazy=True, cascade='all, delete-orphan')
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "color": self.color,
            "recurrence": self.recurrence
        }



# =======================
# HERRAMIENTAS 
# =======================

class PasswordEntry(db.Model):
    __tablename__ = 'password_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)  # Nombre o sitio web
    password = db.Column(db.String(256), nullable=False)  # En producción cifrar/encriptar
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='passwords')



class DiarioTema(db.Model):
    __tablename__ = 'diario_temas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    categorias = db.relationship('DiarioCategoria', back_populates='tema', cascade='all, delete-orphan')
    apartados = db.relationship('DiarioApartado', back_populates='tema', cascade='all, delete-orphan')


class DiarioCategoria(db.Model):
    __tablename__ = 'diario_categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)

    tema_id = db.Column(db.Integer, db.ForeignKey('diario_temas.id'), nullable=False)
    tema = db.relationship('DiarioTema', back_populates='categorias')

    subcategorias = db.relationship('DiarioSubcategoria', back_populates='categoria', cascade='all, delete-orphan')
    apartados = db.relationship('DiarioApartado', back_populates='categoria', cascade='all, delete-orphan')  # Añadido



class DiarioSubcategoria(db.Model):
    __tablename__ = 'diario_subcategorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)

    categoria_id = db.Column(db.Integer, db.ForeignKey('diario_categorias.id'), nullable=False)
    categoria = db.relationship('DiarioCategoria', back_populates='subcategorias')

    apartados = db.relationship('DiarioApartado', back_populates='subcategoria', cascade='all, delete-orphan')


class DiarioApartado(db.Model):
    __tablename__ = 'diario_apartados'
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    tema_id = db.Column(db.Integer, db.ForeignKey('diario_temas.id'), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('diario_categorias.id'), nullable=True)  # Añadido
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('diario_subcategorias.id'), nullable=True)

    tema = db.relationship('DiarioTema', back_populates='apartados')
    categoria = db.relationship('DiarioCategoria', back_populates='apartados')  # Añadido
    subcategoria = db.relationship('DiarioSubcategoria', back_populates='apartados')

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
