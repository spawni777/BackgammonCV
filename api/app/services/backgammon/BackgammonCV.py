# Importing the necessary modules
from ...services.backgammon.BoardPosition import BoardPosition
from ...services.backgammon.Dice import Dice
from ...services.backgammon.Board import Board
from ...services.backgammon.Color import Color
from ...services.backgammon.Detector import Detector
from ...services.backgammon.Disk import Disk
from ...services.backgammon.Point import Point
from ...services.backgammon.Class import Class
from ...utils.get_full_path import get_full_path
import cv2
import numpy as np
from shapely.geometry import Point as ShapelyPoint, Polygon
from ...services.backgammon.Constants import POINT_BBOXS, POINT_CENTERS, NUM_POINTS, NUM_POINT_HOMOGRAPHY


class BackgammonCV:
    def __init__(self):
        self.template_aligned = False
        self.detector = Detector(p_min=0.2, threshold_nms=0.3)

        self.template = []
        self.template_width = 0
        self.template_height = 0
        self.image_width = 0
        self.image_height = 0

        self.points_template = []
        self.points_homography = []
        self.transformation_matrix = []

        self.point_centers = POINT_CENTERS
        self.point_bboxs = POINT_BBOXS

        self.board = Board()

        self.loadTemplate()

    def loadTemplate(self):
        self.template = cv2.imread(get_full_path("data/images/template.jpg"))
        self.template_height, self.template_width, _ = self.template.shape
        self.points_template = [
            (0, 0),
            (self.template_width, 0),
            (self.template_width, self.template_height),
            (0, self.template_height),
        ]

    def get_game_data(self, image, points_homography):
        """
        Given an image and 4 corners of the board, returns the positions of the checkers on the board.

        :param image: The image of the backgammon board.
        :param points_homography: List of 4 points [(x, y), ...] defining the corners of the board in the image.
        :return: Dictionary mapping positions to list of checkers.
        """

        self.frame = image
        self.image_height, self.image_width, _ = self.frame.shape

        self.points_homography = points_homography

        # Set board bbox to the homography points
        self.board.bbox = self.points_homography.copy()

        # Add points to board
        self.board.points = []  # Reset points
        for i in range(len(self.point_bboxs)):
            point = Point((i + 1), self.point_centers[i], bbox=self.point_bboxs[i])
            self.board.addPoint(point)

        # MATRIX TRANSFORM --------------------------------------------------------------

        # Find matrix
        source = np.asarray(self.points_template, dtype=np.float32)
        destination = np.asarray(self.points_homography, dtype=np.float32)
        self.transformation_matrix = cv2.getPerspectiveTransform(source, destination)

        # Apply transformation to all point's bbox
        for point in self.board.points:
            point.bbox_warped = np.asarray(point.bbox, dtype=np.float32)
            point.bbox_warped = point.bbox_warped.reshape((-1, 1, 2))

            point.bbox_warped = cv2.perspectiveTransform(
                point.bbox_warped, self.transformation_matrix
            )

            point.bbox_warped = np.array(point.bbox_warped, dtype=np.int32)

        self.template_aligned = True

        # Now perform detection
        checker_positions, dices = self.detect(image)

        return checker_positions, dices

    def detect(self, image):
        if not self.template_aligned:
            print(
                "\nFirst you need to align the template. Provide the four corner points of the board.\n"
            )
            return

        self.frame = image

        self.board.clear()

        self.image_height, self.image_width, _ = self.frame.shape

        results, class_numbers, confidences, bounding_boxes, centers = self.detector.detect(self.frame)

        # Generate objects from detection ---------------------------------------------------------------
        for i in range(len(centers)):

            # DISK WHITE
            if class_numbers[i] == Class.DISK_WHITE:
                newDisk = Disk(
                    centers[i], confidences[i], Color.WHITE
                )
                self.board.addDisk(newDisk)

            # DISK BLACK
            if class_numbers[i] == Class.DISK_BLACK:
                newDisk = Disk(
                    centers[i], confidences[i], Color.BLACK
                )
                self.board.addDisk(newDisk)

            # DICE
            if self.detector.class_numbers[i] < Class.DISKS:
                newDice = Dice(self.detector.class_numbers[i], self.detector.centers[i], self.detector.confidences[i])

                # Dice position binarization
                if newDice.center[0] >= self.board.getBar().bbox_warped[0][0][0]:
                    newDice.board_position = BoardPosition.RIGHT
                else:
                    newDice.board_position = BoardPosition.LEFT

                self.board.addDice(newDice)

        # Checkers positions --------------------------------------------------------------
        checker_positions = {str(i): [] for i in range(1, 25)}  # Dictionary to hold the results

        # Loop through each point on the board
        for index, point in enumerate(self.board.points):
            position = str(index + 1)  # Convert index + 1 to string to match dictionary keys

            # Loop through each disk in the point
            for disk in point.disks:
                # Determine the checker label based on the disk color
                checker_label = "player_1" if disk.color == Color.WHITE else "player_2"

                # Add the checker label to the corresponding position
                checker_positions[position].append(checker_label)

        # Dices --------------------------------------------------------------
        dices = [{"value": int(dice.value), "confidence": float(dice.confidence)} for dice in self.board.dices]

        return checker_positions, dices

    def pointInPoly(self, point, polygon):
        """
        Check if a point is inside a polygon.

        :param point: Tuple (x, y).
        :param polygon: List of tuples [(x1, y1), (x2, y2), ...].
        :return: True if the point is inside the polygon, False otherwise.
        """
        shapely_point = ShapelyPoint(point)
        shapely_polygon = Polygon(polygon)
        return shapely_polygon.contains(shapely_point)

# Example usage:
if __name__ == "__main__":
    # Instantiate the class
    backgammon_cv = BackgammonCV()

    # Load the image
    image = cv2.imread("path_to_your_image.jpg")

    # Provide the four corner points of the board in the image
    # Replace these with your actual points
    points_homography = [
        (x1, y1),  # Top-left corner
        (x2, y2),  # Top-right corner
        (x3, y3),  # Bottom-right corner
        (x4, y4),  # Bottom-left corner
    ]

    # Get the checker positions
    positions = backgammon_cv.get_checker_positions(image, points_homography)

    print(positions)
