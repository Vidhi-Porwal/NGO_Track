from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from functools import wraps
import mysql.connector

# Define a Blueprint for auth-related routes
auth_bp = Blueprint('auth', __name__)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vidhi@3112",
        database="rha"
    )


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
                    flash("Phone No. already registered.")
                    return redirect(url_for('auth.login'))
                 
                else:
                    print (location_id)
                    query = """INSERT INTO Volunteer (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id) VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query, (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id))
                    connection.commit()
                    return redirect(url_for("auth.login"))

            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

        flash(error)

    return render_template('signup.html', location = location)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_no = request.form.get('phone_no')  # Use .get() to avoid KeyError
        password = request.form['password']

        # Check credentials in the database
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM Volunteer WHERE volunteer_contact = %s AND volunteer_password = %s"
            cursor.execute(query, (phone_no, password))
            user = cursor.fetchone()

            if user:
                session['user'] = user['volunteer_name']
                session['location'] = user['location_id']
                session['user_id'] = user['volunteer_id']
                return redirect(url_for('home'))

            else:
                flash("Invalid Phone No. or Password. Please try again.")
                return redirect(url_for('auth.login'))

        except mysql.connector.Error as err:
            return f"Database error: {err}"

        finally:
            if connection.is_connected():
                cursor.close()  
                connection.close()

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))

