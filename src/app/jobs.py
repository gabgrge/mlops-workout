import os

from .logger_config import configure_logger
from .data_collection import (collect_workout_data, fetch_exercise_data, filter_exercise_data,
                              enrich_workout_data, aggregate_workout_data)
from .models_training import train_models, archive_models

# Configure logging for the scheduler
scheduler_logger = configure_logger(name='scheduler')

# Path to the data directory
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')

# Path to the models directory
models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'models')


def data_ingestion_job():
    scheduler_logger.info("Running data ingestion job...")

    workout_data = collect_workout_data(input_path=os.path.join(data_dir, 'workouts'),
                                        output_path=os.path.join(data_dir, 'current'))
    if workout_data.empty:
        scheduler_logger.error("No workout data was collected.")
        return

    exercise_data = fetch_exercise_data(file_path=os.path.join(data_dir, 'kaggle/megaGymDataset.csv'))
    if exercise_data.empty:
        scheduler_logger.error("No exercise data was fetched.")
        return

    filtered_exercise_data = filter_exercise_data(workout_data=workout_data,
                                                  exercises=exercise_data,
                                                  output_path=os.path.join(data_dir, 'current'))
    if filtered_exercise_data.empty:
        scheduler_logger.error("No exercise data was filtered.")
        return

    enriched_workout_data = enrich_workout_data(workout_data=workout_data,
                                                filtered_exercises=filtered_exercise_data,
                                                output_path=os.path.join(data_dir, 'current'))
    if enriched_workout_data.empty:
        scheduler_logger.error("No workout data was enriched.")
        return

    workout_day_exercises, workout_days = aggregate_workout_data(enriched_workouts=enriched_workout_data,
                                                                 output_path=os.path.join(data_dir, 'current'))
    if workout_day_exercises.empty and workout_days.empty:
        scheduler_logger.error("No workout data was aggregated.")
        return

    scheduler_logger.info("Data ingestion job complete.")
    return


def model_training_job(max_models=None):
    scheduler_logger.info("Running model training job...")

    models_trained = train_models(max_models=max_models,
                                  min_exo_occurrence=10,
                                  data_path=os.path.join(data_dir, 'current/workout_data.csv'),
                                  models_dir=models_dir)
    if not models_trained:
        scheduler_logger.error("Models were not trained.")
        return

    models_archived = archive_models(models_dir=models_dir)
    if not models_archived:
        scheduler_logger.error("Models were not archived.")
        return

    scheduler_logger.info("Model training job complete.")
    return


def data_pipeline_stage():
    data_ingestion_job()
    model_training_job()
    return
