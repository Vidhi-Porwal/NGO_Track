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
        # print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def get_record_count(connection, table_name):
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

def insert_location(connection, num_records):
    Location_ids = []
    cursor = connection.cursor()

    if get_record_count(connection, "Location") < num_records:
        for _ in range(num_records):
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

            # Fetch last inserted ID and append to the list
            Location_ids.append(cursor.lastrowid)
    return Location_ids

def insert_volunteer(connection, Location_ids):
    volunteer_name = fake.name()
    volunteer_contact = fake.phone_number()
    volunteer_password = fake.password()
    volunteer_email = fake.email()
    volunteer_address = fake.address().replace("\n", ", ")
    location_id = random.choice(Location_ids)

    query = """
    INSERT INTO Volunteer (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    data = (volunteer_name, volunteer_contact, volunteer_password, volunteer_email, volunteer_address, location_id)
    execute_query(connection, query, data)



def main():
    # Database credentials
    host = "localhost"
    user = "root"
    password = "Vidhi@3112"
    database = "rha_test"

    # Establish connection
    conn = create_connection(host, user, password, database)

    if conn:
        try:
            # Number of records to insert
            # num_records = 10

            # Insert data into Location
            x = insert_location(conn, 10)

            print("Data insertion completed successfully!")
        finally:
            conn.close()  # Ensure the connection is closed

    # print("Data insertion completed successfully!")

# Run the main function
if __name__ == "__main__":
    main()

### to be completed later