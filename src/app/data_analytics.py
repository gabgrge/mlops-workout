import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import os
import warnings

from .logger_config import configure_logger

data_analytics_logger = configure_logger(name="data_analytics")


def plot_predicted_volume(models_path: str, data_path: str, static_path: str, n_weeks: int) -> bool:
    """
    Plot the predicted volume for each exercise.
    """
    try:
        data_analytics_logger.info(f"Plotting predicted volume for each exercise...")

        # Disable warnings
        warnings.filterwarnings('ignore')

        # Load performance data
        perf = pd.read_csv(os.path.join(data_path, "current/workout_perf.csv"), header=0)

        # Get the list of models
        models = os.listdir(f"{models_path}/current")

        # Get the list of exercises from the models names
        exercises = [model.split(".")[0] for model in models]

        # For each exercise, load the model and make predictions
        for exo in exercises:
            try:
                data_analytics_logger.info(f"Plotting predicted volume for exercise '{exo}'...")

                # Filter the performance data for the specific exercise
                df_exo = perf[perf["EXERCISE"] == exo].reset_index(drop=True)
                if df_exo.empty:
                    data_analytics_logger.error(f"No data found for exercise '{exo}'")
                    return False

                # Format the DATE column to the number of days since the beginning of the exercises
                df_exo['DATE'] = pd.to_datetime(df_exo['DATE'])
                min_date = df_exo['DATE'].min()
                df_exo['DATE'] = (df_exo['DATE'] - df_exo['DATE'].min()) / np.timedelta64(1, 'D')

                # Get the minimum performance value
                min_perf = df_exo['PERF'].min()

                # Normalize columns for the LSTM model
                scaler = MinMaxScaler(feature_range=(0, 1))
                df_exo['PERF'] = scaler.fit_transform(df_exo[['PERF']])
                df_exo['DATE'] = scaler.fit_transform(df_exo[['DATE']])

                # Load exercise model
                model = tf.keras.models.load_model(f'{models_path}/current/{exo}.h5')

                # Create a dataframe with the predictions
                predictions = pd.DataFrame(columns=["DATE", "PERF"])

                # Define a future date
                future_date = scaler.inverse_transform(df_exo[['DATE']]).max()

                # Make predictions for the next n_weeks weeks
                for i in range(n_weeks):
                    future_date_scaled = scaler.transform([[future_date]])
                    future_date_scaled = np.array([[future_date_scaled]])
                    future_date_scaled = future_date_scaled.reshape((future_date_scaled.shape[0], 1, future_date_scaled.shape[1]))
                    future_perf = model.predict(future_date_scaled, verbose=0)
                    future_perf = scaler.inverse_transform(future_perf) + min_perf
                    new_row = pd.DataFrame({"DATE": [future_date], "PERF": [future_perf[0][0]]})
                    predictions = pd.concat([predictions, new_row], ignore_index=True)
                    future_date = future_date + 7

                df_exo['DATE'] = scaler.inverse_transform(df_exo[['DATE']])
                df_exo['DATE'] = pd.to_timedelta(df_exo['DATE'], unit='D') + min_date

                df_exo['PERF'] = scaler.inverse_transform(df_exo[['PERF']]) + min_perf

                predictions['DATE'] = pd.to_timedelta(predictions['DATE'], unit='D') + min_date

                # Plot the actual data and the predictions
                fig = go.Figure()

                # Add actual data to the plot
                fig.add_trace(go.Scatter(x=df_exo['DATE'],
                                         y=df_exo['PERF'],
                                         mode='lines',
                                         name='History',
                                         hovertemplate="%{y:.1f} kg",
                                         line=dict(color='#4a3e80', width=2)))

                # Add predictions to the plot
                fig.add_trace(go.Scatter(x=predictions['DATE'],
                                         y=predictions['PERF'],
                                         mode='lines',
                                         name='Predictions',
                                         hovertemplate="%{y:.1f} kg",
                                         line=dict(color='#bc75ff', width=2)))

                # Add title and labels
                fig.update_layout(
                    title=f"Evolution of the Average Volume - {exo}",
                    xaxis_title=None,
                    yaxis_title="Average Volume (kg)",
                    hovermode="x unified",
                    font=dict(
                        family="Roboto, sans-serif",
                        size=18,
                        color="#333"
                    ),
                    template="plotly_white",
                    height=700,
                    plot_bgcolor="#f4f4f4",
                    paper_bgcolor="#f4f4f4",
                    yaxis=dict(
                        gridcolor="#ddd",
                        zerolinecolor="#ddd",
                    ),
                    xaxis=dict(
                        gridcolor="#ddd",
                        zerolinecolor="#ddd",
                        dtick="M1",
                        tickformat="%b\n%Y"
                    ),
                )

                # Save the plot as an HTML file
                fig.write_html(f"{static_path}/plots/predicted_volume/{exo}.html")

                data_analytics_logger.info(f"Plotted predicted volume for exercise '{exo}'.")

            except Exception as e:
                data_analytics_logger.error(f"Error occurred while plotting predicted volume for exercise '{exo}': {e}")
                return False

        data_analytics_logger.info(f"Plotted predicted volume for each exercise.")
        return True

    except Exception as e:
        data_analytics_logger.error(f"Error occurred while plotting predicted volume for each exercise: {e}")
        return False


