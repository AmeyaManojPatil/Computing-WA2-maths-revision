from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
import time
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

def cosine_of_angle(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

def perpendicular_distance(point, line_point1, line_point2):
    line_vec = np.array(line_point2) - np.array(line_point1)
    point_vec = np.array(point) - np.array(line_point1)
    return np.linalg.norm(np.cross(line_vec, point_vec)) / np.linalg.norm(line_vec)

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("revise_user.db")  # Ensure correct DB name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        users = cursor.fetchall()  # Get all matching records
        conn.close()

        if users:
            user = users[0]  # Get the first record
            stored_password = user[3]  # Assuming password is at index 3
            if stored_password == password:
                session.clear()  # Clear any existing session data
                session['logged_in'] = True
                session['username'] = username  # Store the username for reference

                # Regardless of whether the credentials match or not, redirect to login
                return redirect(url_for('login'))

    return render_template("index.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    # Remove the session check, always render login.html
    return render_template("login.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return render_template("register.html", error="Both fields are required.")

        try:
            conn = sqlite3.connect("revise_user.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
            existing_user = cursor.fetchall()

            if existing_user:
                return render_template("register.html", error="Username already exists.")

            # Insert the new user
            cursor.execute("INSERT INTO Users (Username, QuestionsCount, Password) VALUES (?, ?, ?)", (username, 0, password))
            conn.commit()
            return redirect(url_for('home'))  # Redirect to home page after successful registration

        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")  # Print error to the console for debugging
            return render_template("register.html", error="An error occurred while registering. Please try again.")

        finally:
            conn.close()

    return render_template("register.html")

@app.route('/select-topic', methods=['POST'])
def select_topic():
    topic = request.form['topic']

    if topic == "Vectors 1":
        return redirect(url_for('vectors1'))
    elif topic == "Vectors 2":
        return redirect(url_for('vectors2'))
    elif topic == "Vectors 3":
        return redirect(url_for('vectors3'))
    elif topic == "Transformation of Curves":
        return redirect(url_for('transformation_of_curves'))
    elif topic == "Differentiation":
        return redirect(url_for('differentiation'))
    elif topic == "Integration":
        return redirect(url_for('integration'))
    else:
        return redirect(url_for('home'))

@app.route('/vectors1')
def vectors1():
    # Store start time in the session
    session['start_time'] = time.time()

    OA = [random.randint(-10, 10) for _ in range(3)]
    OB = [random.randint(-10, 10) for _ in range(3)]
    OC = [random.randint(-10, 10) for _ in range(3)]
    OD = [random.randint(-10, 10) for _ in range(3)]

    return render_template('vectors1.html', OA=OA, OB=OB, OC=OC, OD=OD)

@app.route('/submit_vectors1', methods=['POST'])
def submit_vectors1():
    start_time = session.get('start_time')
    if not start_time:
        return redirect(url_for('vectors1'))

    end_time = time.time()
    time_taken = end_time - start_time

    answer1 = request.form['answer1']
    answer2 = request.form['answer2']

    # Define vectors
    OA = np.array([6, 8, -3])
    OB = np.array([10, -2, 3])
    OC = np.array([-2, -9, -10])
    OD = np.array([-2, 5, 3])

    # Calculate correct answers
    cos_angle_DAB = cosine_of_angle(OD - OA, OB - OA)
    distance_D_from_AB = perpendicular_distance(OD, OA, OB)
    projection_CD_on_BC = np.dot(OC - OD, OB - OC) / np.linalg.norm(OB - OC)

    # Convert answers to strings for comparison
    correct_answer1 = f"{cos_angle_DAB:.4f}"
    correct_answer2 = f"{projection_CD_on_BC:.4f}"

    # Check answers
    is_correct1 = answer1.strip() == correct_answer1
    is_correct2 = answer2.strip() == correct_answer2

    # Time limit calculation
    marks = 2  # Marks for this quiz
    time_limit = 1.8 * marks  # 1.8 minutes per mark

    fast_enough = time_taken <= (time_limit * 60)  # Convert minutes to seconds

    return render_template('results.html', 
                           correct=is_correct1 and is_correct2, 
                           time_taken=round(time_taken, 2), 
                           fast_enough=fast_enough,
                           correct_answer1=correct_answer1,
                           correct_answer2=correct_answer2)

@app.route('/vectors2')
def vectors2():
    return render_template("vectors2.html")

@app.route('/vectors3')
def vectors3():
    return render_template("vectors3.html")

@app.route('/transformation_of_curves')
def transformation_of_curves():
    return render_template("transformation_of_curves.html")

@app.route('/differentiation')
def differentiation():
    return render_template("differentiation.html")

@app.route('/integration')
def integration():
    return render_template("integration.html")

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
