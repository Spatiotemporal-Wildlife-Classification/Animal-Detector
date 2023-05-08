import os.path
import sys
import pandas as pd

import requests

root_path = sys.path[1]
csv_path = root_path + '/data/raw_csv/'
raw_image_path = root_path + '/data/images/raw/'

length = 0
count = 0


def create_dataset(observations: str):
    global length

    df_obs = pd.read_csv(csv_path + observations)
    df_obs = df_obs.dropna(subset=['image_url'])
    df_obs = df_obs[df_obs['taxon_species_name'] != 'Felis catus']
    df_obs = df_obs.drop(columns=['observed_on', 'local_time_observed_at', 'positional_accuracy'])
    length = len(df_obs)
    return df_obs


def image_download(x):
    global count
    file_name = raw_image_path + str(x['id']) + '.jpg'
    if not os.path.exists(file_name):
        try:
            img_data = requests.get(x['image_url'], timeout=3).content
            with open(file_name, 'wb') as f:
                f.write(img_data)
        except:
            print('Error in retrieving image: ', x['id'])
    count = count + 1
    status_bar_update()


def status_bar_update():
    progress_bar_length = 50
    percentage_complete = count / length
    filled = int(progress_bar_length * percentage_complete)

    bar = '=' * filled + '-' * (progress_bar_length - filled)
    percentage_display = round(100 * percentage_complete, 5)
    sys.stdout.write('\r[%s] %s%s ... count: %s' % (bar, percentage_display, '%', count))
    sys.stdout.flush()


if __name__ == '__main__':
    observations = 'proboscidia_final.csv'
    df = create_dataset(observations)

    df.head(12000).apply(lambda x: image_download(x), axis=1)
