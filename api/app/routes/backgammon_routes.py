from ..controllers import backgammon_controller
from flask import Blueprint

bp = Blueprint('backgammon', __name__, url_prefix='/api/backgammon')

@bp.route('/parse', methods=['POST'])
def parse_image():
    return backgammon_controller.parse_image()

@bp.route('/detect', methods=['POST'])
def detect():
    return backgammon_controller.detect_objects()

@bp.route('/hint', methods=['POST'])
def detect():
    return backgammon_controller.hint()
