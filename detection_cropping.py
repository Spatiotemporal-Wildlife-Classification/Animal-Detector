"""This file creates sub-images based on Mega-detector animal detections within the raw observation images.

    It is essential, that steps 1 and 2 in the README are completed before this step, as the downloaded raw observation images
    and the object detection    bounding_box.json` file are required for this script's execution.

    Attributes:
        root_path (str): The absolute path to the root of the project directory.
        raw_image_path (str): The complete (absolute + relative) path to the raw image directory.
        processed_image_path (str): The save path for the sub-images pointing to the `images/cropped` directory.
        bounding_box_path (str): The path to the `bounding_box.json` file.
"""
import json
import sys
import numpy as np
import cv2

root_path = sys.path[1]
raw_image_path = root_path + '/data/images/raw/'
processed_image_path = root_path + '/data/images/cropped/'
bounding_box_path = root_path + '/bounding_boxes.json'


def process_images(bounding_boxes):
    """Processes each image within the bounding_box.json file and crops them according to the animal detections.

    This method iterates through all images, matching each identified object's category to detect when it matches animal (category 1).
    When a match occurs, the image is cropped and names <Observation id>_<sub-image character>.jpg where the sub-image character
    is an alphabetical character corresponding to the number of sub-images created so for for each observation.

    Args:
        bounding_boxes (JSON): The JSON format of the bounding_boxes file.
    """
    for i in bounding_boxes['images']:  # Iterate through images in the bounding box file
        file_name = i['file']
        img = cv2.imread(raw_image_path + file_name)  # Read in the image

        try:
            detections = i['detections']  # Try and access the detections JSON (Only occurs if an object was detected)
        except:
            print('Error in Megadetector')
            continue

        if len(detections) != 0:  # Detections is not empty
            detection_count = 0  # Initialize detections counter (sub-image counter)
            for detect in detections:  # Loop through the number of detections
                if detect['category'] == '1':  # Category matches to animal
                    crop_image(detect, img, detection_count, file_name)  # Crop image
                    detection_count = detection_count + 1  # Increase detection counter (sub-image counter)


def crop_image(detect, img, detection_count, file_name):
    multiple_detections_id = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']
    (x1, x2, y1, y2) = convert_to_coords(detect['bbox'], img)
    cropped_img = img[y1:y2, x1:x2]
    cropped_img = cv2.resize(cropped_img, (224, 224), cv2.INTER_LANCZOS4)
    enhanced_img = enhance_image(cropped_img)
    count_extension = multiple_detections_id[detection_count]
    cv2.imwrite(processed_image_path + adapt_name(file_name, count_extension), enhanced_img)


def enhance_image(cropped_img):
    kernel = np.array([[0, -1, 0],
                   [-1, 5,-1],
                   [0, -1, 0]])
    sharpened_img = cv2.filter2D(src=cropped_img, ddepth=-1, kernel=kernel)
    return sharpened_img


def adapt_name(file_name, detector_count_extension):
    image_id = file_name[:-4]
    file_name_adapted = image_id + '_' + detector_count_extension + '.jpg'
    return file_name_adapted


def convert_to_coords(array, img):
    (height, width, _) = img.shape
    x_center = (array[0] * width)
    y_center = (array[1] * height)
    bb_width = (array[2] * width)
    bb_height = (array[3] * height)

    x_start = int(x_center)
    y_start = int(y_center)
    x_end = int(x_start + bb_width)
    y_end = int(y_start + bb_height)
    return [x_start, x_end, y_start, y_end]


if __name__ == "__main__":
    f = open(bounding_box_path, 'r')
    bounding_boxes = json.loads(f.read())

    process_images(bounding_boxes)

