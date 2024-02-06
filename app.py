from flask import Flask, render_template

from features.data_loading import load_workout_data, load_filtered_exercise_data

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/workouts')
def workouts():
    workouts = load_workout_data(file_path='./data/current/workout_data.csv')
    return render_template('workouts.html', workouts=workouts)


if __name__ == '__main__':
    app.run(debug=True)
