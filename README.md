Student Grade Tracker



A full-stack academic performance tracking application designed for teachers and students. Built using Python (Flask + Gradio + SQLite), this tool allows real-time grade management, GPA calculation, data visualization, and CSV export — all running in the cloud via Google Colab.

Features

 Add, update, delete student grades

 GPA and percentage calculation

 Grade visualization (bar charts)

CSV export

No login required (demo mode)

 Accessible dark-mode UI with Gradio

 File Structure

├── app.py                    # Flask API backend
├── ui.py                     # Gradio frontend interface
├── database.py               # SQLite CRUD operations
├── final_production_cleaned.py  # Backup version for final deployment
├── requirements.txt          # Python dependencies

 Getting Started (Google Colab Setup)

This application is designed for cloud execution via Google Colab.

1. Upload Files to Colab

Upload the following .py files manually:

app.py

database.py

ui.py

(optionally) final_production_cleaned.py

2. Install Required Packages

Paste this in the first Colab cell:

!pip install flask gradio pandas matplotlib

3. Initialize Database (Optional Cell)

from database import init_db
init_db()

4. Run Backend and Frontend

!python app.py &
!python ui.py

A public Gradio URL will appear. Open it in a new tab.

 Usage

Select or enter a student name.

Enter or select subject.

Use slider to input grade.

Click Add/Update to save it.

Click View Grades to fetch all data and visualization.

Use Download CSV to export grade report.

 Developer

Name: Muhammad JamilCourse: COSC3506 – Software EngineeringInstitution: Algoma University

Repository Link

https://github.com/Jamie8788/MuhammadJamil_student-grade-tracker

 License

Licensed under the MIT License
