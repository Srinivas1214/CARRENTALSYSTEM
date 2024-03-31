from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
mydb = mysql.connector.connect(
    host='141.209.241.91',
    database='sp2024bis698g5s',
    user='sp2024bis698g5',
    password='warm'
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM LOGIN_INFO WHERE USER_ID=%s AND PASSWORD=%s", (username, password))
    user = cursor.fetchone()

    if user:
        session['username'] = user[1]
        return redirect('/dashboard')
    else:
        return "Login Failed. Invalid username or password."
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb.cursor()
        try:
            cursor.execute("INSERT INTO LOGIN_INFO (USER_ID, PASSWORD) VALUES (%s, %s)", (username, password))
            mydb.commit()
            return redirect('/')
        except mysql.connector.IntegrityError:
            return "Username already exists."

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome, {session['username']}! You are logged in."
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
