from math import ceil
from flask import Flask, flash, render_template, request, session, redirect, url_for, g
from auth import auth_bp, get_db_connection, login_required
from student import student_bp 
import mysql.connector
import os
import base64
from datetime import timedelta, datetime

app = Flask(__name__)
app.secret_key = 'DEV'  # Set a secret key for session management

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

@app.before_request
def check_session_timeout():
    session.permanent = True
    session.modified = True
    now = datetime.utcnow()

    last_activity = session.get('last_activity')
    if last_activity:
        last_activity_time = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
        if now - last_activity_time > app.config['PERMANENT_SESSION_LIFETIME']:
            session.clear()
            flash("Your session has expired. Please log in again.")
            return redirect(url_for('auth.login'))

    session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Activity")
    activities = cursor.fetchall()
    
    for activity in activities:
        if activity['activity_image']:
            activity['activity_image'] = base64.b64encode(activity['activity_image']).decode('utf-8')
    
    cursor.close()
    connection.close()

    return render_template('index.html', activities=activities)


@app.route('/Location')
@login_required
def Location():
    if 'user' in session:
        user = session['user']
        location_id = session['location']

    page=request.args.get('page',1,type=int)
    per_page=5
    offset=(page-1)*per_page   #starting point for current page
    if page < 1:
        flash('Page does not exist')
        return redirect(url_for('Location', page=1))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total from Location")  #total no of rows in location table
    total=cursor.fetchone()['total']

    cursor.execute("SELECT * FROM Location LIMIT %s OFFSET %s",(per_page,offset))
    location = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)

    return render_template('location.html',user=user, location_i=location,page=page, total_pages=total_pages)

@app.route('/Schools')
@login_required
def Schools():
    if 'user' in session:
        user = session['user']
        location_id = session['location']

    page=request.args.get('page',1,type=int)
    per_page=5
    offset=(page-1)*per_page   #starting point for current page
    if page < 1:
        flash('Page does not exist')
        return redirect(url_for('Schools', page=1))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total from School")  #total no of rows in location table
    total=cursor.fetchone()['total']

    cursor.execute("SELECT * FROM School LIMIT %s OFFSET %s",(per_page,offset))
    schools = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)

    return render_template('school.html', user=user, schools=schools ,page=page, total_pages=total_pages)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        print("Session content:", session)  # This will show the session contents in the console
        if 'user' in session:
            user = session['user']
            location_id = session['location']


            try:
                page=request.args.get('page',1,type=int)
                per_page=6
                offset=(page-1)*per_page
                if page < 1:
                    flash('Page does not exist')
                    return redirect(url_for('home', page=1))


                connection = get_db_connection()
                cursor = connection.cursor(dictionary=True)

                # Get total count of students
                count_query = "SELECT COUNT(*) AS total FROM Student WHERE location_id = %s"
                cursor.execute(count_query, (location_id,))
                total_students = cursor.fetchone()['total']

                if total_students == 0:
                    flash("No students in your location.")
                    return render_template('home.html', user=user, students=[], page=page, total_pages=0)

                query = """SELECT s.student_name, sch.school_name, g.grade_year, s.student_id
                            FROM Student s
                            LEFT JOIN Student_school_grade ssg ON s.student_id = ssg.student_id
                            LEFT JOIN School sch ON ssg.school_id = sch.school_id
                            LEFT JOIN Grade g ON ssg.grade_id = g.grade_id
                            WHERE s.location_id = %s
                            LIMIT %s OFFSET %s;
                            """
                # query = "SELECT * FROM Student WHERE location_id = %s "
                cursor.execute(query, (location_id,per_page, offset))
                students = cursor.fetchall()
        
                total_pages = (total_students + per_page - 1) // per_page
                
                return render_template('home.html', user=user, students=students,page=page, total_pages=total_pages)

                   

            except mysql.connector.Error as err:
                return f"Database error: {err}"

            finally:
                if connection.is_connected():
                    cursor.close()  
                    connection.close()

        else:
            flash("You need to log in to view this page.")
            return redirect(url_for('auth.login'))
    return render_template('home.html', user=user)

@app.route('/volunteer_profile')
@login_required
def volunteer_profile():
    if 'user' in session:
        user = session['user']
        location_id = session['location']
        volunteer_id = session['user_id']

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            query = """SELECT v.volunteer_id, v.volunteer_name, v.volunteer_contact, 
                              v.volunteer_email, v.volunteer_address, l.location_name 
                       FROM Volunteer v
                       LEFT JOIN Location l ON v.location_id = l.location_id
                       WHERE v.volunteer_id = %s"""
            cursor.execute(query, (volunteer_id,))
            volunteer = cursor.fetchone()

            query = """SELECT subject_name
                       FROM Subject
                       WHERE volunteer_id = %s"""
            cursor.execute(query, (volunteer_id,))
            volunteer_subjects = cursor.fetchall()

            if not volunteer:
                return render_template('404.html'), 404

            return render_template('volunteer_profile.html', volunteer=volunteer,user = user, 
                                   volunteer_subjects=volunteer_subjects)

        except mysql.connector.Error as err:
            return f"Error fetching volunteer profile: {err}"

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# @app.route('/edit_volunteer/<int:volunteer_id>', methods=['GET', 'POST'])
# def edit_volunteer(volunteer_id):
#     if 'user' in session:
#         user = session['user']
#         location_id = session['location']

