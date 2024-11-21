from math import ceil
from flask import Flask, render_template, request, session, redirect, url_for
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

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from the session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)