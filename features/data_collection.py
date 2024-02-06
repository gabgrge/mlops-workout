import pandas as pd
import os
import re

from logger_config import configure_logger

# Configure logging for the data collection
data_collection_logger = configure_logger(name='data_collection')


def collect_workout_data(input_path: str, output_path: str) -> pd.DataFrame:
    try:
        data_collection_logger.info("Collecting workout data...")

        # Get a list of all workout files in the data/workout directory
        csv_files = sorted(f for f in os.listdir(input_path) if re.match(r'workout_\d{4}-\d{2}-\d{2}.csv', f))

        # Initialize an empty list to hold the dataframes
        dfs = []

        # Loop through the files
        for csv_file in csv_files:
            # Read each file into a DataFrame and append it to the list
            df = pd.read_csv(f"{input_path}/{csv_file}")
            if not df.empty:
                dfs.append(df)

        # Concatenate all the dataframes in the list into a single dataframe
        workout_data = pd.concat(dfs, ignore_index=True)

        # Save the workout data to current directory
        workout_data.to_csv(f"{output_path}/workout_data.csv", index=False, header=True)

        data_collection_logger.info("Workout data collected.")
        return workout_data

    except Exception as e:
        data_collection_logger.error(f"An error occurred during data ingestion: {e}")
        return pd.DataFrame()


def fetch_exercise_data(file_path: str) -> pd.DataFrame:
    try:
        data_collection_logger.info("Fetching exercise data...")

        # Read the exercise data
        exercises = pd.read_csv(file_path, header=0, index_col=0)

        data_collection_logger.info("Exercise data fetched.")
        return exercises

    except Exception as e:
        data_collection_logger.error(f"An error occurred fetching exercise data: {e}")
        return pd.DataFrame()


def filter_exercise_data(workout_data: pd.DataFrame, exercises: pd.DataFrame, output_path: str) -> pd.DataFrame:
    try:
        data_collection_logger.info("Filtering exercise data...")

        # Filter the exercise data to only include exercises that are in the workout data
        filtered_exercises = exercises[exercises['Title'].isin(workout_data['EXERCISE'].unique())] \
            .drop_duplicates(ignore_index=True)

        # Save the filtered exercise data to current directory
        filtered_exercises.to_csv(f"{output_path}/workout_exercises.csv", index=False, header=True)

        data_collection_logger.info("Exercise data filtered.")
        return filtered_exercises

    except Exception as e:
        data_collection_logger.error(f"An error occurred filtering exercise data: {e}")
        return pd.DataFrame()
