# import mysql.connector
# from mysql.connector import Error
# from faker import Faker
# import random

# # Initialize Faker
# fake = Faker()

# def create_connection(host_name, user_name, user_password, db_name):
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#             host=host_name,
#             user=user_name,
#             password=user_password,
#             database=db_name
#         )
#         print("Connection to MySQL DB successful")
#     except Error as e:
#         print(f"The error '{e}' occurred")

#     return connection

# def execute_query(connection, query):
#     cursor = connection.cursor()
#     try:
#         cursor.execute(query)
#         connection.commit()
#         print("Query executed successfully")
#     except Error as e:
#         print(f"The error '{e}' occurred")

# def insert_location(connection):
#     location_name = fake.city()
#     location_address = fake.address().replace("\n", ", ")
#     location_capacity = random.randint(50, 200)
#     location_POC = fake.name()
#     location_POC_contact = fake.phone_number()

#     query = f"""
#     INSERT INTO Location (location_name, location_address, location_capacity, location_POC, location_POC_contact)
#     VALUES ('{location_name}', '{location_address}', {location_capacity}, '{location_POC}', '{location_POC_contact}');
#     """
    
#     execute_query(connection, query)

# def insert_school(connection):
#     school_name = fake.company()
#     school_address = fake.address().replace("\n", ", ")

#     query = f"""
#     INSERT INTO School (school_name, school_address)
#     VALUES ('{school_name}', '{school_address}');
#     """
    
#     execute_query(connection, query)

# def insert_grade(connection):
#     """ Insert a grade entry and return its ID """
#     grade_strength = random.randint(10, 40)
#     grade_year = fake.year()

#     query = f"""
#     INSERT INTO Grade (grade_strength, grade_year)
#     VALUES ({grade_strength}, '{grade_year}');
#     """
    
#     execute_query(connection, query)

# def insert_volunteer(connection, location_id):
#     """ Insert a volunteer entry """
#     volunteer_name = fake.name()
#     volunteer_contact = fake.phone_number()
#     volunteer_password = fake.password()
#     volunteer_email = fake.email()
#     volunteer_address = fake.address().replace("\n", ", ")

#     query = f"""
#     INSERT INTO Volunteer (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id)
#     VALUES ('{volunteer_name}', '{volunteer_contact}', '{volunteer_password}', '{volunteer_email}', '{volunteer_address}', {location_id});
#     """
    
#     execute_query(connection, query)

# def insert_student(connection):
#     student_name = fake.name()
#     student_age = random.randint(5, 18)
#     parent_name = fake.name()
#     parent_contact = fake.phone_number()
    
#     student_documentation = random.choice(['Birth Certificate', 'Report Card', 'ID Card', None])

#     school_id = random.randint(1, 10)  # Adjust this based on actual school entries
#     location_id = random.randint(1, 10)  # Adjust this based on actual location entries

#     query = f"""
#     INSERT INTO Student (student_name, student_age, parent_name, parent_contact, student_documentation, location_id, school_id)
#     VALUES ('{student_name}', {student_age}, '{parent_name}', '{parent_contact}', '{student_documentation}', {location_id}, {school_id});
#     """
    
#     execute_query(connection, query)

# def insert_subject(connection):
#     subject_name = fake.word().capitalize()
    
#     volunteer_id = random.randint(1, 100)

#     query = f"""
#     INSERT INTO Subject (subject_name, volunteer_id)
#     VALUES ('{subject_name}', {volunteer_id});
#     """
    
#     execute_query(connection, query)

# def insert_student_subject(connection):
#    """ Insert entries into the Student_Subject table """
#    # Randomly select existing student and subject IDs
#    student_id = random.randint(1, 500)  # Assuming 500 students are created
#    subject_id = random.randint(1, 100)   # Assuming 100 subjects are created
#    subject_score = random.uniform(0.0, 100.0)  # Random score between 0 and 100
#    subject_progress = fake.sentence()

