import mysql.connector
from mysql.connector import Error

def create_connection(host_name, user_name, user_password, db_name):
    """ Create a database connection to the MySQL database """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    """ Execute a single query """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

# Database credentials
host = "localhost"
user = "root"
password = "Vidhi@3112"

database = "rha"

# Create a connection to the database
conn = create_connection(host, user, password, database)

# SQL queries to create tables
create_location_table = """
CREATE TABLE IF NOT EXISTS Location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    location_address VARCHAR(200) NOT NULL UNIQUE,
    location_capacity INT,
    location_POC VARCHAR(100),
    location_POC_contact VARCHAR(100)
);
"""

create_volunteer_table = """
CREATE TABLE IF NOT EXISTS Volunteer (
    volunteer_id INT PRIMARY KEY AUTO_INCREMENT,
    volunteer_name VARCHAR(100) NOT NULL,
    volunteer_contact VARCHAR(100) NOT NULL,
    volunteer_password VARCHAR(255) NOT NULL,
    volunteer_email VARCHAR(100) NOT NULL,
    volunteer_address VARCHAR(100),
    session_id VARCHAR(255),
    location_id INT,
    FOREIGN KEY (location_id) REFERENCES Location(location_id) ON DELETE CASCADE ON UPDATE CASCADE
);
"""
create_school_table = """
CREATE TABLE IF NOT EXISTS School (
    school_id INT PRIMARY KEY AUTO_INCREMENT,
    school_name VARCHAR(100) NOT NULL,
    school_address VARCHAR(100)
);
"""

create_student_table = """
CREATE TABLE IF NOT EXISTS Student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_name VARCHAR(100) NOT NULL,
    student_age INT NOT NULL,
    parent_name VARCHAR(100) NOT NULL,
    parent_contact VARCHAR(100) NOT NULL,
    student_documentation VARCHAR(100),
    location_id INT,
    school_id INT,
    FOREIGN KEY (location_id) REFERENCES Location(location_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (school_id) REFERENCES School(school_id) ON DELETE CASCADE ON UPDATE CASCADE
);
"""

create_grade_table = """
CREATE TABLE IF NOT EXISTS Grade (
    grade_id INT PRIMARY KEY AUTO_INCREMENT,
    grade_strength INT,
    grade_year VARCHAR(100) NOT NULL
);
"""

create_subject_table = """
CREATE TABLE IF NOT EXISTS Subject (
    subject_id INT PRIMARY KEY AUTO_INCREMENT,
    subject_name VARCHAR(100) NOT NULL,
    volunteer_id INT,
    FOREIGN KEY (volunteer_id) REFERENCES Volunteer(volunteer_id) ON DELETE CASCADE ON UPDATE CASCADE
);
"""

create_student_subject_table = """
CREATE TABLE IF NOT EXISTS Student_Subject (
    ss_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    subject_id INT,
    subject_score FLOAT,
    subject_progress TEXT,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE ON UPDATE CASCADE
);
"""

create_student_school_grade_table = """
CREATE TABLE IF NOT EXISTS Student_school_grade (
    ssg_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    school_id INT,
    grade_id INT,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (school_id) REFERENCES School(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (grade_id) REFERENCES Grade(grade_id) ON DELETE CASCADE ON UPDATE CASCADE
);
"""

create_activity_table = """
CREATE TABLE IF NOT EXISTS Activity (
    activity_id INT PRIMARY KEY AUTO_INCREMENT,
    activity_image MEDIUMBLOB,
    activity_title TEXT,
    activity_description TEXT,
    activity_date DATE
);
"""

# Execute table creation queries
execute_query(conn, create_location_table)
execute_query(conn, create_volunteer_table)
execute_query(conn, create_school_table)
execute_query(conn, create_student_table)
execute_query(conn, create_grade_table)
execute_query(conn, create_subject_table)
execute_query(conn, create_student_subject_table)
execute_query(conn, create_student_school_grade_table)
execute_query(conn, create_activity_table)

# Close the connection
if conn.is_connected():
    conn.close()
