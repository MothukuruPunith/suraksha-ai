import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Punith@2005",  # put your mysql password if any
        database="suraksha_ai"
    )