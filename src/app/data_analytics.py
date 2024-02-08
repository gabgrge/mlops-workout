import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import os


def plot_predictions(exo, models_path, data_path, n_weeks=26):
    """
    Plot the predictions for a specific exercise.
    """
    # Load performance data
    perf = pd.read_csv(os.path.join(data_path, "current/workout_perf.csv"))

    # Filter the performance data for the specific exercise
    df_exo = perf[perf["EXERCISE"] == exo].reset_index(drop=True)

    # Format the DATE column to the number of days since the beginning of the exercises
    df_exo['DATE'] = pd.to_datetime(df_exo['DATE'])
    min_date = df_exo['DATE'].min()
    df_exo['DATE'] = (df_exo['DATE'] - df_exo['DATE'].min()) / np.timedelta64(1, 'D')

    # Normalize columns for the LSTM model
    scaler = MinMaxScaler(feature_range=(0, 1))
    df_exo['PERF'] = scaler.fit_transform(df_exo[['PERF']])
    df_exo['DATE'] = scaler.fit_transform(df_exo[['DATE']])

    # Load exercise model
    model = tf.keras.models.load_model(f'{models_path}/current/{exo}.keras')

    # Create a dataframe with the predictions
    predictions = pd.DataFrame(columns=["DATE", "PERF"])

    # Define a future date
    future_date = scaler.inverse_transform(df_exo[['DATE']]).max()

    # Make predictions for the next n_weeks weeks
    for i in range(n_weeks):
        future_date_scaled = scaler.transform([[future_date]])
        future_date_scaled = np.array([[future_date_scaled]])
        future_date_scaled = future_date_scaled.reshape((future_date_scaled.shape[0], 1, future_date_scaled.shape[1]))
        future_perf = model.predict(future_date_scaled)
        future_perf = scaler.inverse_transform(future_perf)
        new_row = pd.DataFrame({"DATE": [future_date], "PERF": [future_perf[0][0]]})
        predictions = pd.concat([predictions, new_row], ignore_index=True)
        future_date = future_date + 7

    df_exo['DATE'] = scaler.inverse_transform(df_exo[['DATE']])
    df_exo['DATE'] = pd.to_timedelta(df_exo['DATE'], unit='D') + min_date

    df_exo['PERF'] = scaler.inverse_transform(df_exo[['PERF']])

    predictions['DATE'] = pd.to_timedelta(predictions['DATE'], unit='D') + min_date

    # Plot the actual data and the predictions
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_exo['DATE'], y=df_exo['PERF'], mode='lines', name='Actual data'))
    fig.add_trace(go.Scatter(x=predictions['DATE'], y=predictions['PERF'], mode='lines', name='Predictions',
                             line=dict(color='red')))
    fig.update_layout(title=f"Actual data and predictions for {exo}")
    fig.show()
    print(df_exo)
    print(predictions)
