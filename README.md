# Project Documentation

## Original Data

The original data for this project is stored in two main files:

- `data/workouts/workout_YYYY-MM-DD.csv`: The `workouts` directory contains workout data files. Each file contains the workout data for a specific week. The data includes the date, workout type, exercise, muscle group, set number, number of repetitions, and weight lifted. (Source: my own workout data)

- `data/kaggle/megaGymDataset.csv`: This file contains a comprehensive list of exercises with their descriptions, types, targeted body parts, equipment used, difficulty level, and ratings. (Source: [Kaggle](https://www.kaggle.com/datasets/niharika41298/gym-exercise-data))

## Data Pipeline

The data pipeline for this project consists of several stages:

1. **Data Collection**: The `data_collection.py` script collects workout data from the original data files. It includes functions to collect workout data, fetch exercise data, filter exercise data, enrich workout data, and aggregate workout data. The collected data is saved in the `data/current` directory.

2. **Data Preprocessing**: The `models_training.py` script preprocesses the collected data to prepare it for model training.

3. **Model Training & Versioning**: The `models_training.py` script also trains models for each exercise and saves them in the `models` directory. The models are versioned by saving them in a `current` subdirectory and archiving old models in a `versions` subdirectory *(unversioned for size purposes)*. It also plots the loss of the models and saves the plots in the `loss` subdirectory.

4. **Data Analysis**: The `data_analytics.py` script performs data analysis on the workout data and model predictions. It includes functions to plot predicted volume, plot distribution of muscle groups, plot distribution of workout types, and plot weight and repetitions over time. The plots are saved as HTML files in the `static/plots` directory.

All these steps are defined in the `jobs.py` script, which sets up the data pipeline stage.

## Model

The model used in this project is a Long Short-Term Memory (LSTM) model, which is a type of Recurrent Neural Network (RNN). LSTM models are particularly good at processing sequences of data, making them well-suited for time-series data like our workout data.

The model takes as input a sequence of workout data and outputs a prediction for the volume of the next workouts. The volume is calculated as the product of the number of sets, the number of repetitions per set, and the weight lifted.

The model's performance is evaluated using the Mean Squared Error (MSE) loss function. 

## App

The project includes a web app that allows users to view workout data, exercise data, and analytics. The app is defined in the `app.py` script and uses Flask as the web framework.

- `/`: The home page.
- `/workouts`: The workouts page contains a table with the workout data.
- `/my-exercises`: The exercises page contains a table with the filtered exercise data.
- `/analytics`: The analytics page contains plots of the workout data and model predictions.

The data loading process for the app is defined in the `data_loading.py` script. It includes functions to load workout data and load filtered exercise data.

## Logging

Logging is configured in the `logger_config.py` script. Each script in the project has its own logger, which is configured to log messages to a file in the `logs` directory. The log messages include the timestamp, log level, and the name of the script that generated the log message. The log messages are also printed to the console.

## Run

To run the project, you can use the `run.py` script. This script runs the app and the data pipeline in sequence. The data pipeline is scheduled to run every monday at 12:00 AM.

```bash
python src/run.py
```

## Testing

The project includes several types of tests:

- **Unit Tests**: The `test_data_collection.py` and `test_data_loading.py` scripts include unit tests for some data collection and data loading functionalities respectively.

- **Integration Tests**: The `test_app.py` script includes integration tests for the app and for the data ingestion and model training jobs of the data pipeline.

- **End-to-End Test**: The `test_end_to_end.py` script includes an end-to-end test that tests the entire app and data pipeline.

## Deployment

The project uses Docker for deployment. The `Dockerfile` defines the Docker image for the project, which uses Python 3.10 as the base image and runs the `src/run.py` script when the container is launched.

## CI/CD Pipeline & Automation

The project also uses GitHub Actions for automation and CI/CD. The `ci-cd.yml` workflow defines the CI/CD pipeline, which runs the tests, builds the Docker image, versions it and pushes it to Docker Hub. Finally, it creates a pull request to merge the changes to the main branch if the pipeline passes. The `automerge.yml` workflow, which defines the automerge action, automatically merges pull requests that pass the CI/CD pipeline.