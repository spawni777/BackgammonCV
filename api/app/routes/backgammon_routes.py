from flask import Blueprint, request, jsonify, send_file
import cv2
import numpy as np
import io
from ..utils.resize_and_pad_image import resize_and_pad_image
from ..utils.filter_and_get_largest_rectangle import filter_and_get_largest_rectangle
from ..services.backgammon.Detector import Detector

bp = Blueprint('backgammon', __name__, url_prefix='/api/backgammon')

@bp.route('/parse', methods=['POST'])
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
