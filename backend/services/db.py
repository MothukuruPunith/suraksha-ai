import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # put your mysql password if any
        database="suraksha_ai"
    )
