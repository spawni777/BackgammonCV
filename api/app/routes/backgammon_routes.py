from ..utils.format_repo_game_data import format_repo_game_data
from ..controllers import backgammon_controller
from flask import Blueprint
from flask_socketio import emit
from .. import socketio

bp = Blueprint('backgammon', __name__, url_prefix='/api/backgammon')

@bp.route('/parse', methods=['POST'])
def parse_image():
    return backgammon_controller.parse_image()

@bp.route('/detect', methods=['POST'])
def detect():
    return backgammon_controller.detect_objects()

@bp.route('/hint', methods=['POST'])
def hint():
    response = backgammon_controller.hint()
    
    game_data, status_code = backgammon_controller.get_saved_game_data()

    if status_code == 200:
        formatted_data = format_repo_game_data(game_data.json['checker_position'], game_data.json['dices'], game_data.json['current_player'])
        socketio.emit('game_data', formatted_data)

    return response

@bp.route('/game-data', methods=['GET'])
def get_game_data():
    return backgammon_controller.get_saved_game_data()

@bp.route('/game-data', methods=['DELETE'])
def delete_game_data():
    response = backgammon_controller.delete_saved_game_data()

    game_data, status_code = backgammon_controller.get_saved_game_data()

    if status_code == 200:
        formatted_data = format_repo_game_data(game_data.json['checker_position'], game_data.json['dices'], game_data.json['current_player'])
        socketio.emit('game_data', formatted_data)

    return response

@socketio.on('connect')
def handle_connect(auth):
    game_data, status_code = backgammon_controller.get_saved_game_data()

    if status_code == 200:
        formatted_data = format_repo_game_data(game_data.json['checker_position'], game_data.json['dices'], game_data.json['current_player'])
        socketio.emit('game_data', formatted_data)