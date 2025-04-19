
from flask import Flask, request, jsonify
from database import get_grades, add_grade, delete_grade

app = Flask(__name__)

USERS = {
    "teacher": {"password": "teach123", "role": "teacher"},
    "alice":   {"password": "alice123", "role": "student", "name": "Alice Anderson"},
    "bob":     {"password": "bob123",   "role": "student", "name": "Bob Brown"}
}

@app.route('/grades', methods=['GET'])
def api_get_grades():
    student = request.args.get('student')
    if student:
        records = get_grades(student)
        grades_list = [{"subject": subj, "grade": grade} for (subj, grade) in records]
        if records:
            grades_vals = [float(g) for (_, g) in records]
            avg = sum(grades_vals) / len(grades_vals)
            gpa = (avg / 100) * 4.0
            avg = round(avg, 2)
            gpa = round(gpa, 2)
        else:
            avg = 0
            gpa = 0
        return jsonify({"student": student, "grades": grades_list, "average": avg, "gpa": gpa})
    else:
        records = get_grades()
        grades_list = [{"student": stu, "subject": subj, "grade": grade} 
                       for (stu, subj, grade) in records]
        return jsonify({"grades": grades_list})

@app.route('/add_grade', methods=['POST'])
def api_add_grade():
    data = request.get_json(force=True)
    if not data or not all(k in data for k in ("student", "subject", "grade")):
        return jsonify({"error": "Missing fields"}), 400
    student = data["student"]
    subject = data["subject"]
    grade   = data["grade"]
    message = add_grade(student, subject, grade)
    return jsonify({"message": message})

@app.route('/delete_grade', methods=['POST'])
def api_delete_grade():
    data = request.get_json(force=True)
    if not data or not all(k in data for k in ("student", "subject")):
        return jsonify({"error": "Missing fields"}), 400
    student = data["student"]
    subject = data["subject"]
    message = delete_grade(student, subject)
    return jsonify({"message": message}")

# Comment out app.run() for Colab use
# if __name__ == "__main__":
#     app.run(debug=True)
