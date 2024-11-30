from math import ceil
from flask import Flask, flash, render_template, request, session, redirect, url_for
from auth import auth_bp, get_db_connection, login_required
import mysql.connector


app = Flask(__name__)
app.secret_key = 'DEV'  # Set a secret key for session management

app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/Location')
@login_required
def Location():
    page=request.args.get('page',1,type=int)
    per_page=5
    offset=(page-1)*per_page   #starting point for current page
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total from Location")  #total no of rows in location table
    total=cursor.fetchone()['total']

    cursor.execute("SELECT * FROM Location LIMIT %s OFFSET %s",(per_page,offset))
    location = cursor.fetchall()
    cursor.close()
    connection.close()
    total_pages = ceil(total / per_page)

    return render_template('location.html', location_i=location,page=page, total_pages=total_pages)


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


@app.route('/student_profile/<int:student_id>')
@login_required
def student_profile(student_id):
    if 'user' in session:
        user = session['user']
        location_id = session['location']

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = """SELECT s.student_id , s.student_name , s.student_age , s.parent_name , s.parent_contact , s.student_documentation , sch.school_name , l.location_name , g.grade_year 
                FROM Student s
                LEFT JOIN Student_school_grade ssg ON s.student_id = ssg.student_id
                LEFT JOIN School sch ON ssg.school_id = sch.school_id
                LEFT JOIN Grade g ON ssg.grade_id = g.grade_id
                LEFT JOIN Location l ON s.location_id = l.location_id
                WHERE s.student_id = %s
                """

            cursor.execute(query, (student_id,))
            student = cursor.fetchone()

            if not student:
                return render_template('404.html'), 404
            return render_template('student_profile.html', student=student, user=user)


        except mysql.connector.Error as err:
            return f"Error fetching student profile: {err}"

        finally:
            if connection.is_connected():
                cursor.close()  
                connection.close()
    return render_template('student_profile.html')


if __name__ == '__main__':
    app.run(debug=True)