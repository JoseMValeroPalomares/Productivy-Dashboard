import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from app.db import db  # importar la instancia central de db
from app.routes.main import main_bp
from app.routes.goals import goals_bp
from app.routes.categories import categories_bp
from app.routes.herramientas import herramientas_bp
from app.routes.schedule import schedule_bp
from app.routes.tasks import tasks_api, tasks_page
from config import Config

# Carga el archivo .env automáticamente al iniciar la app
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar la base de datos
    db.init_app(app)
    from app import models

    # Inicializar migraciones, activando render_as_batch para SQLite
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        migrate = Migrate(app, db, render_as_batch=True)
    else:
        migrate = Migrate(app, db)

    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Context processor para inyectar current_user en las plantillas
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(herramientas_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    app.register_blueprint(tasks_page)  # /tasks
    app.register_blueprint(tasks_api)   # /api/events

    app.register_blueprint(schedule_bp)

    return app
