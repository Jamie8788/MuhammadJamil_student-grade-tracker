
import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
from database import init_db, get_grades, add_grade, delete_grade

# Initialize the database and sample data (ensure this runs in Colab environment)
init_db()

USERS = {
    "teacher": {"password": "teach123", "role": "teacher"},
    "alice":   {"password": "alice123", "role": "student", "name": "Alice Anderson"},
    "bob":     {"password": "bob123",   "role": "student", "name": "Bob Brown"}
}

def plot_grades(grades_list):
    subjects = [subj for (subj, _) in grades_list]
    scores = [float(s) for (_, s) in grades_list]
    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(1,1,1)
    if len(scores) == 0:
        ax.text(0.3, 0.5, "No grades to display", fontsize=12)
        ax.axis('off')
        return fig
    ax.bar(subjects, scores, color='skyblue')
    ax.set_ylim(0, 100)
    ax.set_title("Student Performance")
    ax.set_xlabel("Subject")
    ax.set_ylabel("Grade (%)")
    for i, v in enumerate(scores):
        ax.text(i, v + 2, f"{v:.0f}%", ha='center', va='bottom')
    avg = sum(scores) / len(scores)
    ax.axhline(avg, color='red', linestyle='--', linewidth=1)
    ax.text(len(scores)-1, avg + 4, f"Avg: {avg:.1f}%", color='red')
    plt.tight_layout()
    return fig

