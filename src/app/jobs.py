from src.app.logger_config import configure_logger
from src.app.data_collection import (collect_workout_data, fetch_exercise_data, filter_exercise_data,
                                     enrich_workout_data, aggregate_workout_data)

# Configure logging for the scheduler
scheduler_logger = configure_logger(name='scheduler')


def data_ingestion_job():
    scheduler_logger.info("Running data ingestion job...")

    workout_data = collect_workout_data(input_path='./data/workouts',
                                        output_path='./data/current')
    if workout_data.empty:
        scheduler_logger.error("No workout data was collected.")
        return

    exercise_data = fetch_exercise_data(file_path='./data/kaggle/megaGymDataset.csv')
    if exercise_data.empty:
        scheduler_logger.error("No exercise data was fetched.")
        return

    filtered_exercise_data = filter_exercise_data(workout_data=workout_data,
                                                  exercises=exercise_data,
                                                  output_path='./data/current')
    if filtered_exercise_data.empty:
        scheduler_logger.error("No exercise data was filtered.")
        return

    enriched_workout_data = enrich_workout_data(workout_data=workout_data,
                                                filtered_exercises=filtered_exercise_data,
                                                output_path='./data/current')
    if enriched_workout_data.empty:
        scheduler_logger.error("No workout data was enriched.")
        return

    workout_day_exercises, workout_days = aggregate_workout_data(enriched_workouts=enriched_workout_data,
                                                                 output_path='./data/current')
    if workout_day_exercises.empty and workout_days.empty:
        scheduler_logger.error("No workout data was aggregated.")
        return

    scheduler_logger.info("Data ingestion job complete.")
    return