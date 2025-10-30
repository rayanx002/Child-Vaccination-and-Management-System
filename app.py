from flask import Flask, render_template, request, redirect # type: ignore
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home / Front Page
@app.route('/')
def home():
    return render_template('index.html')

# Dashboard (list all children)
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    children = conn.execute('SELECT * FROM children').fetchall()
    conn.close()
    return render_template('dashboard.html', children=children)

# Register a child
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        guardian_name = request.form['guardian_name']
        contact = request.form['contact']

        conn = get_db_connection()
        conn.execute('INSERT INTO children (name, dob, guardian_name, contact) VALUES (?, ?, ?, ?)',
                     (name, dob, guardian_name, contact))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('register.html')

# View vaccination schedule
@app.route('/schedule/<int:child_id>')
def schedule(child_id):
    conn = get_db_connection()
    child = conn.execute('SELECT * FROM children WHERE id = ?', (child_id,)).fetchone()
    vaccines = conn.execute('SELECT * FROM vaccines').fetchall()
    records = conn.execute('SELECT * FROM vaccination_records WHERE child_id = ?', (child_id,)).fetchall()

    # Auto-insert records if missing
    if len(records) == 0:
        for vaccine in vaccines:
            conn.execute('INSERT INTO vaccination_records (child_id, vaccine_id) VALUES (?, ?)',
                         (child_id, vaccine['id']))
        conn.commit()
        records = conn.execute('SELECT * FROM vaccination_records WHERE child_id = ?', (child_id,)).fetchall()

    conn.close()
    return render_template('view_schedule.html', child=child, records=records)

# Update vaccine status
@app.route('/update_status/<int:record_id>', methods=['POST'])
def update_status(record_id):
    vaccination_date = request.form['vaccination_date']
    conn = get_db_connection()
    conn.execute('UPDATE vaccination_records SET status = "Completed", vaccination_date = ? WHERE id = ?',
                 (vaccination_date, record_id))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