def plot_distribution_muscle_groups(data_path: str, static_path: str) -> bool:
    """
    Plot the distribution of the targeted muscle groups.
    """
    try:
        data_analytics_logger.info("Plotting the distribution of the targeted muscle groups...")

        # Load enriched workout data
        enriched_workout_data = pd.read_csv(f"{data_path}/current/enriched_workout_data.csv", header=0)

        # Calculate the distribution of the targeted muscle groups
        hist_data = enriched_workout_data['BodyPart'].value_counts().sort_values(ascending=False)

        # Plot the distribution of the targeted muscle groups
        fig = go.Figure()

        # Define the bar plot
        fig.add_trace(go.Bar(
            x=hist_data.index,
            y=hist_data.values,
            marker=dict(color="#4a3e80"),
            hovertemplate="Number of Sets: %{y}<extra></extra>",
        ))

        # Add title and labels
        fig.update_layout(
            title="Distribution of Targeted Muscle Groups",
            xaxis_title="Muscle Group",
            yaxis_title="Number of Sets",
            hovermode="x unified",
            font=dict(
                family="Roboto, sans-serif",
                size=18,
                color="#333"
            ),
            template="plotly_white",
            height=700,
            plot_bgcolor="#f4f4f4",
            paper_bgcolor="#f4f4f4",
            yaxis=dict(
                gridcolor="#ddd",
                zerolinecolor="#ddd",
            ),
        )

        # Save the plot as an HTML file
        fig.write_html(f"{static_path}/plots/distribution_muscle_groups.html")

        data_analytics_logger.info("Plotted the distribution of the targeted muscle groups.")
        return True

    except Exception as e:
        data_analytics_logger.error(f"Error occurred while plotting the distribution of the targeted muscle groups: {e}")
        return False


