import pandas as pd
import numpy as np

from src.app.logger_config import configure_logger

# Configure logging for the data loading
data_loading_logger = configure_logger(name='data_loading')


def load_workout_data(file_path: str) -> list:
    try:
        data_loading_logger.info("Loading workout data...")

        # Read the workout data and replace NaN with empty strings
        workout_data = (pd.read_csv(file_path, header=0)).replace({np.nan: ""})

        # Convert the workout data to a list of dictionaries
        workout_data = workout_data.to_dict(orient='records')

        data_loading_logger.info("Workout data loaded.")
        return workout_data

    except Exception as e:
        data_loading_logger.error(f"An error occurred loading workout data: {e}")
        return list()


def load_filtered_exercise_data(file_path: str) -> list:
    try:
        data_loading_logger.info("Loading filtered exercise data...")

        # Read the filtered exercise data drop column "RatingDesc" and replace NaN with empty strings
        filtered_exercise_data = pd.read_csv(file_path, header=0).drop(columns=["RatingDesc"]).replace({np.nan: ""})

        # Convert the filtered exercise data to a list of dictionaries
        filtered_exercise_data = filtered_exercise_data.to_dict(orient='records')

        data_loading_logger.info("Filtered exercise data loaded.")
        return filtered_exercise_data

    except Exception as e:
        data_loading_logger.error(f"An error occurred loading filtered exercise data: {e}")
        return list()
