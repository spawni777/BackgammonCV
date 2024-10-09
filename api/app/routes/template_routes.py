from flask import Blueprint, render_template
from ..controllers import user_controller

bp = Blueprint('templates', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/users')
def list_users():
    users = user_controller.get_users()
    return render_template('users.html', users=users["users"])
