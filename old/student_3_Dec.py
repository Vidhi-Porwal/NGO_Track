from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
import mysql.connector
from auth import login_required, get_db_connection

student_bp = Blueprint('student', __name__)

def log_session():
    """Log session details for debugging."""
    print("Session Details:")
    for key, value in session.items():
        print(f"{key}: {value}")

@student_bp.before_request
def load_user_from_session():
    """Load user and location details from the session into Flask's global object."""
    g.user = session.get('user')
    g.location = session.get('location')

    if not g.user or not g.location:
        flash("Session expired. Please log in.")
        return redirect(url_for('auth.login'))


@student_bp.route('/student_profile/<int:student_id>')
@login_required
def student_profile(student_id):
    """Display student profile."""
    log_session()

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """SELECT s.student_id , s.student_name , s.student_age , s.parent_name , s.parent_contact , s.student_documentation , sch.school_name , l.location_name , g.grade_year 
                   FROM Student s
                   LEFT JOIN Student_school_grade ssg ON s.student_id = ssg.student_id
                   LEFT JOIN School sch ON ssg.school_id = sch.school_id
                   LEFT JOIN Grade g ON ssg.grade_id = g.grade_id
                   LEFT JOIN Location l ON s.location_id = l.location_id
                   WHERE s.student_id = %s"""
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()

        query = """SELECT sub.subject_name , ss.subject_score , ss.subject_progress
                   FROM Student_Subject ss
                   JOIN Subject sub ON ss.subject_id = sub.subject_id
                   WHERE ss.student_id = %s"""
        cursor.execute(query, (student_id,))
        student_subjects = cursor.fetchall()

        if not student:
            return render_template('404.html'), 404

        return render_template('student_profile.html', student=student, user=g.user, student_subjects=student_subjects)

    except mysql.connector.Error as err:
        return f"Error fetching student profile: {err}"

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@student_bp.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit student's details and subjects."""
    log_session()

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == 'POST':
            # Handle student details updates
            student_age = request.form.get('student_age')
            parent_name = request.form.get('parent_name')
            parent_contact = request.form.get('parent_contact')
            grade_id = request.form.get('grade_id')
            school_id = request.form.get('school_id')
            student_documentation = request.form.get('student_documentation', '')

            updates = []
            values = []

            if student_age:
                updates.append("student_age = %s")
                values.append(student_age)
            if parent_name:
                updates.append("parent_name = %s")
                values.append(parent_name)
            if parent_contact:
                updates.append("parent_contact = %s")
                values.append(parent_contact)
            if student_documentation:
                updates.append("student_documentation = %s")
                values.append(student_documentation)

            if updates:
                student_update_query = f"""
                    UPDATE Student
                    SET {', '.join(updates)}
                    WHERE student_id = %s
                """
                values.append(student_id)
                cursor.execute(student_update_query, tuple(values))

            # Handle school and grade updates
            if grade_id or school_id:
                grade_school_update_query = """
                    UPDATE Student_school_grade
                    SET grade_id = IFNULL(%s, grade_id), school_id = IFNULL(%s, school_id)
                    WHERE student_id = %s
                """
                cursor.execute(grade_school_update_query, (grade_id, school_id, student_id))

            # Handle adding or updating subjects
            subject_name = request.form.get('subject_name')
            subject_score = request.form.get('subject_score')
            subject_progress = request.form.get('subject_progress')

            if subject_name and subject_score and subject_progress:
                cursor.execute("""
                    INSERT INTO Subject (subject_name)
                    VALUES (%s)
                """, (subject_name,))
                subject_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO Student_Subject (student_id, subject_id, subject_score, subject_progress)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, subject_id, subject_score, subject_progress))

            # Handle editing existing subject scores and progress
            edit_subject_id = request.form.get('edit_subject_id')
            if edit_subject_id:
                cursor.execute("""
                    UPDATE Student_Subject
                    SET subject_score = %s, subject_progress = %s
                    WHERE student_id = %s AND subject_id = %s
                """, (subject_score, subject_progress, student_id, edit_subject_id))

            # Handle deleting subjects
            delete_subject_id = request.form.get('delete_subject_id')
            if delete_subject_id:
                cursor.execute("""
                    DELETE FROM Student_Subject
                    WHERE student_id = %s AND subject_id = %s
                """, (student_id, delete_subject_id))

            connection.commit()
            return redirect(url_for('student.edit_student', student_id=student_id))

        # Fetch student data and other related info
        cursor.execute("SELECT * FROM Student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()

        if not student:
            return render_template('404.html'), 404

        cursor.execute("SELECT * FROM School")
        schools = cursor.fetchall()

        cursor.execute("SELECT * FROM Grade")
        grades = cursor.fetchall()

        cursor.execute("SELECT * FROM Subject")
        subjects_list = cursor.fetchall()

        cursor.execute("""SELECT sub.subject_id, sub.subject_name, ss.subject_score, ss.subject_progress
                          FROM Student_Subject ss
                          LEFT JOIN Subject sub ON ss.subject_id = sub.subject_id
                          WHERE ss.student_id = %s""", (student_id,))
        subjects = cursor.fetchall()

        return render_template('edit_student.html', student=student, schools=schools, grades=grades, subjects=subjects, subjects_list=subjects_list, next_subject_index=len(subjects) + 1)

    except mysql.connector.Error as err:
        return f"Database error: {err}"

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
