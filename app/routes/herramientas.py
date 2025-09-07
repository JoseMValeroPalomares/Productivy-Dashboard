from flask import Blueprint, render_template
from flask_login import login_required

# Definición del blueprint con url_prefix '/herramientas'
herramientas_bp = Blueprint('herramientas', __name__, url_prefix='/herramientas')


@herramientas_bp.route('/')
@login_required
def index():
    return render_template('herramientas/index.html')


@herramientas_bp.route('/calculadora')
@login_required
def calculadora():
    return render_template('herramientas/calculadora.html')


@herramientas_bp.route('/matrices')
@login_required
def matrices():
    return render_template('herramientas/matrices.html')


@herramientas_bp.route('/determinante')
@login_required
def determinante():
    return render_template('herramientas/determinante.html')


@herramientas_bp.route('/estadistica')
@login_required
def estadistica():
    return render_template('herramientas/estadistica.html')


@herramientas_bp.route('/conversores')
@login_required
def conversores():
    return render_template('herramientas/conversores.html')


@herramientas_bp.route('/unidades')
@login_required
def unidades():
    return render_template('herramientas/unidades.html')


@herramientas_bp.route('/tabla_verdad')
@login_required
def tabla_verdad():
    return render_template('herramientas/tabla_verdad.html')


@herramientas_bp.route('/automata')
@login_required
def automata():
    return render_template('herramientas/automata.html')

@herramientas_bp.route('/contrasenas')
@login_required
def contrasenas():
    return render_template('herramientas/contrasenas.html')


@herramientas_bp.route('/diario')
@login_required
def diario():
    return render_template('herramientas/diario.html')
