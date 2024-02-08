from flask import Flask, render_template, url_for
import os
import glob

from .data_loading import load_workout_data, load_filtered_exercise_data


# Path to the data directory
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')

# Path to the static directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/workouts')
def workouts():
    workouts = load_workout_data(file_path=os.path.join(data_dir, 'current/workout_data.csv'))
    return render_template('workouts.html', workouts=workouts)


@app.route('/my-exercises')
def my_exercises():
    my_exercises = load_filtered_exercise_data(file_path=os.path.join(data_dir, 'current/workout_exercises.csv'))
    return render_template('my-exercises.html', my_exercises=my_exercises)


@app.route('/analytics')
def analytics():
    predicted_volume_files = glob.glob(f"{static_dir}/plots/predicted_volume/*.html")
    exercises = sorted(os.path.basename(file).replace('.html', '') for file in predicted_volume_files)
    plot_paths = {
        'exercises': exercises,
        'predicted_volume': [url_for('static', filename=f'plots/predicted_volume/{exercise}.html') for exercise in exercises],
        'distribution_workout_types': url_for('static', filename='plots/distribution_workout_types.html'),
        'distribution_muscle_groups': url_for('static', filename='plots/distribution_muscle_groups.html'),
        'weight_reps_over_time': url_for('static', filename='plots/weight_reps_over_time.html')
    }
    return render_template('analytics.html', plot_paths=plot_paths)
