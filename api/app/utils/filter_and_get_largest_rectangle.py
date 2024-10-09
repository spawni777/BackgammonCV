import math

# Function to calculate the Euclidean distance between two points
def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


# Function to calculate the center of a bounding box
def get_box_center(box):
    x, y, w, h = box
    return (x + w / 2, y + h / 2)

# Function to find the two bounding boxes that are diagonally farthest from each other
def get_largest_rectangle_from_boxes(bounding_boxes):
    max_distance = 0
    farthest_boxes = None

    # Find the pair of bounding boxes with the largest diagonal distance
    for i in range(len(bounding_boxes)):
        for j in range(i + 1, len(bounding_boxes)):
            center1 = get_box_center(bounding_boxes[i])
            center2 = get_box_center(bounding_boxes[j])
            distance = euclidean_distance(center1, center2)
            if distance > max_distance:
                max_distance = distance
                farthest_boxes = (bounding_boxes[i], bounding_boxes[j])

    if farthest_boxes:
        # Get the coordinates for the largest rectangle
        box1, box2 = farthest_boxes
        x_min = min(box1[0], box2[0])
        y_min = min(box1[1], box2[1])
        x_max = max(box1[0] + box1[2], box2[0] + box2[2])
        y_max = max(box1[1] + box1[3], box2[1] + box2[3])

        # Corners of the rectangle
        top_left = (x_min, y_min)
        bottom_right = (x_max, y_max)

        return top_left, bottom_right

    return None, None

# Filter bounding boxes based on class numbers
def filter_bounding_boxes_by_class(bounding_boxes, class_numbers, target_classes):
    filtered_boxes = [
        bounding_boxes[i]
        for i in range(len(class_numbers))
        if class_numbers[i] in target_classes
    ]
    return filtered_boxes

def filter_and_get_largest_rectangle(bounding_boxes, class_numbers, target_classes):
    """
    Filters bounding boxes by target classes and returns the largest rectangle.

    :param bounding_boxes: List of bounding boxes.
    :param class_numbers: List of class numbers corresponding to each bounding box.
    :param target_classes: List of target classes to filter by.
    :return: Top-left and bottom-right coordinates of the largest rectangle if found, otherwise None.
    """
    # Filter the bounding boxes based on the specified classes
    filtered_bounding_boxes = [
        bbox for bbox, class_num in zip(bounding_boxes, class_numbers) if class_num in target_classes
    ]

    if not filtered_bounding_boxes:
        return None  # No valid bounding boxes

    # Get the largest rectangle from the filtered bounding boxes
    return get_largest_rectangle_from_boxes(filtered_bounding_boxes)


