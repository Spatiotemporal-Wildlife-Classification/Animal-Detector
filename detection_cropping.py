import json
import sys

root_path = sys.path[1]
raw_image_path = root_path + '/data/images/raw/'
processed_image_path = root_path + '/data/images/processed/'
bounding_box_path = root_path + '/bounding_boxes.json'

def categorical_culling(bounding_boxes):
    for i in bounding_boxes['images']:
        file_name = i['file']
        detections = i['detections']
        print(file_name)
        print(detections)


# Going through the list:
# Check per image if there are any predictions, if none this can be skipped.
# If there are predictions check categorical type
# If categorical type match animal
# Crop image using bb specifications (may result in 1+ images)

def process_images(bounding_boxes):
    for i in bounding_boxes['images']:
        file_name = i['file']

        print(file_name)
        detections = i['detections']

        if len(detections) != 0:
            for detect in detections:
                if detect['category'] == '1':
                    print(detect)



if __name__ == "__main__":
    f = open(bounding_box_path, 'r')
    bounding_boxes = json.loads(f.read())

    process_images(bounding_boxes)