def plot_distribution_workout_types(data_path: str, static_path: str) -> bool:
    """
    Plot the distribution of the workout types.
    """
    try:
        data_analytics_logger.info("Plotting the distribution of the workout types...")

        # Load workout days data
        workout_days = pd.read_csv(f"{data_path}/current/workout_days.csv", header=0)

        # Count of workout types
        workout_occurrences = workout_days["WORKOUT"].value_counts()

        # Workout types above 5 occurrences
        valid_workouts = workout_occurrences[workout_occurrences > 5].index
        valid_workouts_data = workout_days[workout_days['WORKOUT'].isin(valid_workouts)]

        # Distribution of workout types (Workouts above 5 occurrences)
        fig = go.Figure()

        # Create donut chart
        fig.add_trace(go.Pie(
            labels=valid_workouts_data['WORKOUT'].value_counts().index,
            values=valid_workouts_data['WORKOUT'].value_counts().values,
            hole=0.6,
            marker_colors=px.colors.qualitative.Bold,
            hoverinfo="label+percent",
            hovertemplate="Workout: %{label}<br>Percentage: %{percent}<br>Occurrences: %{value}<extra></extra>",
            textinfo="value",
            textposition="inside"
        ))

        # Add title and labels
        fig.update_layout(
            title="Distribution of Workout Types",
            font=dict(
                family="Roboto, sans-serif",
                size=18,
                color="#333"
            ),
            template="plotly_white",
            plot_bgcolor="#f4f4f4",
            paper_bgcolor="#f4f4f4",
            height=500,
        )

        # Save the plot as an HTML file
        fig.write_html(f"{static_path}/plots/distribution_workout_types.html")

        data_analytics_logger.info("Plotted the distribution of the workout types.")
        return True

    except Exception as e:
        data_analytics_logger.error(f"Error occurred while plotting the distribution of the workout types: {e}")
        return False


def plot_weight_reps_over_time(data_path: str, static_path: str) -> bool:
    """
    Plot the evolution of the weight and reps over time.
    """
    try:
        data_analytics_logger.info("Plotting the evolution of the weight and reps over time...")

        # Load workout day exercises data
        workout_day_exercises = pd.read_csv(f"{data_path}/current/workout_day_exercises.csv", header=0)

        # Get top 5 exercises
        top_5_exercises = workout_day_exercises['EXERCISE'].value_counts().head(5).index
        top_5_exercises_data = workout_day_exercises[workout_day_exercises['EXERCISE'].isin(top_5_exercises)]
        top_5_exercises_data.loc[:, 'DATE'] = pd.to_datetime(top_5_exercises_data['DATE'])

        # Define color map for the exercises
        color_map = dict(zip(top_5_exercises, px.colors.qualitative.Bold))

        # Evolution of weights and reps over time (Top 5 exercises)
        fig = go.Figure()

        # Add a scatter trace for each exercise
        for exo in top_5_exercises:
            exo_data = top_5_exercises_data[top_5_exercises_data['EXERCISE'] == exo]
            fig.add_trace(
                go.Scatter(
                    x=exo_data['DATE'],
                    y=exo_data['AVERAGE_WEIGHT'],
                    mode='markers',
                    marker=dict(size=exo_data['AVERAGE_REPS'], color=color_map[exo]),
                    name=exo,
                    hovertext=exo_data['EXERCISE'],
                    hovertemplate=
                    "<b>%{hovertext}</b><br>" +
                    "Average Weight: %{y:.1f} kg<br>" +
                    "Average Reps: %{marker.size:.1f}<extra></extra>",
                )
            )

        # Add title and labels
        fig.update_layout(
            title="Evolution of Weights and Reps over Time (Top 5 Exercises)",
            xaxis_title=None,
            yaxis_title="Average Weight",
            hovermode="x unified",
            font=dict(
                family="Roboto, sans-serif",
                size=18,
                color="#333"
            ),
            template="plotly_white",
            height=700,
            plot_bgcolor="#f4f4f4",
            paper_bgcolor="#f4f4f4",
            yaxis=dict(
                gridcolor="#ddd",
                zerolinecolor="#ddd",
            ),
            xaxis=dict(
                gridcolor="#ddd",
                zerolinecolor="#ddd",
            ),
        )

        # Save the plot as an HTML file
        fig.write_html(f"{static_path}/plots/weight_reps_over_time.html")

        data_analytics_logger.info("Plotted the evolution of the weight and reps over time.")
        return True

    except Exception as e:
        data_analytics_logger.error(f"Error occurred while plotting the evolution of the weight and reps over time: {e}")
        return False
