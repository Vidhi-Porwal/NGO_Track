from math import ceil
from flask import Flask, flash, render_template, request, session, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'DEV'  # Set a secret key for session management

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vidhi@3112",
        database="rha"
    )

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/Location')
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # phone_no = request.form['phone_no']
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
                session['phone_no'] = user['volunteer_contact']
                return redirect(url_for('dashboard'))
                # return render_template('signup.html')
            else:
                return "Invalid Phone No. or Password. Please try again."
        except mysql.connector.Error as err:
            return f"Database error: {err}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('login.html')

@app.route('/home')
def home():
     # If the user is logged in, render the personalized homepage
    if 'user' in session:
        user = session['user']
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # to get location name and data from database
    if request.method == 'GET':
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT location_id, location_name from Location")  
        location=cursor.fetchall()

    # to add new user to database
    if request.method == 'POST':
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

                if user :
                    error = f"User {volunteer_name} is already registered."
                    return redirect(url_for('signup'))
                    
                else:
                    query = "INSERT INTO Volunteer WHERE volunteer_name = %s AND volunteer_contact = %s AND volunteer_password = %s AND volunteer_email = %s AND volunteer_address = %s AND location_id = %s"
                    cursor.execute(query, (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id ))
                    return redirect(url_for("login"))

            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        flash(error)

        
    return render_template('signup.html', location = location)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from the session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)