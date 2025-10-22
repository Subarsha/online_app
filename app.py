import csv
import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Replace with a strong random key

# ------------------------
# Base directory
# ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, 'students.csv')
RESULTS_FILE = os.path.join(BASE_DIR, 'results.csv')

# ------------------------
# Questions data
# ------------------------
QUESTIONS = [
    {"id": 1, "text": "What is the capital of India?", "choices": ["Mumbai", "New Delhi", "Kolkata", "Chennai"], "answer": 1},
    {"id": 2, "text": "Which gas do plants absorb from the atmosphere?", "choices": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"], "answer": 2},
    {"id": 3, "text": "2 + 2 * 3 = ?", "choices": ["12", "8", "10", "6"], "answer": 1},
    {"id": 4, "text": "Who wrote 'Romeo and Juliet'?", "choices": ["Charles Dickens", "William Shakespeare", "Leo Tolstoy", "Mark Twain"], "answer": 1},
    {"id": 5, "text": "Which planet is known as the Red Planet?", "choices": ["Earth", "Venus", "Mars", "Jupiter"], "answer": 2}
]

# ------------------------
# Load valid student IDs
# ------------------------
VALID_IDS = set()
if os.path.isfile(STUDENTS_FILE):
    with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            VALID_IDS.add(row[0].strip())

# ------------------------
# Home Page
# ------------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        if not student_id:
            return render_template('index.html', error="Please enter your Student ID.")
        if student_id not in VALID_IDS:
            return render_template('index.html', error="Invalid Student ID.")
        session['student_id'] = student_id
        session['taken'] = False
        return redirect(url_for('test'))
    return render_template('index.html', error=None)

# ------------------------
# Test Page
# ------------------------
@app.route('/test', methods=['GET', 'POST'])
def test():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('home'))

    # Prevent multiple attempts
    if os.path.isfile(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row[0] == student_id:
                    return render_template("already_submitted.html", student_id=student_id)

    if session.get('taken'):
        return render_template("already_submitted.html", student_id=student_id)

    if request.method == 'POST':
        # Grab answers
        answers = {}
        for q in QUESTIONS:
            key = f'question_{q["id"]}'
            value = request.form.get(key)
            answers[q["id"]] = int(value) if value is not None else None

        # Calculate score
        score = sum(1 for q in QUESTIONS if answers[q["id"]] == q["answer"])

        # Save result
        file_exists = os.path.isfile(RESULTS_FILE)
        with open(RESULTS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Student ID', 'Score', 'Total'] + [f'Q{i}' for i in range(1, len(QUESTIONS)+1)])
            row_answers = [q["choices"][answers[q["id"]]] if answers[q["id"]] is not None else "Not Answered" for q in QUESTIONS]
            writer.writerow([student_id, score, len(QUESTIONS)] + row_answers)

        session['taken'] = True
        return render_template("result.html", name=student_id, score=score, total=len(QUESTIONS), questions=QUESTIONS, answers=answers)

    return render_template("test.html", name=student_id, questions=QUESTIONS)

# ------------------------
# Run App
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)
