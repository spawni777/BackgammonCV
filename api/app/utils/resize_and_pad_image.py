import cv2
import numpy as np


def resize_and_pad_image(image, desired_size=1024):
    old_size = image.shape[:2]  # Get the current size (height, width)

    # Calculate the ratio of the desired size to the old size
    ratio = float(desired_size) / max(old_size)
    new_size = tuple([int(x * ratio) for x in old_size])

    # Resize the image while keeping the aspect ratio
    resized_image = cv2.resize(image, (new_size[1], new_size[0]))

    # Create a new square image (desired_size x desired_size) and fill with black (zeros)
    new_image = np.zeros((desired_size, desired_size, 3), dtype=np.uint8)

    # Paste the resized image into the center of the new image
    new_image[
        (desired_size - new_size[0]) // 2 : (desired_size - new_size[0]) // 2
        + new_size[0],
        (desired_size - new_size[1]) // 2 : (desired_size - new_size[1]) // 2
        + new_size[1],
    ] = resized_image

    return new_image
