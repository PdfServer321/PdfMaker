from flask import Flask, render_template, redirect, url_for, request, make_response
import database
import datetime
import base64

app = Flask(__name__, template_folder='templates', static_folder='static')
connection, cursor = database.connect()

def get_token(username, password):
    auth_string = f"{username}:{password}"
    token = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    return token

def set_cookie(token):
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    response = make_response(redirect(url_for(".panel")))
    response.set_cookie(key='token', value=token, expires=expires)
    return response

def check_cookie():
    token = request.cookies.get('token')
    return database.is_token_valid(cursor, token)

@app.route('/auto')
def auto():
    if check_cookie(): return render_template("auto.html")
    else: return redirect(url_for(".main"))

@app.route('/contianers')
def contianers():
    if check_cookie(): return render_template("contianers.html")
    else: return redirect(url_for(".main"))

@app.route('/')
def main():
    if check_cookie(): return redirect(url_for(".panel"))
    try: error_msg = request.args.get("error_msg")
    except: error_msg = None
    return render_template("login.html", error_msg=error_msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form["username"]
    password = request.form["password"]
    token = get_token(username, password)
    if database.is_token_valid(cursor, token): return set_cookie(token)
    else: return redirect(url_for(".main", error_msg="Username or password is incorrect"))

@app.route('/panel')
def panel():
    token = request.cookies.get('token')
    if check_cookie(): 
        if database.is_user_types(cursor, token, "('admin', 'superadmin')"): return render_template("panel.html")
        else: return redirect(url_for(".test"))
    else: return redirect(url_for(".main"))

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for(".main")))
    response.delete_cookie('token')
    return response

@app.route('/users')
def users():
    token = request.cookies.get('token')
    if check_cookie():
        if database.is_user_types(cursor, token, "('admin', 'superadmin')"): 
            users = database.get_users(cursor)
            return render_template("users.html", users=users)
        else: return redirect(url_for(".test"))
    else: return redirect(url_for(".main"))

@app.route('/status')
def status():
    token = request.cookies.get('token')
    if check_cookie():
        if database.is_user_types(cursor, token, "('admin', 'superadmin')"): 
            id = request.args.get("id")
            type = request.args.get("type")
            database.change_user_status(connection, cursor, id, type)
            return redirect(url_for(".users"))
        else: return redirect(url_for(".test"))
    else: return redirect(url_for(".main"))

@app.route('/delete')
def delete():
    if check_cookie():
        token = request.cookies.get('token')
        if database.is_user_types(cursor, token, "('admin', 'superadmin')"): 
            id = request.args.get("id")
            database.delete_user(connection, cursor, id)
            return redirect(url_for(".users"))
        else: return redirect(url_for(".test"))
    else: return redirect(url_for(".main"))

@app.route('/add')
def add():
    try: error_msg = request.args.get("error_msg")
    except: error_msg = None
    token = request.cookies.get('token')
    if check_cookie():
        if database.is_user_types(cursor, token, "('admin', 'superadmin')"): 
            return render_template("add.html", error_msg=error_msg)
    else: return redirect(url_for(".main"))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if check_cookie():
        if database.is_user_types(cursor, token, "('admin', 'superadmin')"): 
            username = request.form["username"]
            password = request.form["password"]
            status = request.form["status"]
            token = get_token(username, password)
            if database.is_user_exist(cursor, username): return redirect(url_for(".add", error_msg="User with this login already exist"))
            else:
                database.add_user(connection, cursor, username, token, status) 
                return redirect(url_for(".add", error_msg="User added successfully"))
    else: return redirect(url_for(".main"))

if __name__ == '__main__':
    app.run()