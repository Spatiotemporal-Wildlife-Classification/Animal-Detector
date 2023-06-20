"""This file creates sub-images based on Mega-detector animal detections within the raw observation images.

    It is essential, that steps 1 and 2 in the README are completed before this step, as the downloaded raw observation images
    and the object detection bounding_box.json` file are required for this script's execution.

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
    """This method crops an image based on the bounding box created by Mega-detector.

    Each image is assigned a sub-image suffix character to represent the current sub-image number.
    The sub-image is enhanced through Lanczos Interpolation and edge enhancement kernels to maintain resolution.
    However, resolution loss still occurs due to the cropping process.

    Args:
        detect (JSON dict): The current object detection of the observation image (from `bounding_boxes.json`)
        img (Image): The raw observation image in which the objects were detected.
        detection_count (int): The number of sub-images cropped so far.
        file_name (str): The name of the raw image in the format `<Observation id>.jpg`
    """
    multiple_detections_id = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']

    (x1, x2, y1, y2) = convert_to_coords(detect['bbox'],
                                         img)  # Convert the bounding box values into coordinates for image cropping
    cropped_img = img[y1:y2, x1:x2]  # Crop the image

    cropped_img = cv2.resize(cropped_img, (224, 224), cv2.INTER_LANCZOS4)  # Resize and interpolate image
    enhanced_img = enhance_image(cropped_img)  # Perform image enhancement

    count_extension = multiple_detections_id[detection_count]  # Determine the sub-image suffix
    cv2.imwrite(processed_image_path + adapt_name(file_name, count_extension), enhanced_img)  # Save cropped image


def enhance_image(cropped_img):
    """This method attempts to enhance the cropped and resize image through edge enhancement, to ensure that crucial
    details of the image are not lost.

    Args:
        cropped_img (Image): The cropped and resized (interpolated) image to be enhanced.

    Returns:
        (Image): The edge enhanced image.
    """
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened_img = cv2.filter2D(src=cropped_img, ddepth=-1, kernel=kernel)
    return sharpened_img


def adapt_name(file_name, detector_count_extension):
    """This method adapts the name of the raw observation image to include the sub-image suffix.

    Args:
        file_name (str): The filename of the raw observation image in the format `<Observation id>.jpg`
        detector_count_extension (str): The alphabetical character sub-image extension indicating what sub-image number this is.

    Returns:
        (str): The modified image name to include the sub-image suffix extension.
    """
    image_id = file_name[:-4]
    file_name_adapted = image_id + '_' + detector_count_extension + '.jpg'
    return file_name_adapted


def convert_to_coords(array, img):
    """This method converts the `bounding_boxes.json` `bbox` values into coordinates used to crop the sub-image

    The `bbox` JSON dictionary contains the following value:
    ```
    bbox: [
        percentage width of the center of the bounding box,
        percentage height of the center of the bounding box,
        The percentage width of bounding box. The percentage is calculated as the percentage of the width of the image,
        The percentage height of the bounding box. The percentage is calculated as the percentage of the height of the image
        ]
    ```

    Args:
        array (List): The list of `bbox` values for the object detection.
        img (Image): The raw observation image on which the object detection occurred.

    Returns:
        (list): The list contains the following coordinates: [x_start, x_end, y_start, y_end] to suit the image slicing that produces the cropped image.
    """
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
    f = open(bounding_box_path, 'r')  # Open the bounding box file
    bounding_boxes = json.loads(f.read())  # Red the contents into JSON format
    process_images(bounding_boxes)  # Process and crop the images
