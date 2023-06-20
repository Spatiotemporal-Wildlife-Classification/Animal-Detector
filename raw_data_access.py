"""This file serves to access and download the observation images from the provided URL of each observation.

    This file saves the downloaded JPG images to the `data/images/raw` directory for further processing.
    The observations are sourced from the directory `data/observations`.
    Each image is saved in the following format <Observation ID>.jpg

    Attributes:
        root_path (str): The absolute path to the root of the project directory.
        csv_path (str): The complete path (absolute + relative) to the observation data in `data/observations/`
        raw_image_path (str): The save location of the downloaded images. The directory is `data/images/raw/`
        length (int): This value represents the quantity of observations in the dataset. Used in the calculation of the progress bar.
        count (int): This value represents the total images downloaded. Used in the calculation of the progress bar.
"""
import os.path
import sys
import pandas as pd
import requests

# Paths
root_path = sys.path[1]
csv_path = root_path + '/data/raw_csv/'
raw_image_path = root_path + '/data/images/raw/'

# Progress bar variables
length = 0
count = 0


def create_dataset(observations: str) -> pd.DataFrame:
    """This method created the DataFrame of the dataset and pre-processes it for image extraction.]

    Args:
        observations (str): The name of the CSV file to convert into a DataFrame and pre-process for image extraction.

    Returns:
        (DataFrame): The pre-processed DataFrame containing observations ready for image extraction.
    """
    global length

    df_obs = pd.read_csv(csv_path + observations)
    df_obs = df_obs.dropna(subset=['image_url'])  # Remove null image url values if any remain
    df_obs = df_obs[df_obs['taxon_species_name'] != 'Felis catus']  # Remove erroneous species
    df_obs = df_obs.drop(columns=['observed_on', 'local_time_observed_at', 'positional_accuracy'])  # Remove uneccessary columns

    length = len(df_obs)  # Initialize length of the dataset
    return df_obs


def image_download(x):
    """This method extracts the URL from an observation, and downloads the image.

    This method is used in conjunction with the DataFrame.apply method within a lambda expression.
    This method saves the image in the following format: <Observation ID>.jpg to the `images/raw` save path.
    Each image downloaded increases the global count variable to update the status bar.

    Args:
        x (row): The row of the dataframe.
    """
    global count
    file_name = raw_image_path + str(x['id']) + '.jpg'

    if not os.path.exists(file_name):  # If the file doesn't exist to avoid repeated downloads
        try:
            img_data = requests.get(x['image_url'], timeout=3).content
            with open(file_name, 'wb') as f:
                f.write(img_data)
        except:
            print('Error in retrieving image: ', x['id'])

    count = count + 1  # Update the global count
    status_bar_update()  # Update the status bar


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


if __name__ == '__main__':
    """Please specify the `observation.csv` file you wish to extract images for."""

    observations = 'proboscidia_train.csv'
    df = create_dataset(observations)  # Create the DataFrame to be used
    df.apply(lambda x: image_download(x), axis=1)  # Extract the images