#    query = f"""
#    INSERT INTO Student_Subject (student_id, subject_id, subject_score, subject_progress)
#    VALUES ({student_id}, {subject_id}, {subject_score}, '{subject_progress}');
#    """

#    execute_query(connection, query)

# def insert_student_school_grade(connection):
#    """ Insert entries into the Student_school_grade table """
#    # Randomly select existing student and school IDs
#    student_id = random.randint(1, 500)  # Assuming 500 students are created
#    school_id = random.randint(1, 10)     # Assuming 10 schools are created
#    grade_id = random.randint(1, 100)     # Assuming grades have been created

#    query = f"""
#    INSERT INTO Student_school_grade (student_id, school_id, grade_id)
#    VALUES ({student_id}, {school_id}, {grade_id});
#    """

#    execute_query(connection, query)

# def main():
#    # Database credentials
#     host = "localhost"
#     user = "root"
#     password = "Vidhi@3112"
#     database = "rha"


#     conn = create_connection(host, user, password, database)

#     for _ in range(10):  # Create 10 locations for example
#        insert_location(conn)

#     for _ in range(10):  # Create 10 schools for example
#        insert_school(conn)

#     for _ in range(10):  # Create 100 grades for example
#        insert_grade(conn)

#     for _ in range(100):  # Create 100 volunteers
#        location_id = random.randint(1, 10)  # Randomly assign to one of the created locations
#        insert_volunteer(conn, location_id)

#     for _ in range(500):  # Create 500 students
#        insert_student(conn)

#     for _ in range(100):  # Create 100 subjects linked to volunteers
#        insert_subject(conn)

#     for _ in range(500):  # Create relationships for each student with subjects.
#        insert_student_subject(conn)

#     for _ in range(500):  
#        insert_student_school_grade(conn)

# if __name__ == "__main__":
#    main()


# import random
# from faker import Faker
# import mysql.connector


# fake = Faker()


# connection = mysql.connector.connect(
#     host = "localhost",
#     user = "root",
#     password = "Vidhi@3112",
#     database = "rha",
#     ssl_disabled=True
# )

# cursor = connection.cursor()

# def get_record_count(table_name):
#     cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
#     return cursor.fetchone()[0]

# if get_record_count("Location") < num_records:
#     location_ids = []
#     for _ in range(10):
#         location_name = fake.city()
#         location_address = fake.address().replace("\n", ", ")
#         location_capacity = random.randint(50, 200)
#         location_POC = fake.name()
#         location_POC_contact = fake.phone_number()

#          cursor.execute("""
#             INSERT INTO Location (location_name, location_address, location_capacity, location_POC, location_POC_contact)
#             VALUES (%s, %s, %s, %s, %s)
#         """, (location_name, location_address, location_capacity, location_POC, location_POC_contact))
#         location_ids.append(cursor.lastrowid)
# connection.commit()

import random
from faker import Faker
import mysql.connector
from mysql.connector import Error

# Initialize Faker
fake = Faker()

def create_connection(host_name, user_name, user_password, db_name):
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