with gr.Blocks(title="Student Grade Tracker") as demo:
    user_state = gr.State({"username": None, "role": None})
    
    gr.Markdown("### Login", elem_id="login-title")
    with gr.Row() as login_section:
        username_input = gr.Textbox(label="Username", placeholder="Enter username")
        password_input = gr.Textbox(label="Password", type="password", placeholder="Enter password")
        login_button = gr.Button(value="Log In")
    login_message = gr.Markdown("")
    
    teacher_section = gr.Column(visible=False)
    with teacher_section:
        teacher_greet = gr.Markdown("")
        with gr.Row():
            student_select = gr.Dropdown(label="Select Student", choices=["All Students", "Alice Anderson", "Bob Brown"], value="All Students")
            subject_select = gr.Dropdown(label="Subject (choose existing or type new)", choices=[], interactive=True)
            new_subject = gr.Textbox(label="New Subject Name (if adding a new subject)", placeholder="e.g. Science")
        grade_input = gr.Slider(label="Grade (%)", minimum=0, maximum=100, step=1, value=0)
        with gr.Row():
            add_button = gr.Button("Add/Update Grade")
            delete_button = gr.Button("Delete Grade")
        teacher_status = gr.Markdown("")
        teacher_table = gr.Dataframe(headers=["Student", "Subject", "Grade"], value=pd.DataFrame(), interactive=False)
    
    student_section = gr.Column(visible=False)
    with student_section:
        student_greet = gr.Markdown("")
        student_stats = gr.Markdown("")
        student_table = gr.Dataframe(headers=["Subject", "Grade"], value=pd.DataFrame(), interactive=False)
        student_plot = gr.Plot()
        refresh_button = gr.Button("Refresh Data")
    
    logout_button = gr.Button("Logout", visible=False)
    
    def login_user(username, password):
        if username in USERS and USERS[username]["password"] == password:
            role = USERS[username]["role"]
            user_state.value = {"username": username, "role": role}
            if role == "teacher":
                teacher_name = "Teacher"
                teacher_greet_text = f"**Welcome, {teacher_name}!**"
                all_records = get_grades()
                subjects = sorted({rec[1] for rec in all_records})
                subject_select.update(choices=subjects)
                df = pd.DataFrame(all_records, columns=["Student", "Subject", "Grade"])
                for user, info in USERS.items():
                    if info.get("name") and not df.empty:
                        df.loc[df["Student"] == user, "Student"] = info["name"]
                return ("", gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=True),
                        teacher_greet_text, gr.update(value=pd.DataFrame(), visible=False), gr.update(value="", visible=False),
                        df, pd.DataFrame(), None)
            else:
                student_name = USERS[username].get("name", username)
                student_greet_text = f"**Welcome, {student_name}!**"
                records = get_grades(username)
                df = pd.DataFrame(records, columns=["Subject", "Grade"])
                if len(records) > 0:
                    grades = [float(g) for (_, g) in records]
                    avg = sum(grades) / len(grades)
                    gpa = (avg / 100) * 4.0
                    stats_text = f"**GPA:** {gpa:.2f} &nbsp;&nbsp; **Average:** {avg:.1f}%"
                else:
                    stats_text = "*No grades available yet.*"
                fig = plot_grades(records)
                return ("", gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True),
                        "", student_greet_text, stats_text, pd.DataFrame(), df, fig)
        else:
            return ("**Invalid username or password.**", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False),
                    gr.update(visible=False), "", "", "", pd.DataFrame(), pd.DataFrame(), None)
    
    def teacher_add_grade(selected_student, subj_selected, new_subj, grade):
        if selected_student == "All Students":
            return "**Please select a specific student to add/update.**", gr.update(value=get_grades())
        subject = new_subj.strip() if new_subj else subj_selected
        if not subject:
            return "**Please specify a subject.**", gr.update(value=get_grades())
        username = None
        for user, info in USERS.items():
            if info.get("name") == selected_student:
                username = user
        if username is None:
            username = selected_student
        msg = add_grade(username, subject, float(grade))
        all_subjects = sorted({rec[1] for rec in get_grades()})
        subject_select.update(choices=all_subjects)
        if username and selected_student != "All Students":
            records = get_grades(username)
            df = pd.DataFrame([(username, subj, grd) for subj, grd in records], columns=["Student", "Subject", "Grade"])
        else:
            records = get_grades()
            df = pd.DataFrame(records, columns=["Student", "Subject", "Grade"])
        for user, info in USERS.items():
            if info.get("name") and not df.empty:
                df.loc[df["Student"] == user, "Student"] = info["name"]
        return msg, df

    def teacher_delete_grade(selected_student, subj_selected, new_subj):
        if selected_student == "All Students":
            return "**Please select a specific student to delete.**", gr.update(value=get_grades())
        subject = new_subj.strip() if new_subj else subj_selected
        if not subject:
            return "**Please specify a subject to delete.**", gr.update(value=get_grades())
        username = None
        for user, info in USERS.items():
            if info.get("name") == selected_student:
                username = user
        if username is None:
            username = selected_student
        msg = delete_grade(username, subject)
        if username and selected_student != "All Students":
            records = get_grades(username)
            df = pd.DataFrame([(username, subj, grd) for subj, grd in records], columns=["Student", "Subject", "Grade"])
        else:
            records = get_grades()
            df = pd.DataFrame(records, columns=["Student", "Subject", "Grade"])
        for user, info in USERS.items():
            if info.get("name") and not df.empty:
                df.loc[df["Student"] == user, "Student"] = info["name"]
        return msg, df

    def refresh_student_data(state):
        username = state["username"]
        if username and state["role"] == "student":
            records = get_grades(username)
            df = pd.DataFrame(records, columns=["Subject", "Grade"])
            if len(records) > 0:
                grades = [float(g) for (_, g) in records]
                avg = sum(grades) / len(grades)
                gpa = (avg / 100) * 4.0
                stats_text = f"**GPA:** {gpa:.2f} &nbsp;&nbsp; **Average:** {avg:.1f}%"
            else:
                stats_text = "*No grades available yet.*"
            fig = plot_grades(records)
            return df, stats_text, fig

    def logout_user():
        user_state.value = {"username": None, "role": None}
        return (gr.update(visible=True), gr.update(visible=False), gr.update(visible=False),
                gr.update(visible=False), "", "")

    login_button.click(fn=login_user,
                       inputs=[username_input, password_input],
                       outputs=[login_message, login_section, teacher_section, student_section, logout_button,
                                teacher_greet, student_greet, student_stats, teacher_table, student_table, student_plot])
    add_button.click(fn=teacher_add_grade,
                     inputs=[student_select, subject_select, new_subject, grade_input],
                     outputs=[teacher_status, teacher_table])
    delete_button.click(fn=teacher_delete_grade,
                        inputs=[student_select, subject_select, new_subject],
                        outputs=[teacher_status, teacher_table])
    refresh_button.click(fn=refresh_student_data,
                         inputs=user_state,
                         outputs=[student_table, student_stats, student_plot])
    logout_button.click(fn=logout_user,
                        inputs=None,
                        outputs=[login_section, teacher_section, student_section, logout_button, teacher_status, login_message])

demo.launch(debug=False, share=True)
