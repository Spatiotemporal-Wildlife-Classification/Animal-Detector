"""This file creates a taxonomic directory structure, allocating the cropped images into the correct taxonomic level and directory.

    The taxonomic directory is required for the image classification model training in the Wildlife Classification repository.
    It makes use of the `image_dataset_from_directory()` function to construct images with the corresponding labels based on the directory structure.

    Attributes:
        root_path (str): The absolute path to the root of the project directory.
        cropped_img_path (str): The path to the sub-images of the observations
        img_path (str): The path to the training directory where the images are arranged within the taxonomic directory.
        test_path (str): The path to the validation directory where the images are arranged within the taxonomic directory.
        data_path (str): The path to where the iNaturalist observations are stored.
        multiple_detections_id (list): The possible suffixes of the sub-images used to identify how many sub-images exist per observation.
        img_size (int): (528, 528) The size of the images accepted by the EfficientNet-B6 Classification model in Wildlife Classification.
        test_split (float): The percentage of images to be placed in the validation directory (A 15% validation split)
        taxonomy_list (list): The list of the taxonomic column names at which the taxon hierarchy will be based on.
        count (int): The number of sub-images placed in the correct directory.
        length (int): The total number of observations.
"""
import sys
import random
import numpy as np
import pandas as pd
import os
import shutil

# Paths
root_path = sys.path[1]
cropped_img_path = root_path + '/data/images/cropped/'
img_path = root_path + '/data/images/taxon_structured/taxon_train/'
test_path = root_path + '/data/images/taxon_structured/taxon_validate/'
data_path = root_path + '/data/observations/'
multiple_detections_id = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r']

# Image and dataset specification
img_size = 528
test_split = 0.15

# Taxonomic Info
taxonomy_list = ['taxon_family_name', 'taxon_genus_name', 'taxon_species_name', 'sub_species']

# Progress bar variables
count = 0
length = 0


def create_dataset(observations: list):
    global length
    df_obs = pd.DataFrame()

    for observation in observations:
        df_obs = pd.concat([df_obs, pd.read_csv(data_path + observation)])

    df_obs = df_obs.dropna(subset=['image_url'])

    df_obs = df_obs[df_obs['taxon_species_name'] != 'Felis catus']

    # Remove unnecessary columns
    df_obs = df_obs.drop(columns=['observed_on', 'local_time_observed_at', 'positional_accuracy'])
    length = len(df_obs)
    return df_obs


def sub_species_detection(x):
    name_count = len(x['scientific_name'].split())
    x['sub_species'] = np.nan
    if name_count >= 3:
        x['sub_species'] = x['scientific_name']
    return x


def taxonomic_analysis(df: pd.DataFrame):
    # Taxonomy breakdown
    taxonomy_list = ['taxon_family_name', 'taxon_genus_name', 'taxon_species_name', 'sub_species']
    taxon_breakdown = dict()

    # Identify each unique taxon level mammal
    for taxon in taxonomy_list:
        df = df.dropna(subset=[taxon])  # Remove all n/a labels
        taxon_breakdown[taxon] = df[taxon].unique().tolist()  # Find unique taxon level genus names
    return taxon_breakdown


def image_download(x):
    global count
    path = img_path
    set_decider = random.uniform(0, 1)
    if set_decider < test_split:
        path = test_path

    for level in taxonomy_list:
        taxon_level = x[level]

        if taxon_level is np.nan:
            break

        # Clean file path
        taxon_level = taxon_level.replace(" ", "_")
        taxon_level = taxon_level.lower()
        path = path + taxon_level + "/"

    multiple_obs(x['id'], path)

    count = count + 1
    status_bar_update()


def multiple_obs(id, path):
    for suffix in multiple_detections_id:
        raw_path = cropped_img_path + str(id) + '_' + suffix + '.jpg'
        if os.path.exists(raw_path):
            file_name = path + str(id) + '_' + suffix + '.jpg'
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            shutil.copy(raw_path, file_name)
        else:
            break


def status_bar_update():
    progress_bar_length = 50
    percentage_complete = count / length
    filled = int(progress_bar_length * percentage_complete)

    bar = '=' * filled + '-' * (progress_bar_length - filled)
    percentage_display = round(100 * percentage_complete, 5)
    sys.stdout.write('\r[%s] %s%s ... count: %s' % (bar, percentage_display, '%', count))
    sys.stdout.flush()


if __name__ == "__main__":
    observations = ['proboscidia_train.csv']
    df = create_dataset(observations)

    # Generate sub_species
    df = df.apply(lambda x: sub_species_detection(x), axis=1)

    taxon_breakdown = taxonomic_analysis(df.copy())

    df.apply(lambda x: image_download(x), axis=1)
