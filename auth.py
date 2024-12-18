from flask import Flask, Blueprint, request, render_template, redirect, url_for, session, flash
from functools import wraps
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
import re
import uuid



app = Flask(__name__)
app.secret_key = 'DEV' 
# Define a Blueprint for auth-related routes
auth_bp = Blueprint('auth', __name__)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vidhi@3112",
        database="rha"
    )

def ValidPassword(volunteer_password):
    pattern = "^(?=.?[A-Z])(?=.?[a-z])(?=.?[0-9])(?=.?[#?!@$%^&*-]).{8,}$"
    return re.match(pattern, volunteer_password)




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  # Check for 'user' session key
            flash("You need to be logged in to access this page.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # to get location name and data from database
    if request.method == 'GET':
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT location_id, location_name from Location")  
        location=cursor.fetchall()

    # to add new user to database
    if request.method == 'POST':
        # import pdb; pdb.set_trace()
        volunteer_name = request.form['name']
        volunteer_contact = request.form['contact']
        volunteer_email = request.form['email']
        volunteer_address = request.form['address']
        volunteer_password = request.form['password']
        location_id = request.form['location_dropdown']
        error = None

        if not volunteer_name:
            error = 'Name is required.' 
        elif not volunteer_contact:
            error = 'Contact is required.'
        elif not volunteer_email:
            error = 'Email is required.'
        elif not volunteer_address:
            error = 'address is required.'
        elif not volunteer_password:
            error = 'Password is required.'
        elif not location_id:
            error = 'Choose a location.'
        elif not valid_password(volunteer_password):
            error = 'Password must include uppercase, lowercase, number, and special character.'
    

        else:
            if error is None :
                try:
                    connection = get_db_connection()
                    cursor = connection.cursor(dictionary=True)
                    query = "SELECT * FROM Volunteer WHERE volunteer_contact = %s"
                    cursor.execute(query, (volunteer_contact,))
                    user = cursor.fetchone()
                    # import pdb; pdb.set_trace()
                    if user :
                        # error = f"User {volunteer_name} is already registered."
                        flash("Phone number already registered. Please log in.", 'error')
                        return redirect(url_for('auth.login'))
                     
                    else:
                        print (location_id)
                        query = """INSERT INTO Volunteer (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id) VALUES (%s, %s, %s, %s, %s, %s)"""
                        cursor.execute(query, (volunteer_name, volunteer_contact, generate_password_hash(volunteer_password), volunteer_email, volunteer_address, location_id))
                        connection.commit()
                        return redirect(url_for("auth.login"))

                except mysql.connector.Error as err:
                    flash(f"Database error: {err}", "error")

                finally:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()

        flash(error)

    return render_template('signup.html', location = location)


@app.before_request
def check_session():
    if 'user_id' in session and 'session_id' in session:
        user_id = session['user_id']
        session_id = session['session_id']

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            
            cursor.execute("SELECT session_id FROM Volunteer WHERE volunteer_id = %s", (user_id,))
            db_session = cursor.fetchone()
            print(db_session)

            if not db_session or db_session['session_id'] != session_id:
                session.clear()  # Clear session data
                flash("You have been logged out because your account was logged in from another location.", "warning")
                return redirect(url_for('auth.login'))

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
            session.clear()
            return redirect(url_for('auth.login'))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()





@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_no = request.form.get('phone_no')  # Use .get() to avoid KeyError
        password = request.form['password']
        error = None

        # Check credentials in the database
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM Volunteer WHERE volunteer_contact = %s"
            cursor.execute(query, (phone_no,))
            user = cursor.fetchone()

            if user is None:
                error = 'Incorrect phone number.'
            elif not check_password_hash(user['volunteer_password'], password):
                error = 'Incorrect password.'

            if error is None:
                session_id = str(uuid.uuid4())
                print('New session ID:' ,session_id)
                cursor.execute("UPDATE Volunteer SET session_id = %s WHERE volunteer_id = %s", (session_id, user['volunteer_id']))
                connection.commit()

                session['user'] = user['volunteer_name']
                session['location'] = user['location_id']
                session['user_id'] = user['volunteer_id']
                session['session_id'] = session_id
                print('session saved in browser:' ,session)

                return redirect(url_for('home'))
            else:
                flash(error)

        except mysql.connector.Error as err:
            flash(f"Database error: {err}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""UPDATE Volunteer SET session_id = NULL WHERE volunteer_id = %s""" ,(user_id,))
    connection.commit()
    cursor.close()
    connection.close()


    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))

