import pandas as pd
import numpy as np
import os
import re

from src.app.logger_config import configure_logger

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


def enrich_workout_data(workout_data: pd.DataFrame, filtered_exercises: pd.DataFrame, output_path: str) -> pd.DataFrame:
    try:
        data_collection_logger.info("Enriching workout data...")

        # Merge the workout data with the filtered exercise data
        enriched_workouts = pd.merge(workout_data, filtered_exercises, how='left', left_on='EXERCISE', right_on='Title')

        # Drop unnecessary columns
        enriched_workouts = enriched_workouts.drop(columns=['Title', 'Desc', 'RatingDesc'])

        # Save the enriched workout data to current directory
        enriched_workouts.to_csv(f"{output_path}/enriched_workout_data.csv", index=False, header=True)

        data_collection_logger.info("Workout data enriched.")
        return enriched_workouts

    except Exception as e:
        data_collection_logger.error(f"An error occurred enriching workout data: {e}")
        return pd.DataFrame()


def aggregate_workout_data(enriched_workouts: pd.DataFrame, output_path: str) -> [pd.DataFrame, pd.DataFrame]:
    try:
        data_collection_logger.info("Aggregating workout data...")

        # Aggregate the enriched workout data by date, workout, and exercise
        workout_day_exercises = enriched_workouts \
            .groupby(["DATE", "WORKOUT", "EXERCISE"], sort=False) \
            .agg(Type=("Type", "first"),
                 BodyPart=("BodyPart", "first"),
                 Equipment=("Equipment", "first"),
                 Level=("Level", "first"),
                 Rating=("Rating", "first"),
                 NB_SETS=("SET", len),
                 AVERAGE_REPS=("NB_REPS", "mean"),
                 AVERAGE_WEIGHT=("WEIGHT", lambda x: np.average(x, weights=enriched_workouts.loc[x.index, "NB_REPS"])),
                 MAX_WEIGHT=("WEIGHT", "max")) \
            .reset_index()

        # Aggregate the enriched workout data by date and workout
        workout_days = workout_day_exercises \
            .groupby(["DATE", "WORKOUT"], sort=False) \
            .agg(NB_EXERCISES=("EXERCISE", len),
                 NB_SETS=("NB_SETS", "sum")) \
            .reset_index()

        # Save the aggregated workout data to current directory
        workout_day_exercises.to_csv(f"{output_path}/workout_day_exercises.csv", index=False, header=True)
        workout_days.to_csv(f"{output_path}/workout_days.csv", index=False, header=True)

        data_collection_logger.info("Workout data aggregated.")
        return workout_day_exercises, workout_days

    except Exception as e:
        data_collection_logger.error(f"An error occurred aggregating workout data: {e}")
        return pd.DataFrame(), pd.DataFrame()
