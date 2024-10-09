from flask import Blueprint
from ..controllers import user_controller

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/', methods=['GET'])
def list_users():
    return user_controller.get_users()

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return user_controller.get_user(user_id)
