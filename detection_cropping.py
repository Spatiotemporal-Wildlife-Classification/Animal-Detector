import json
import sys
import numpy as np
import cv2

root_path = sys.path[1]
raw_image_path = root_path + '/data/images/raw/'
processed_image_path = root_path + '/data/images/processed/'
bounding_box_path = root_path + '/bounding_boxes.json'


# Going through the list:
# Check per image if there are any predictions, if none this can be skipped.
# If there are predictions check categorical type
# If categorical type match animal
# Crop image using bb specifications (may result in 1+ images)

def process_images(bounding_boxes):
    for i in bounding_boxes['images']:
        file_name = i['file']
        img = cv2.imread(raw_image_path + file_name)

        print(file_name)
        detections = i['detections']

        if len(detections) != 0:
            detection_count = 0
            for detect in detections:
                if detect['category'] == '1':
                    print(detect)
                    crop_image(detect, img, detection_count, file_name)
                    detection_count = detection_count + 1


def crop_image(detect, img, detection_count, file_name):
    multiple_detections_id = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    (x1, x2, y1, y2) = convert_to_coords(detect['bbox'], img)
    print(x1, x2, y1, y2)
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