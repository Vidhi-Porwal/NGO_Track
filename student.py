from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
import mysql.connector
from auth import login_required, get_db_connection

student_bp = Blueprint('student', __name__)

def log_session():
    print("Session Details:")
    for key, value in session.items():
        print(f"{key}: {value}")

@student_bp.before_request
def load_user_from_session():
    g.user = session.get('user')
    g.location = session.get('location')
    g.user_id = session.get('user_id')

    if not g.user or not g.location or not g.user_id:
        flash("Session expired. Please log in.")
        return redirect(url_for('auth.login'))


@student_bp.route('/student_profile/<int:student_id>')
@login_required
def student_profile(student_id):
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

        return render_template('student_profile.html', student=student, user=g.user, user_id = g.user_id , student_subjects=student_subjects)

    except mysql.connector.Error as err:
        return f"Error fetching student profile: {err}"

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@student_bp.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    log_session()
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == 'POST':
            # import pdb; pdb.set_trace()
            student_age = request.form.get('student_age')
            parent_name = request.form.get('parent_name')
            parent_contact = request.form.get('parent_contact')
            grade_id = request.form.get('grade_id')
            school_id = request.form.get('school_id')
            student_documentation = request.form.get('student_documentation')

            updates = []
            updates_1 = []
            values = []
            values_1 = []


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
            if school_id:
                updates_1.append("school_id = %s")
                values_1.append(school_id)
            if grade_id:
                updates_1.append("grade_id = %s")
                values_1.append(grade_id)


            if updates: 
                student_update_query = f"""
                    UPDATE Student
                    SET {', '.join(updates)}
                    WHERE student_id = %s
                """
                values.append(student_id)
                cursor.execute(student_update_query, tuple(values))


            if updates_1:
                school_id = None if not school_id else school_id
                grade_id = None if not grade_id else grade_id

                query_2 = "SELECT * FROM Student_school_grade WHERE student_id = %s"
                cursor.execute(query_2, (student_id,))
                student_exist = cursor.fetchone()

                if student_exist:
                    student_update_query_2 = f"""
                        UPDATE Student_school_grade
                        SET {', '.join(updates_1)}
                        WHERE student_id = %s
                    """
                    values_1.append(student_id)
                    cursor.execute(student_update_query_2, tuple(values_1))

                else :
                    student_insert_query = """
                        INSERT INTO Student_school_grade (student_id, school_id, grade_id)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(student_insert_query, (student_id, school_id, grade_id))
    


            connection.commit()
            flash("Student updated successfully!", "success")

            return redirect(url_for('student.edit_student', student_id=student_id))

        query = """SELECT s.student_id , s.student_name , s.student_age , s.parent_name , s.parent_contact , s.student_documentation , sch.school_name , l.location_name , g.grade_year 
                   FROM Student s
                   LEFT JOIN Student_school_grade ssg ON s.student_id = ssg.student_id
                   LEFT JOIN School sch ON ssg.school_id = sch.school_id
                   LEFT JOIN Grade g ON ssg.grade_id = g.grade_id
                   LEFT JOIN Location l ON s.location_id = l.location_id
                   WHERE s.student_id = %s"""
        cursor.execute(query, (student_id,))
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

        return render_template('edit_student.html', student_id=student_id, student=student, schools=schools, grades=grades, subjects=subjects, subjects_list=subjects_list,next_subject_index=len(subjects) + 1)

    except mysql.connector.Error as err:
        return f"Database error: {err}"

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@student_bp.route('/edit_subject/<int:student_id>', methods=['POST'])
@login_required
def edit_subject(student_id):
    log_session()
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        subject_id = request.form.get('subject_id')
        subject_score = request.form.get('subject_score')
        subject_progress = request.form.get('subject_progress')

        
        if subject_id and subject_score and subject_progress:
            cursor.execute("""
                UPDATE Student_Subject
                SET subject_score = %s, subject_progress = %s
                WHERE student_id = %s AND subject_id = %s
            """, (subject_score, subject_progress, student_id, subject_id))

            
            connection.commit()

            flash("Subject updated successfully!", "success") 
        else:
            flash("All fields are required!", "error")

        return redirect(url_for('student.edit_student', student_id=student_id))

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        return redirect(url_for('student.edit_student', student_id=student_id))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@student_bp.route('/delete_subject/<int:student_id>', methods=['POST'])
@login_required
def delete_subject(student_id):
    subject_id = request.form.get('subject_id')

    if not subject_id:
        flash("No subject selected for deletion.", "error")
        return redirect(url_for('student.edit_student', student_id=student_id))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        delete_query = "DELETE FROM Student_Subject WHERE subject_id = %s AND student_id = %s"
        cursor.execute(delete_query, (subject_id, student_id))

        connection.commit()

        flash("Subject deleted successfully!", "success")

    except mysql.connector.Error as err:
        flash(f"Error deleting subject: {err}", "error")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('student.edit_student', student_id=student_id))




@student_bp.route('/add_subject/<int:student_id>', methods=['POST'])
@login_required
def add_subject(student_id):
    # {{ url_for('student.add_subject', student_id=student.student_id) }}
    # import pdb; pdb.set_trace()
    log_session()
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        subject_id = request.form.get('subject_id')
        subject_score = request.form.get('subject_score')
        subject_progress = request.form.get('subject_progress')

        if subject_id and subject_score and subject_progress:
            cursor.execute("""
                INSERT INTO Student_Subject (student_id, subject_id, subject_score, subject_progress)
                VALUES (%s, %s, %s, %s)
            """, (student_id, subject_id, subject_score, subject_progress))

            connection.commit()

        return redirect(url_for('student.edit_student', student_id=student_id))

    except mysql.connector.Error as err:
        return f"Database error: {err}"

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@student_bp.route('/cancel_changes/<int:student_id>', methods=['POST'])
@login_required
def cancel_changes(student_id):
    """Cancel all changes and redirect back to the student profile."""
    return redirect(url_for('student.student_profile', student_id=student_id))

@student_bp.route('/new_student', methods=['GET', 'POST'])
@login_required
def new_student():
    log_session()

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == 'POST':
            student_name = request.form.get('student_name')
            student_age = request.form.get('student_age')
            parent_name = request.form.get('parent_name')
            parent_contact = request.form.get('parent_contact')
            school_id = request.form.get('school_id')
            grade_id = request.form.get('grade_id')
            student_documentation = request.form.get('student_documentation', '')

            
            if not student_name or not parent_name or not parent_contact :
                flash("All required fields must be filled!", "error")
                return redirect(url_for('student.new_student'))

            student_documentation = None if not student_documentation else student_documentation

            cursor.execute("""
                INSERT INTO Student (student_name, student_age, parent_name, parent_contact, student_documentation, location_id, school_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (student_name, student_age, parent_name, parent_contact, student_documentation, g.location, school_id))
            connection.commit()

            
            student_id = cursor.lastrowid

            if school_id and grade_id:
                cursor.execute("""
                    INSERT INTO Student_school_grade (student_id, school_id, grade_id)
                    VALUES (%s, %s, %s)
                """, (student_id, school_id, grade_id))
                connection.commit()

            # cursor.execute("""
            #     INSERT INTO Student_school_grade (student_id, school_id, grade_id)
            #     VALUES (%s, %s, %s)
            # """, (student_id, school_id if school_id else None, grade_id if grade_id else None))
            # connection.commit()

            # cursor.execute(student_add_query, tuple(value))

            flash("Student added successfully!", "success")
            return redirect(url_for('student.student_profile', student_id=student_id))

        
        cursor.execute("SELECT * FROM School")
        schools = cursor.fetchall()

        cursor.execute("SELECT * FROM Grade")
        grades = cursor.fetchall()

        
        return render_template('new_student.html', schools=schools, grades=grades, user=g.user, user_id=g.user_id)

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        return redirect(url_for('student.new_student'))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@student_bp.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    log_session()
    if not student_id:
        flash("No subject selected for deletion.", "error")
        return redirect(url_for('student.edit_student', student_id=student_id))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # delete_student_subject_query = "DELETE FROM Student_Subject WHERE student_id = %s"
        # cursor.execute(delete_student_subject_query, (student_id,))

        # delete_student_school_grade_query = "DELETE FROM Student_school_grade WHERE student_id = %s"
        # cursor.execute(delete_student_school_grade_query, (student_id,))

        delete_student_query = "DELETE FROM Student WHERE student_id = %s"
        cursor.execute(delete_student_query, (student_id,))

        connection.commit()

        flash("Student deleted successfully!", "success")

    except mysql.connector.Error as err:
        flash(f"Error deleting student: {err}", "error")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('home'))