import schedule
import time

from logger_config import configure_logger
from features.data_collection import collect_workout_data, fetch_exercise_data, filter_exercise_data

# Configure logging for the scheduler
scheduler_logger = configure_logger(name='scheduler')


def data_ingestion_job():
    scheduler_logger.info("Running data ingestion job...")

    workout_data = collect_workout_data(input_path='./data/workouts', output_path='./data/current')
    if workout_data.empty:
        scheduler_logger.error("No workout data was collected.")
        return

    exercise_data = fetch_exercise_data(file_path='./data/kaggle/megaGymDataset.csv')
    if exercise_data.empty:
        scheduler_logger.error("No exercise data was fetched.")
        return

    filtered_exercise_data = filter_exercise_data(workout_data=workout_data, exercises=exercise_data, output_path='./data/current')
    if filtered_exercise_data.empty:
        scheduler_logger.error("No exercise data was filtered.")
        return

    scheduler_logger.info("Data ingestion job complete.")
    return


# Schedule the job to run every Monday at 00:00
schedule.every().monday.at("00:00").do(data_ingestion_job)

# Temporarily schedule the job to run every 10 seconds for testing purposes
schedule.every(10).seconds.do(data_ingestion_job)

# Main loop to continuously check for scheduled jobs
while True:
    schedule.run_pending()
    #time.sleep(60)  # Sleep for 60 seconds before checking again
