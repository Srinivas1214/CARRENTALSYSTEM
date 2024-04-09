from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime
import logging


app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
mydb = mysql.connector.connect(
    host='141.209.241.91',
    database='sakila_g5',
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
    cursor.execute("SELECT USERNAME FROM LOGIN_INFO WHERE USERNAME=%s AND PASSWORD=%s", (username, password))
    user = cursor.fetchone()

    if user:
        session['username'] = user[0]
        return redirect('/dashboard')
    else:
        error_message = "Login Failed. Invalid username or password."
        return render_template('index.html', error_message=error_message)
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        dob = request.form['dob']
        gender = request.form['gender']
        phonenumber = request.form['phonenumber']
        email = request.form['email']
        licNumber = request.form['licNumber']
        licExpDate = request.form['licExpDate']
        address1 = request.form['address1']
        address2 = request.form['address2']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']

        username = firstname + lastname
        password = request.form['password']
        try:
            cursor = mydb.cursor()
            cursor.execute("insert into LOGIN_INFO (USERNAME, PASSWORD) values (%s, %s);",(username, password))
            mydb.commit()

            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM LOGIN_INFO WHERE USERNAME="+ "'"+ username + "'")
            cus_id = cursor.fetchone()
           
            cursor.execute("INSERT INTO CUSTOMER (CUSTOMER_ID, FIRST_NAME, LAST_NAME, DOB, GENDER, PHONE_NUMBER, EMAIL_ID, LICENCE_NO, LICENCE_EXPIRY_DATE, ADDRESS_LINE_1, ADDRESE_LINE_2, CITY, STATE, ZIP_CODE) VALUES ( %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s, %s, %s)",
                           (cus_id[0], firstname, lastname, dob, gender, phonenumber, email, licNumber, licExpDate, address1, address2, city, state, zipcode))

            mydb.commit()
            return redirect('/')
        except Exception as Argument:
            logging.exception("Error occurred while printing GeeksforGeeks") 
            return "Username already exists."

def gatDate(date_string):
    current_format = "%m-%d-%Y"
    date_object = datetime.strptime(date_string, current_format)
    desired_format = "%Y-%m-%d"
    return date_object.strftime(desired_format)


@app.route('/dashboard')
def dashboard():
    cursor = mydb.cursor()
    if 'username' in session:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        cursor.execute("SELECT * FROM VEHICLE LIMIT %s OFFSET %s", (per_page, offset))
        vehicles = cursor.fetchall()

        # Check if there are more results
        cursor.execute("SELECT COUNT(*) FROM VEHICLE")
        total_records = cursor.fetchone()[0]
        has_next = (offset + per_page) < total_records
        has_prev = page > 1

        return render_template('dashboard.html', vehicles=vehicles, page=page, per_page=per_page, has_next=has_next, has_prev=has_prev)
        

    else:
        return redirect('/')
    
@app.route('/reservations')
def reservations():
    cursor = mydb.cursor()
    if 'username' in session:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        cursor.execute("SELECT * FROM RESERVATION LIMIT %s OFFSET %s", (per_page, offset))
        reservations = cursor.fetchall()

        # Check if there are more results
        cursor.execute("SELECT COUNT(*) FROM RESERVATION")
        total_records = cursor.fetchone()[0]
        has_next = (offset + per_page) < total_records
        has_prev = page > 1

        return render_template('reservations.html', reservations=reservations, page=page, per_page=per_page, has_next=has_next, has_prev=has_prev)
        

    else:
        return redirect('/')

@app.route('/reservation/<int:reservation_id>')
def reservation(reservation_id):
    # Fetching individual record details
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM RESERVATION WHERE RESERVATION_ID = %s", (reservation_id,))
    reservation_details = cursor.fetchone()
    if reservation_details:
        return render_template('reservationdetails.html', reservation=reservation_details)
    else:
        return "Vehicle not found"
    
@app.route('/vehicle/<int:vehicle_id>')
def vehicle(vehicle_id):
    # Fetching individual record details
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM VEHICLE WHERE VEHICLE_ID = %s", (vehicle_id,))
    vehicle_details = cursor.fetchone()
    if vehicle_details:
        return render_template('vehicle.html', vehicle=vehicle_details)
    else:
        return "Vehicle not found"

if __name__ == '__main__':
    app.run(debug=True)
