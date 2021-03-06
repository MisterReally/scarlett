import os
import json
import time
from datetime import datetime
import pandas as pd
from Storage import Store
# consider combining fileoperations into one class


class FileReader:
    # file read operations
    def __init__(self):
        self.store = Store()

    def load_json(self, filename):
        # loads json file as dictionary data
        with open(filename, 'r') as file:
            return json.load(file)

    def load_csv(self, filename):
        # loads csv file as Dataframe
        one_day = 60 * 60 * 24
        now = datetime.fromtimestamp(time.time())
        file_exists = os.path.exists(filename)

        if file_exists:
            then = datetime.fromtimestamp(os.path.getmtime(filename))
            delta = now - then
            last_modified = delta.total_seconds()
        try:
            if not file_exists or last_modified > one_day:
                self.store.download_file(filename)
            df = pd.read_csv(filename).round(10)
        except pd.errors.EmptyDataError:
            print(f'{filename} is an empty csv file.')
            raise
        except FileNotFoundError:
            print(f'{filename} does not exist locally.')
            raise
        except Exception:
            df = pd.DataFrame()
        return df

    def check_update(self, filename, df):
        # given a csv filename and dataframe
        # return whether the csv needs to be updated
        return len(df) >= len(self.load_csv(filename))

    def update_df(self, filename, new, column):
        old = self.load_csv(filename)
        if not old.empty:
            old = old[~old[column].isin(new[column])]
            new = old.append(new, ignore_index=True)
        return new

    def check_file_exists(self, filename):
        return os.path.exists(filename) and self.store.key_exists(filename)


class FileWriter:
    # file write operations
    def __init__(self):
        self.store = Store()

    def save_json(self, filename, data):
        # saves data as json file with provided filename
        self.store.finder.make_path(filename)
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    def save_csv(self, filename, data):
        # saves df as csv file with provided filename
        if data.empty:
            return False
        else:
            self.store.finder.make_path(filename)
            with open(filename, 'w') as f:
                data.to_csv(f, index=False)
            self.store.upload_file(filename)
            return True

    def update_csv(self, filename, df):
        # update csv if needed
        if FileReader().check_update(filename, df):
            self.save_csv(filename, df)

    def remove_files(self, filenames):
        [os.remove(file) for file in filenames]
        self.store.delete_objects(filenames)

    def rename_file(self, old_name, new_name):
        os.rename(old_name, new_name)
        self.store.rename_key(old_name, new_name)

# add function that takes in a Constants directory, old to new column mapping
# and renames the cols using df.rename(columns=mapping) for all csvs in the dir


# FileReader().get_all_paths('.')
