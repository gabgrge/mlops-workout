from flask import Flask, render_template

from src.app.data_loading import load_workout_data, load_filtered_exercise_data

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/workouts')
def workouts():
    workouts = load_workout_data(file_path='./data/current/workout_data.csv')
    return render_template('workouts.html', workouts=workouts)


@app.route('/my-exercises')
def my_exercises():
    my_exercises = load_filtered_exercise_data(file_path='./data/current/workout_exercises.csv')
    return render_template('my-exercises.html', my_exercises=my_exercises)


@app.route('/analytics')
def analytics():
    my_exercises = load_filtered_exercise_data(file_path='./data/current/workout_exercises.csv')
    return render_template('my-exercises.html', my_exercises=my_exercises)
