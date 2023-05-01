# import sqlite3
import psycopg2

def connect():
    DB_URL = "postgres://wquooiwq:0Q6wYSUi8mBoRF1y3pDSOd3ve95QhHE_@dumbo.db.elephantsql.com/wquooiwq"
    connection = psycopg2.connect(DB_URL, sslmode='require')
    cursor = connection.cursor()
    return connection, cursor

def create_table(cursor, table_name, columns):
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}{columns}""")

def is_token_valid(cursor, token):
    cursor.execute(f"""SELECT token FROM users WHERE token = '{token}'""")
    token = cursor.fetchone()
    if token: return True
    else: return False

def get_users(cursor):
    cursor.execute(f"""SELECT * FROM users""")
    users = cursor.fetchall()
    return users

def add_user(connection, cursor, username, token, status):
    cursor.execute(f'SELECT max(id)+1 FROM users')
    id = cursor.fetchone()[0]
    cursor.execute(f'INSERT INTO users( id, username, token, status ) VALUES ( %s, %s, %s, %s )', ( id, username, token, status ))
    connection.commit()
    
def change_user_status(connection, cursor, id, type):
    cursor.execute(f"""UPDATE users SET status = '{type}' WHERE id = {int(id)}""")
    connection.commit()

def delete_user(connection, cursor, id):
    cursor.execute(f"""DELETE FROM users WHERE id = {id}""")
    connection.commit()

def is_user_types(cursor, token, types):
    cursor.execute(f"""SELECT id FROM users where token = '{token}' and status in {types}""")
    user = cursor.fetchone()
    if user: return True
    else: return False
    
def is_user_exist(cursor, username):
    cursor.execute(f"""SELECT id FROM users WHERE username = '{username}'""")
    id = cursor.fetchone()
    if id: return True
    else: return False