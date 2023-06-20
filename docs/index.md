# Animal Detector

This repository serves 4 purposes arranged in sequential steps: 
1. Download the raw observation images from iNaturalist observations. 
2. Execute Mega-detector object detection to identify individual animal instances
3. Crop Mega-detector animal instanced into sub-images
4. Arrange each sub-image into a taxonomic directory structure. 

The below headings provide information on how to execute each step, what the process entails, and what the expected
output should be. This page provides additional links to the repositories providing the observations data, and the repositories
using the resulting data. 

## Data Origin
Please use the `<dataset_name>_train.csv` file that is located within the [Wildlife Classification](https://github.com/Spatiotemporal-Wildlife-Classification/Wildlife-Classification)
repository. The data is produced as part of the data preparation process. Please consult the README and the documentation of that repository
for further information. The link to the documentation is as follows: [https://spatiotemporal-wildlife-classification.github.io/Wildlife-Classification/](https://spatiotemporal-wildlife-classification.github.io/Wildlife-Classification/)


## 1. Download Observations
This process aims to download the observations from the iNaturalist observation urls. 

The `raw_data_access.py` file is responsible for raw image downloads. 
Please perform the following steps to download the raw images for an iNaturalist observations CSV file.

1. Load the `<observations>.csv` file into the `observations/` directory. 
    - In this case, it is the `proboscidia_train.csv` file. This file is available at a public Dataset: [https://www.kaggle.com/datasets/travisdaws/spatiotemporal-wildlife-dataset](https://www.kaggle.com/datasets/travisdaws/spatiotemporal-wildlife-dataset)
2. Specify the name of the observation file on line 90.
3. Execute the file. The progress bar will update you on the status of the download.

## Project layout

    ai4eutils/  # ai4eutils repository
    CameraTraps/  # CameraTraps repository
    data/  
    docs/  
    yolov5/  # Yolov5 repository
    resources/  # Resources for documentation
    bounding_boxes.json  # Step 2 resulting file
    dataset_structure.py  # Step 4
    detection_cropping.py  # Step 3
    mkdocs.yml  # Documentation configuration
    raw_data_access.py  # Step 1
    README.md 
