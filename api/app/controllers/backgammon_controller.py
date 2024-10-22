from flask import request, jsonify, send_file
import cv2
import numpy as np
import io
import subprocess
import re
import random

from ..db.BackgammonGameRepository import BackgammonRepository
from ..utils.resize_and_pad_image import resize_and_pad_image
from ..utils.filter_and_get_largest_rectangle import filter_and_get_largest_rectangle
from ..services.backgammon.BackgammonCV import BackgammonCV
from ..services.backgammon.Detector import Detector


def parse_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    image_file = request.files['image']

    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read the image into OpenCV format
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Resize image if necessary (adjust according to your model's requirements)
        image = resize_and_pad_image(image, 608)

        # Instantiate the Detector
        p_min = 0.3
        threshold_nms = 0.3
        detector = Detector(p_min, threshold_nms)

        # Perform detection
        detector.detect(image)

        # Retrieve class_numbers and bounding_boxes
        class_numbers = detector.class_numbers
        bounding_boxes = detector.bounding_boxes  # Corrected attribute name

        # Specify the target classes that correspond to the board edges or markers
        # Adjust these class numbers to match your model's outputs for the board
        target_classes = [6, 7]  # Example class numbers representing board markers

        # Use the utility function to filter and get the largest rectangle
        rectangle = filter_and_get_largest_rectangle(bounding_boxes, class_numbers, target_classes)

        if rectangle:
            top_left, bottom_right = rectangle

            # Compute the four corner points of the rectangle
            x_min, y_min = top_left
            x_max, y_max = bottom_right

            # Define the four corners of the rectangle in the correct order
            points_homography = [
                (x_min, y_min),  # Top-left corner
                (x_max, y_min),  # Top-right corner
                (x_max, y_max),  # Bottom-right corner
                (x_min, y_max),  # Bottom-left corner
            ]

            # Instantiate the BackgammonCV class
            backgammon_cv = BackgammonCV()

            # Get the checker positions
            checker_positions, dices = backgammon_cv.get_game_data(image, points_homography)

            if not dices or len(dices) < 2:
                dices = [
                    {"value": random.randint(1, 6), "randomized": True},
                    {"value": random.randint(1, 6), "randomized": True}
                ]

            # Return the positions as a JSON response
            return jsonify({"checkerPositions": checker_positions, "dices": dices}), 200
        else:
            return jsonify({"error": "Unable to detect the game board."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def detect_objects():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read the image into OpenCV format
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Resize image for the model
        image = resize_and_pad_image(image, 608)

        # Detect checkers on the image
        p_min = 0.3
        threshold_nms = 0.3
        detector = Detector(p_min, threshold_nms)

        results, class_numbers, confidences, bounding_boxes, centers = detector.detect(image)

        # At least one detection should exist, draw results on the image
        image = detector.drawResult()

        # Specify the target classes (for example, class 7 and class 6)
        target_classes = [6, 7]

        # Use the utility function to filter and get the largest rectangle
        rectangle = filter_and_get_largest_rectangle(bounding_boxes, class_numbers, target_classes)

        if rectangle:
            top_left, bottom_right = rectangle
            # Draw the rectangle on the image
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

            # Add a label "game_space" above the rectangle
            label = "game_space"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_color = (0, 255, 0)  # Green color (same as rectangle)
            thickness = 1

            # Determine the label's position (above the top-left corner of the rectangle)
            label_size, _ = cv2.getTextSize(label, font, font_scale, thickness)
            label_x = top_left[0]  # X coordinate for label
            label_y = top_left[1] - 30  # Y coordinate for label (above the rectangle)

            # Make sure the label does not go out of the image bounds
            label_y = max(label_y, label_size[1])

            # Put the text on the image
            cv2.putText(image, label, (label_x, label_y), font, font_scale, font_color, thickness)

        # Encode the modified image to return as response
        _, buffer = cv2.imencode('.jpg', image)
        image_io = io.BytesIO(buffer)

        # Return the image as a response
        return send_file(image_io, mimetype='image/jpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def convert_checker_positions(checker_positions):
    board = [0] * 26

    for position, checkers in checker_positions.items():
        pos_index = int(position)

        # Temp zeros (we need to detect bar checkers later, now the first element and the last element are zeros)
        if pos_index == 0 | pos_index == 25:
            board[pos_index] = 0
            continue

        if checkers:
            if checkers[0] == 'player_1':
                board[pos_index] = len(checkers)
            elif checkers[0] == 'player_2':
                board[pos_index] = -len(checkers)

    return board

def get_suggested_moves(board_position, dice_rolls):
    script_content = f"""
import gnubg

gnubg.command('new match')

board = {board_position}
gnubg.command(f"set board simple {{' '.join(map(str, board))}}")

gnubg.command(f"set dice {dice_rolls[0]} {dice_rolls[1]}")

gnubg.command("hint")
    """

    script_path = '/tmp/get_moves.py'
    with open(script_path, 'w') as script_file:
        script_file.write(script_content)

    result = subprocess.run(['/usr/games/gnubg', '-p', script_path, '-q'], capture_output=True, text=True)

    return result.stdout

def parse_gnubg_output(output):
    lines = output.splitlines()
    
    hints = []
    capture_hints = False

    dice_regex = re.compile(r'The dice have been set to')
    hint_regex = re.compile(r'^\s*\d+\.\s+([^\d\s].*?)?$')
    
    for line in lines:
        dice_match = dice_regex.match(line)
        if dice_match:
            capture_hints = True
            continue

        if capture_hints:
            hint_match = hint_regex.match(line)
            if hint_match:
                hint_description = hint_match.group(1).strip()
                hints.append(hint_description)
    
    return hints

def hint():
    data = request.json
    checker_positions = data.get('checkerPositions')
    dice_data = data.get('dices')

    if not checker_positions:
        return jsonify({"error": "Checker positions are required"}), 400

    if not dice_data or len(dice_data) < 2:
        dice_data = [
            {"value": random.randint(1, 6), "randomized": True},
            {"value": random.randint(1, 6), "randomized": True}
        ]
        
    dice_values = [dice['value'] for dice in dice_data]

    checker_position = convert_checker_positions(checker_positions)

    repository = BackgammonRepository()
    repository.update(new_positions=checker_position, dice_values=dice_values)

    output = get_suggested_moves(checker_position, dice_values)
    suggested_moves = parse_gnubg_output(output)
    
    return jsonify(suggested_moves), 200

def get_saved_game_data():
    repository = BackgammonRepository()
    checker_position, dices, current_player = repository.get()

    repository.close()

    return jsonify({ "checker_position": checker_position, "dices": dices, "current_player": current_player }), 200

def delete_saved_game_data():
    repository = BackgammonRepository()
    repository.delete()
    repository.close()

    return jsonify({"success": True}), 200