#         try:
#             if request.method == 'POST':
#                 volunteer_contact = request.form['volunteer_contact']
#                 volunteer_email = request.form['volunteer_email']
#                 volunteer_address = request.form.get('volunteer_address', '')
#                 location_id = request.form.get('location_id')

#                 profile_picture = request.files.get('profile_picture')
#                 if profile_picture:
#                     picture_path = os.path.join('static/uploads', f'volunteer_{volunteer_id}_profile.jpg')
#                     profile_picture.save(picture_path)

#                 connection = get_db_connection()
#                 cursor = connection.cursor()
#                 cursor.execute("""
#                     UPDATE Volunteer
#                     SET volunteer_contact = %s, 
#                         volunteer_email = %s, volunteer_address = %s, 
#                         location_id = %s
#                     WHERE volunteer_id = %s
#                 """, (volunteer_contact, volunteer_email, volunteer_address, location_id, volunteer_id))
#                 connection.commit()

#                 return redirect(url_for('volunteer_profile', volunteer_id=volunteer_id))

#             connection = get_db_connection()
#             cursor = connection.cursor(dictionary=True)

#             cursor.execute("SELECT * FROM Volunteer WHERE volunteer_id = %s", (volunteer_id,))
#             volunteer = cursor.fetchone()

#             cursor.execute("SELECT * FROM Location")
#             locations = cursor.fetchall()

#             return render_template('edit_volunteer.html',user= user, volunteer=volunteer, locations=locations )

#         except mysql.connector.Error as err:
#             return f"Error fetching volunteer profile: {err}"

#         finally:
#             if connection.is_connected():
#                 cursor.close()
#                 connection.close()

@app.route('/edit_volunteer/<int:volunteer_id>', methods=['GET', 'POST'])
def edit_volunteer(volunteer_id):
    if 'user' not in session:
        # If 'user' is not in session, redirect to the login page
        return redirect(url_for('auth.login'))

    user = session['user']
    location_id = session['location']

    try:
        if request.method == 'POST':
            volunteer_contact = request.form['volunteer_contact']
            volunteer_email = request.form['volunteer_email']
            volunteer_address = request.form.get('volunteer_address', '')
            location_id = request.form.get('location_id')

            profile_picture = request.files.get('profile_picture')
            if profile_picture:
                picture_path = os.path.join('static/uploads', f'volunteer_{volunteer_id}_profile.jpg')
                profile_picture.save(picture_path)

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Volunteer
                SET volunteer_contact = %s, 
                    volunteer_email = %s, volunteer_address = %s, 
                    location_id = %s
                WHERE volunteer_id = %s
            """, (volunteer_contact, volunteer_email, volunteer_address, location_id, volunteer_id))
            connection.commit()

            return redirect(url_for('volunteer_profile', volunteer_id=volunteer_id))

        # GET request: Fetch volunteer data
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Volunteer WHERE volunteer_id = %s", (volunteer_id,))
        volunteer = cursor.fetchone()

        if not volunteer:
            # If the volunteer is not found, return a 404 or error page
            return f"Volunteer with ID {volunteer_id} not found.", 404

        cursor.execute("SELECT * FROM Location")
        locations = cursor.fetchall()

        return render_template('edit_volunteer.html', user=user, volunteer=volunteer, locations=locations)

    except mysql.connector.Error as err:
        # Handle database errors with a valid response
        return f"Error fetching volunteer profile: {err}", 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/poc_home', methods=['GET', 'POST'])
@login_required
def poc_home():
    if request.method == 'GET':
        print("Session content:", session)  # This will show the session contents in the console
        if 'user' in session:
            user = session['user']
            location_id = session['location']


            try:
                page=request.args.get('page',1,type=int)
                per_page=6
                offset=(page-1)*per_page


                connection = get_db_connection()
                cursor = connection.cursor(dictionary=True)

                # Get total count of students
                count_query = "SELECT COUNT(*) AS total FROM Student WHERE location_id = %s"
                cursor.execute(count_query, (location_id,))
                total_students = cursor.fetchone()['total']

                if total_students == 0:
                    flash("No students in your location.")
                    return render_template('home.html', user=user, students=[], page=page, total_pages=0)

                query = """SELECT s.student_name, sch.school_name, g.grade_year, s.student_id
                            FROM Student s
                            LEFT JOIN Student_school_grade ssg ON s.student_id = ssg.student_id
                            LEFT JOIN School sch ON ssg.school_id = sch.school_id
                            LEFT JOIN Grade g ON ssg.grade_id = g.grade_id
                            WHERE s.location_id = %s
                            LIMIT %s OFFSET %s;
                            """
                # query = "SELECT * FROM Student WHERE location_id = %s "
                cursor.execute(query, (location_id,per_page, offset))
                students = cursor.fetchall()
        
                total_pages = (total_students + per_page - 1) // per_page
                
                return render_template('home.html', user=user, students=students,page=page, total_pages=total_pages)

                   

            except mysql.connector.Error as err:
                return f"Database error: {err}"

            finally:
                if connection.is_connected():
                    cursor.close()  
                    connection.close()

        else:
            flash("You need to log in to view this page.")
            return redirect(url_for('auth.login'))
    return render_template('home.html', user=user)


@app.route('/Dashboard')
@login_required
def Dashboard():
    return render_template('dashboard.html')

@app.context_processor
def utility_processor():
    def file_exists(filepath):
        return os.path.exists(filepath)
    return dict(file_exists=file_exists)

if __name__ == '__main__':
    app.run(debug=True)