from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Define function to connect to SQLite database
def connect_db():
    return sqlite3.connect('exercise_database.db')

# Define function to fetch exercise data by muscle group
def get_exercises_by_muscle_group():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT exercises.name, pr.weight, pr.reps, exercises.muscle_group FROM pr JOIN exercises ON pr.exercise_id = exercises.id")

    exercises = cursor.fetchall()
    conn.close()
    
    exercises_by_muscle_group = {}
    for exercise in exercises:
        name, weight, reps, muscle_group = exercise
        if muscle_group not in exercises_by_muscle_group:
            exercises_by_muscle_group[muscle_group] = []
        exercises_by_muscle_group[muscle_group].append((name, weight, reps))
    
    return exercises_by_muscle_group

# Define route to display tables
@app.route('/')
def display_tables():
    exercises_by_muscle_group = get_exercises_by_muscle_group()
    return render_template('prshow.html', exercises_by_muscle_group=exercises_by_muscle_group)

if __name__ == '__main__':
    app.run(debug=True)
