import pandas as pd
import numpy as np
import tensorflow as tf
import os
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Bidirectional, Dropout, Flatten
from sklearn.preprocessing import MinMaxScaler
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt

from .logger_config import configure_logger

models_training_logger = configure_logger(name="models_training")


def load_and_preprocess_data(min_exo_occurrence: int, data_path: str) -> Tuple[List[str], pd.DataFrame]:
    """
    Load and preprocess data.
    """
    try:
        models_training_logger.info("Loading and preprocessing data...")

        # Load data
        df = pd.read_csv(data_path)

        # Metric to predict
        df['PERF'] = df['NB_REPS'] * df['WEIGHT']

        # Remove sets greater than 3
        df = df.drop(df[df['SET'] > 3].index)

        # Remove exercises with less than 3 sets
        df = df[df.groupby(["DATE", "EXERCISE"])['SET'].transform('count') >= 3].reset_index(drop=True)

        # Average performance per exercise per day
        perf = df.groupby(["DATE", "EXERCISE"]).mean("PERF").reset_index()

        # Create a list with the exercises that have more than 10 values
        p = perf.groupby("EXERCISE").count().sort_values("DATE", ascending=False).reset_index()
        exos = p[p["DATE"] > min_exo_occurrence]["EXERCISE"].to_list()

        models_training_logger.info("Data loaded and preprocessed.")
        return exos, perf

    except Exception as e:
        models_training_logger.error(f"Error occurred while loading data or preprocessing: {e}")
        return [], pd.DataFrame()


def train_model(exo: str, perf: pd.DataFrame, models_dir: str) -> Optional[tf.keras.callbacks.History]:
    """
    Train a model for a specific exercise.
    """
    try:
        models_training_logger.info(f"Training model for exercise '{exo}'...")

        # We try to predict the performances for a specific exercise
        df_exo = perf[perf["EXERCISE"] == exo].reset_index(drop=True)

        # We format the DATE column to the number of days since the beginning of the exercises
        df_exo['DATE'] = pd.to_datetime(df_exo['DATE'])
        df_exo['DATE'] = (df_exo['DATE'] - df_exo['DATE'].min()) / np.timedelta64(1, 'D')

        # Normalize our columns for the LSTM model
        scaler = MinMaxScaler(feature_range=(0, 1))
        df_exo['PERF'] = scaler.fit_transform(df_exo[['PERF']])
        df_exo['DATE'] = scaler.fit_transform(df_exo[['DATE']])

        # Let's split our train - test data by 80% - 20%
        split_point = int(len(df_exo) * 0.8)

        train = df_exo.iloc[:split_point]
        test = df_exo.iloc[split_point:]

        # Prepare data for LSTM
        X_train = train['DATE'].values
        y_train = train['PERF'].values

        X_test = test['DATE'].values
        y_test = test['PERF'].values

        X_train = X_train.reshape(-1, 1, 1)
        X_test = X_test.reshape(-1, 1, 1)

        # Clear session
        tf.keras.backend.clear_session()

        # Define LSTM model
        model = Sequential()
        model.add(Bidirectional(LSTM(200, return_sequences=True), input_shape=(X_train.shape[1], X_train.shape[2])))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(150, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(100, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(50, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Flatten())
        model.add(Dense(1))

        # Define the loss and optimizer
        model.compile(loss='mse', optimizer='adam')

        # Save the best model based on the validation loss
        best_model = tf.keras.callbacks.ModelCheckpoint(
            filepath=f'{models_dir}/current/{exo}.keras',
            monitor='val_loss',  # Monitor other things like val_accuracy or accuracy
            save_best_only=True,  # Make sure to save only the best model
            verbose=0
        )

        # Fit model
        history = model.fit(
            X_train, y_train,
            validation_data=[X_test, y_test],
            epochs=20,
            batch_size=5,
            callbacks=[best_model],
            verbose=0,
            shuffle=False
        )

        models_training_logger.info(f"Model for exercise '{exo}' trained.")
        return history

    except Exception as e:
        models_training_logger.error(f"Error occurred while training model '{exo}': {e}")
        return None


def plot_loss(exo: str, history: tf.keras.callbacks.History, models_dir: str) -> bool:
    """
    Plot the loss.
    """
    try:
        models_training_logger.info("Plotting loss...")

        # Plot the loss
        plt.plot(history.history['loss'], label='train')
        plt.plot(history.history['val_loss'], label='test')
        plt.legend()
        plt.savefig(f"{models_dir}/loss/{exo}.png")
        plt.close()

        models_training_logger.info("Loss plotted.")
        return True

    except Exception as e:
        models_training_logger.error(f"Error occurred while plotting loss: {e}")
        return False


def train_models(max_models: Optional[int], min_exo_occurrence: int, data_path: str, models_dir: str) -> bool:
    """
    Train models for each exercise.
    """
    try:
        models_training_logger.info("Training models...")

        # Load and preprocess data
        exos, perf = load_and_preprocess_data(min_exo_occurrence=min_exo_occurrence, data_path=data_path)
        if perf.empty:
            return False
        if not exos:
            models_training_logger.error("No exercises to train models for.")
            return False

        if max_models is not None:
            # Limit the number of models to train (for testing)
            exos = exos[:max_models]

        for exo in exos:
            # Train model
            history = train_model(exo=exo, perf=perf, models_dir=models_dir)
            if history is None:
                return False

            # Plot loss
            loss_plotted = plot_loss(exo=exo, history=history, models_dir=models_dir)
            if not loss_plotted:
                return False

            # Get the epoch with the best validation loss
            best_epoch = np.argmin(history.history['val_loss'])

            # Get the loss and validation loss of the best epoch
            best_loss = history.history['loss'][best_epoch]
            best_val_loss = history.history['val_loss'][best_epoch]

            # Log the loss and val_loss of the best epoch
            models_training_logger.info(f"Best Model '{exo}': epoch = {best_epoch + 1}, loss = {best_loss}, val_loss = {best_val_loss}")

        models_training_logger.info("Models trained.")
        return True

    except Exception as e:
        models_training_logger.error(f"Error occurred while training models: {e}")
        return False


def archive_models(models_dir: str) -> bool:
    """
    Archive models for versioning.
    """
    try:
        models_training_logger.info("Archiving models...")

        # Get the relative path to models_dir
        models_dir = os.path.relpath(models_dir, start=os.getcwd())

        # Archive models
        os.system(f"tar -czf {models_dir}/versions/models_{datetime.now().strftime('%Y-%m-%d')}.tar.gz -C {models_dir}/current .")

        models_training_logger.info(f"Models archived to : {models_dir}/versions/models_{datetime.now().strftime('%Y-%m-%d')}.tar.gz")
        return True

    except Exception as e:
        models_training_logger.error(f"Error occurred while archiving models: {e}")
        return False