def execute_query(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

# Function to insert Location data
def insert_location(connection):
    location_name = fake.city()
    location_address = fake.address().replace("\n", ", ")
    location_capacity = random.randint(50, 200)
    location_POC = fake.name()
    location_POC_contact = fake.phone_number()

    query = """
    INSERT INTO Location (location_name, location_address, location_capacity, location_POC, location_POC_contact)
    VALUES (%s, %s, %s, %s, %s);
    """
    data = (location_name, location_address, location_capacity, location_POC, location_POC_contact)
    execute_query(connection, query, data)

# Function to insert School data
def insert_school(connection):
    school_name = fake.company()
    school_address = fake.address().replace("\n", ", ")

    query = """
    INSERT INTO School (school_name, school_address)
    VALUES (%s, %s);
    """
    data = (school_name, school_address)
    execute_query(connection, query, data)

# Function to insert Grade data
def insert_grade(connection):
    grade_strength = random.randint(10, 40)
    grade_year = fake.year()

    query = """
    INSERT INTO Grade (grade_strength, grade_year)
    VALUES (%s, %s);
    """
    data = (grade_strength, grade_year)
    execute_query(connection, query, data)

# Function to insert Volunteer data
def insert_volunteer(connection, location_id):
    volunteer_name = fake.name()
    volunteer_contact = fake.phone_number()
    volunteer_password = fake.password()
    volunteer_email = fake.email()
    volunteer_address = fake.address().replace("\n", ", ")

    query = """
    INSERT INTO Volunteer (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    data = (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id)
    execute_query(connection, query, data)

# Function to insert Student data
def insert_student(connection):
    student_name = fake.name()
    student_age = random.randint(5, 18)
    parent_name = fake.name()
    parent_contact = fake.phone_number()

    student_documentation = random.choice(['Birth Certificate', 'Report Card', 'ID Card', None])

    school_id = random.randint(1, 10)  # Adjust based on the number of schools in your DB
    location_id = random.randint(1, 10)  # Adjust based on actual location entries

    query = """
    INSERT INTO Student (student_name, student_age, parent_name, parent_contact, student_documentation, location_id, school_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    data = (student_name, student_age, parent_name, parent_contact, student_documentation, location_id, school_id)
    execute_query(connection, query, data)

# Function to insert Subject data
def insert_subject(connection):
    subject_name = fake.word().capitalize()

    volunteer_id = random.randint(1, 200)  # Adjust based on actual volunteers

    query = """
    INSERT INTO Subject (subject_name, volunteer_id)
    VALUES (%s, %s);
    """
    data = (subject_name, volunteer_id)
    execute_query(connection, query, data)

# Function to insert Student_Subject data (many-to-many relationship)
def insert_student_subject(connection):
    student_id = random.randint(1, 500)  # Assuming 500 students have been created
    subject_id = random.randint(1, 25)  # Assuming 100 subjects
    subject_score = random.uniform(0.0, 100.0)  # Random score
    subject_progress = fake.sentence()

    query = """
    INSERT INTO Student_Subject (student_id, subject_id, subject_score, subject_progress)
    VALUES (%s, %s, %s, %s);
    """
    data = (student_id, subject_id, subject_score, subject_progress)
    execute_query(connection, query, data)

# Function to insert Student_School_Grade data (many-to-many relationship)
def insert_student_school_grade(connection):
    student_id = random.randint(1, 500)  # Assuming 500 students have been created
    school_id = random.randint(1, 10)    # Assuming 10 schools
    grade_id = random.randint(1, 10)    # Assuming 10 grades

    query = """
    INSERT INTO Student_school_grade (student_id, school_id, grade_id)
    VALUES (%s, %s, %s);
    """
    data = (student_id, school_id, grade_id)
    execute_query(connection, query, data)

# Main function to insert data for multiple tables
def main():
    # Database credentials
    host = "localhost"
    user = "root"
    password = "Vidhi@3112"
    database = "rha"

    # Establish connection
    conn = create_connection(host, user, password, database)

    # Insert data into Location, School, Grade, etc.
    for _ in range(10):  # Insert 10 Locations
        insert_location(conn)

    for _ in range(10):  # Insert 10 Schools
        insert_school(conn)

    for _ in range(10):  # Insert 10 Grades
        insert_grade(conn)

    for _ in range(200):  # Insert 50 Volunteers (assuming each is linked to a location)
        location_id = random.randint(1, 10)
        insert_volunteer(conn, location_id)

    for _ in range(500):  # Insert 200 Students
        insert_student(conn)

    for _ in range(25):  # Insert 100 Subjects
        insert_subject(conn)

    for _ in range(300):  # Link 300 students to subjects
        insert_student_subject(conn)

    for _ in range(300):  # Link 300 students to schools and grades
        insert_student_school_grade(conn)

    print("Data insertion completed successfully!")

# Run the main function
if __name__ == "__main__":
    main()
