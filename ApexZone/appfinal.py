import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Use environment variable for secret key
from urllib.parse import urlparse
def get_db_connection():
    url = os.getenv("DB_URL")
    return psycopg2.connect(url)


# Database setup function
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        password = request.form.get('password')
        
        if not username or not dob or not gender or not password:
            flash('Please fill out all fields', 'error')
            return redirect(url_for('signup'))

        try:
            # Check if username already exists
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    flash('Username already exists', 'error')
                    return redirect(url_for('signup'))

            # Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Insert user and initialize PR
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, DOB, gender, password) VALUES (%s, %s, %s, %s) RETURNING id' ,
                    (username, dob, gender, hashed_password)
                )
                user_id = cursor.fetchone()[0]
                conn.commit()

                try:
                    # Insert 23 default PR rows
                    for i in range(23):
                        cursor.execute(
                            'INSERT INTO pr (user_id, exercise_id, weight, reps) VALUES (%s, %s, %s, %s)',
                            (user_id, i + 1, 0, 0)
                        )
                    conn.commit()
                except psycopg2.Error as pr_error:
                    flash(f'User created, but failed to initialize PR records: {pr_error}', 'warning')
                    return redirect(url_for('login'))

            flash('Registration successful', 'success')
            return redirect(url_for('login'))

        except psycopg2.Error as e:
            flash(f'Database error: {e}', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                user = cursor.fetchone()

                if user:
                    if check_password_hash(user[4], password):  # password is 5th column (index 4)
                        session['user_id'] = user[0]  # user_id is 1st column (index 0)
                        flash('Login successful', 'success')
                        return redirect(url_for('redirect_after_login'))
                    else:
                        flash('Invalid password', 'error')
                        return redirect(url_for('login'))
                else:
                    flash('Username does not exist', 'error')
                    return redirect(url_for('signup'))
        except psycopg2.Error as e:
            flash(f'Database error: {e}', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/redirect_after_login')
def redirect_after_login():
    user_id = session.get('user_id')
    if user_id:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM BMI WHERE user_id = %s', (user_id,))
            bmi_data = cursor.fetchone()
            if bmi_data:
                return redirect(url_for('exercise'))
            else:
                return redirect(url_for('bmi_input'))
    return redirect(url_for('login'))

@app.route('/bmi-input', methods=['GET', 'POST'])
def bmi_input():
    if 'user_id' not in session:
        flash('You need to log in first', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            height = float(request.form['height'])
            weight = float(request.form['weight'])
            bmi = weight / (height / 100) ** 2
            user_id = session['user_id']

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO BMI (user_id, height, weight, bmi) VALUES (%s, %s, %s, %s)',
                               (user_id, height, weight, bmi))
                conn.commit()

            return render_template('bmi-result.html', bmi=bmi)
        except ValueError:
            flash('Invalid input for height or weight', 'error')
            return redirect(url_for('bmi_input'))
        
    return render_template('bmi-input.html')

@app.route('/bmi-result')
def bmi_result():
    if 'user_id' not in session:
        flash('You need to log in first', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    bmi_data = None
    bmi_category = None
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT height, weight, bmi FROM BMI WHERE user_id = %s ORDER BY id DESC LIMIT 1', (user_id,))
            bmi_data = cursor.fetchone()
            print(f'Debug: Fetched bmi_data: {bmi_data}')
            
        if bmi_data:
            latest_bmi = bmi_data[2]  # bmi is 3rd column (index 2)
            print(f'Debug: Latest BMI: {latest_bmi}')
            if latest_bmi < 18.5:
                bmi_category = 'Underweight - BULK'
            elif 18.5 <= latest_bmi < 25:
                bmi_category = 'Normal weight - FIT'
            elif 25 <= latest_bmi < 30:
                bmi_category = 'Overweight - CUT'
            else:
                bmi_category = 'Obesity - CUT'
            print(f'Debug: BMI Category: {bmi_category}')
        return render_template('bmi-result.html', bmi_data=bmi_data, bmi_category=bmi_category)
    except psycopg2.Error as e:
        flash(f'Database error: {e}', 'error')
        print(f'Debug: Database error: {e}')
        return redirect(url_for('bmi_input'))


@app.route('/exercise')
def exercise():
    return render_template('exercise.html')

@app.route('/diet')
def diet():
    return render_template('diet.html')

@app.route('/cut')
def cut():
    return render_template('cut.html')

@app.route('/bulk')
def bulk():
    return render_template('bulk.html')

@app.route('/legs')
def legs():
    return render_template('legs.html')

@app.route('/shoulders')
def shoulders():
    return render_template('shoulders.html')

@app.route('/chest')
def chest():
    return render_template('chest.html')

@app.route('/back')
def back():
    return render_template('back.html')

@app.route('/update_pr', methods=['GET', 'POST'])
def update_pr():
    if request.method == 'POST':
        try: 
            exercise_id = request.form['exercise_id']
            user_id = session['user_id']
            weight = request.form['weight']
            reps = request.form['reps']

            # Convert weight and reps to integers
            weight = int(weight)
            reps = int(reps)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE pr SET weight = %s, reps = %s WHERE user_id = %s AND exercise_id = %s", 
                               (weight, reps, user_id, exercise_id))
                conn.commit()
                
            if cursor.rowcount == 0:
                flash('Exercise not found or no update performed', 'error')
                return redirect(url_for('update_pr', id=exercise_id, user=user_id))

            # Calculate new PR
            new_pr = weight * reps
            flash(f'PR updated successfully. New PR: {new_pr}', 'success')
            return redirect(request.referrer)  # Redirect back to the previous page
                  
        except ValueError:
            flash('Invalid weight or reps value', 'error')
            return redirect(request.referrer)
        except psycopg2.Error as e:
            flash(f'Database error: {e}', 'error')
            return redirect(request.referrer)
        finally:
            try:
                conn.close()
            except Exception:
                pass
            
    else:
        exercise_id = request.args.get('id', '')
        user_id = request.args.get('user', '')
        return render_template('update_pr.html', exercise_id=exercise_id, user_id=user_id)
    
def get_exercises_by_muscle_group():
    user_id = session.get('user_id')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                SELECT exercises.name, pr.weight, pr.reps, exercises.muscle_group 
                FROM pr 
                JOIN exercises ON pr.exercise_id = exercises.id 
                WHERE pr.user_id = %s
            """, (user_id,))
        exercises = cursor.fetchall()
     
    exercises_by_muscle_group = {}
    for exercise in exercises:
        name, weight, reps, muscle_group = exercise
        if muscle_group not in exercises_by_muscle_group:
            exercises_by_muscle_group[muscle_group] = []
        exercises_by_muscle_group[muscle_group].append((name, weight, reps))
    
    return exercises_by_muscle_group

# Define route to display tables
@app.route('/display_tables')
def display_tables():
    exercises_by_muscle_group = get_exercises_by_muscle_group()
    
    return render_template('prshow.html', exercises_by_muscle_group=exercises_by_muscle_group)
    
if __name__ == '__main__':
    app.run(debug=True)
