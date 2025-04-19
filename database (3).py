
import sqlite3
from datetime import datetime

def init_db(db_path='grades.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS grades (
                      id INTEGER PRIMARY KEY,
                      student TEXT,
                      subject TEXT,
                      grade REAL,
                      timestamp TEXT
                   )''')
    cur.execute('DELETE FROM grades')
    sample_grades = [
        ('alice', 'Math', 92),
        ('alice', 'English', 85),
        ('alice', 'History', 70),
        ('bob',   'Math', 68),
        ('bob',   'English', 74),
        ('bob',   'History', 81)
    ]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for student, subject, grade in sample_grades:
        cur.execute('INSERT INTO grades (student, subject, grade, timestamp) VALUES (?,?,?,?)',
                    (student, subject, grade, timestamp))
    conn.commit()
    conn.close()

def get_grades(student=None, db_path='grades.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    if student:
        cur.execute('SELECT subject, grade FROM grades WHERE student=?', (student,))
    else:
        cur.execute('SELECT student, subject, grade FROM grades')
    rows = cur.fetchall()
    conn.close()
    return rows

def add_grade(student, subject, grade, db_path='grades.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT id FROM grades WHERE student=? AND subject=?', (student, subject))
    row = cur.fetchone()
    if row:
        cur.execute('UPDATE grades SET grade=?, timestamp=? WHERE id=?',
                    (grade, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row[0]))
        message = "Grade updated."
    else:
        cur.execute('INSERT INTO grades (student, subject, grade, timestamp) VALUES (?,?,?,?)',
                    (student, subject, grade, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        message = "Grade added."
    conn.commit()
    conn.close()
    return message

def delete_grade(student, subject, db_path='grades.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT id FROM grades WHERE student=? AND subject=?', (student, subject))
    row = cur.fetchone()
    if row:
        cur.execute('DELETE FROM grades WHERE id=?', (row[0],))
        conn.commit()
        message = "Grade deleted."
    else:
        message = "Grade not found."
    conn.close()
    return message
