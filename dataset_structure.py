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
    """This method creates a DataFrame from the specified observations list.

    Note, multiple dataset files can be specified and the taxonomic structure will remain correct.
    The method removes any Null values from the image_urls, removes the erroneous Felis Catus species,
    and drops unnecessary columns.

    Returns:
        (DataFrame): A dataframe of the specified observations file aggregated together.
    """
    global length
    df_obs = pd.DataFrame()

    for observation in observations:
        df_obs = pd.concat([df_obs, pd.read_csv(data_path + observation)])  # Concatenate multiple observations into one dataframe

    df_obs = df_obs.dropna(subset=['image_url'])
    df_obs = df_obs[df_obs['taxon_species_name'] != 'Felis catus']
    df_obs = df_obs.drop(columns=['observed_on', 'local_time_observed_at', 'positional_accuracy'])  # Remove unnecessary columns

    length = len(df_obs)  # Instantiate length value
    return df_obs


def sub_species_detection(x):
    """This method performs subspecies detection based on the information available in the scientific name column.

    This method identifies a subspecies name by definition as containing three distinct words making up the scientific name (unique to subspecies)
    This method is used in conjunction with the `DataFrame.apply()` method and the lambda expression.

    Args:
        x (Row): The row of the dataframe representing a single observation.

    Returns:
        (Row): The same row augmented to include an additional column titled sub_species.
    """
    name_count = len(x['scientific_name'].split())
    x['sub_species'] = np.nan
    if name_count >= 3:
        x['sub_species'] = x['scientific_name']
    return x


def taxonomic_analysis(df: pd.DataFrame):
    """This method performs a taxonomic analysis, whereby it identifies each unique label at the specified taxonomic levels.

    This method in this cause can be used to visualize the potential unique taxonomic labels, but is not required in the taxon directory process.
    Args:
        df (DataFrame): The dataframe containing all observations.

    Returns:
        (dict): A dictionary whereby the keys are the specified taxon levels, and the values are a list of unique taxon labels at each level.
    """
    taxonomy_list = ['taxon_family_name', 'taxon_genus_name', 'taxon_species_name', 'sub_species']  # Specify taxonomic levels at which the analysis should occur
    taxon_breakdown = dict()  # Dictionary to contain unique values per level.

    for taxon in taxonomy_list:  # For each taxonomic level
        df = df.dropna(subset=[taxon])  # Remove all n/a labels
        taxon_breakdown[taxon] = df[taxon].unique().tolist()  # Find unique taxon level genus names
    return taxon_breakdown


def image_access(x):
    """This method creates the taxonomic path based on the specified taxonomic levels. The resulting path indicates
     where in the taxon directory the image will be stored.

     Additionally, this method splits the images into training and validation datasets.
     This method is used in conjunction with the `DataFrame.apply()` method and the lambda expression.
     This method updates the status bar upon saving the sub-image into the correct directory.

     Args:
         x (Row): The row of the dataframe representing a single observation.
     """
    global count
    path = img_path  # Path is set to the training set by default
    set_decider = random.uniform(0, 1)  # Generate a random uniform value
    if set_decider < test_split:  # If the probability is less that the test_split the image is sent to the validation set instead.
        path = test_path

    for level in taxonomy_list:  # Iterate down the taxonomic levels
        taxon_level = x[level]  # This is the taxon label at this level

        if taxon_level is np.nan:  # If the taxon level is null, then there exist no further labels below. This is the final path
            break

        taxon_level = taxon_level.replace(" ", "_")  # Clean file path (lowercase and no spaces)
        taxon_level = taxon_level.lower()
        path = path + taxon_level + "/"

    multiple_obs(x['id'], path)  # Account for multiple observations at the same file path.

    count = count + 1  # Increase the completed observation count
    status_bar_update()  # Update the status bar


def multiple_obs(id, path):
    """This method searches for multiple sub-images per observation in order to place them at the same file path within the taxonomic directories.

    This method copies the images from the `images/cropped/` directory to the target file path specified.

    Args:
        id (int): The unique observation id.
        path (str): The path to the correct taxon directory within the taxonomic directory structure. This path should be the same for all sub-images of an observation.
    """
    for suffix in multiple_detections_id:  # Iterate through the possible sub-image suffixes
        raw_path = cropped_img_path + str(id) + '_' + suffix + '.jpg'  # Create a path with that suffix which could already exist within the cropped images directory
        if os.path.exists(raw_path):  # Path exists so copy file to destination path
            file_name = path + str(id) + '_' + suffix + '.jpg'
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            shutil.copy(raw_path, file_name)
        else:  # No file exists, stop searching for further sub-images
            break


def status_bar_update():
    """This method updates the visual status bar to represent the status of the image download.
    """
    progress_bar_length = 50
    percentage_complete = count / length
    filled = int(progress_bar_length * percentage_complete)  # Calculate the percentage of the bar completed.

    bar = '=' * filled + '-' * (progress_bar_length - filled)
    percentage_display = round(100 * percentage_complete, 5)  # Round percentage complete to 5 decimals for display
    sys.stdout.write('\r[%s] %s%s ... count: %s' % (bar, percentage_display, '%', count))
    sys.stdout.flush()


if __name__ == "__main__":
    observations = ['proboscidia_train.csv']  # Specify the datasets to convert into taxonomic directories.
    df = create_dataset(observations)  # Create the dataset
    df = df.apply(lambda x: sub_species_detection(x), axis=1)  # Generate sub_species

    df.apply(lambda x: image_access(x), axis=1)  # Perform the taxon directory construction
