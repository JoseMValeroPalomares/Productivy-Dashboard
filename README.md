                                        /*═══════════════════════════════════════════════════════════════*
                                        |                                                                |
                                        |   ███████╗ ███████╗  ██████╗      ██╗      ██╗                 |
                                        |   ██╔════╝ ██╔════╝ ██╔═══██╗     ██║  ██╗ ██║                 |
                                        |   █████╗   █████╗   ██║   ██║     ╚██╗████╗██╔╝                |
                                        |   ██╔══╝   ██╔══╝   ██║   ██║      ████╔═████║                 |
                                        |   ███████╗ ███████╗ ╚██████╔╝      ╚██╔╝ ╚██╔╝                 |
                                        |   ╚══════╝ ╚══════╝  ╚═════╝        ╚═╝   ╚═╝                  |
                                        |                                                                |
                                        |   ESOJOTA                                                      |
                                        |                                                                |
                                        |   Autor: josevaleropalomares@gmail.com                         |
                                        |   ✦ Code with ♥ | Built with ☕ | Debugged with console.log ✦ |
                                        |                                                                |
                                        *═══════════════════════════════════════════════════════════════*/


Dashboard de Productividad
Un sistema web personal para gestionar la productividad, tareas, metas y calendario con funcionalidades similares a Google Calendar, construido con Flask, SQLAlchemy y FullCalendar.js.

Características principales
Gestión de tareas: Crear, editar, eliminar y marcar tareas como completadas. Filtrado por prioridad y etiquetas.

Calendario interactivo: Visualiza y gestiona tareas y recordatorios en un calendario mensualmente, con soporte para arrastrar y soltar eventos (drag & drop).

Lista de tareas ordenable: Ordena y visualiza tus tareas de forma sencilla.

Gestión de metas y objetivos: Define metas, clasifícalas por categorías y sigue su progreso mediante estadísticas visuales.

Herramientas adicionales: Conversores, calculadoras y utilidades para apoyar tu productividad.

Interfaz moderna y responsiva: Diseño limpio, personalizado y animaciones suaves para una mejor experiencia de usuario.

Instalación
Clonar el repositorio:

bash
git clone https://github.com/usuario/dashboard-productividad.git
cd dashboard-productividad
Instalar dependencias:

bash
pip install -r requirements.txt
Aplicar migraciones para crear la base de datos:

bash
flask db upgrade
Ejecutar la aplicación:

bash
flask run
Luego abre tu navegador en http://localhost:5000

Estructura del proyecto
text
app/
  __init__.py             # Configuración y factory Flask
  db.py                   # Instancia SQLAlchemy
  models.py               # Definición de modelos de datos
  routes/                 # Rutas organizadas en blueprints
    main.py
    tasks.py
    goals.py
    categories.py
    herramientas.py
    auth.py
  templates/              # Plantillas HTML con Jinja2
    base.html
    tasks.html
    goals.html
    herramientas/
    juegos/
  static/                 # Archivos estáticos (CSS, JS, imágenes)
    css/
    js/
    images/
config.py                 # Configuración global del proyecto
requirements.txt          # Dependencias Python
run.py                    # Punto de entrada para lanzar la app
migrations/               # Archivos de migraciones de base de datos
README.md                 # Documentación del proyecto


Licencia
Este proyecto se distribuye bajo la licencia MIT.