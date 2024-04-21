from flask import Flask, render_template, request, redirect, session, Response
import mysql.connector
from datetime import datetime
import logging
import csv
import io


app = Flask(__name__)
app.secret_key = "your_secret_key1"

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
    cursor.execute("SELECT USERNAME, USER_ID FROM LOGIN_INFO WHERE USERNAME=%s AND PASSWORD=%s", (username, password))
    user = cursor.fetchone()

    cursor.execute("select EMPLOYEE_ID from EMPLOYEE where EMPLOYEE_ID =%s;",(user[1],))
    emp = cursor.fetchone()

    if emp:
        session['emp'] = emp[0]
        return redirect('/reservations')

    if user:
        session['username'] = user[0]
        return redirect('/dashboard')
    else:
        error_message = "Login Failed. Invalid username or password."
        return render_template('index.html', error_message=error_message)

@app.route('/logout')
def logout():
    # Clear the session data
    session.pop('username', None)
    session.pop('emp', None)
    session.clear()
    # Redirect to the login page
    return redirect('/')
    

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
            cursor.execute("SELECT * FROM LOGIN_INFO WHERE USERNAME="+ "'"+ username + "'")
            user = cursor.fetchone()
            if not user or user[0] == 0:
                return render_template('user_created_sucessful.html', username = username)


            cursor.execute("insert into LOGIN_INFO (USERNAME, PASSWORD) values (%s, %s);",(username, password))

            cursor.execute("SELECT * FROM LOGIN_INFO WHERE USERNAME="+ "'"+ username + "'")
            cus_id = cursor.fetchone()
           
            cursor.execute("INSERT INTO CUSTOMER (CUSTOMER_ID, FIRST_NAME, LAST_NAME, DOB, GENDER, PHONE_NUMBER, EMAIL_ID, LICENCE_NO, LICENCE_EXPIRY_DATE, ADDRESS_LINE_1, ADDRESE_LINE_2, CITY, STATE, ZIP_CODE) VALUES ( %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s, %s, %s)",
                           (cus_id[0], firstname, lastname, dob, gender, phonenumber, email, licNumber, licExpDate, address1, address2, city, state, zipcode))

            mydb.commit()
            return render_template('user_created_sucessful.html', username = username)
        except Exception as Argument:
            logging.exception("Error occurred while signup") 
            return "Error occurred while signup please signup again"
        

@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'GET':
        return render_template('add_vehicle.html')
    elif request.method == 'POST':
        try:
            make = request.form['make']
            model = request.form['model']
            year = request.form['year']
            type = request.form['type']
            mileage = request.form['mileage']
            color = request.form['color']
            capacity = request.form['capacity']
            transmission = request.form['transmission']
            mpg = request.form['mpg']
            cargroup = request.form['cargroup']
            price = request.form['price']
            location = request.form['location']

            cursor = mydb.cursor()
            cursor.execute("INSERT INTO VEHICLE (MAKE, MODEL, YEAR, TYPE, MILEAGE, COLOR, STATUS, CAPACITY, TRANSMISSION, MPG, CAR_GROUP, PRICE_PER_DAY, ADDRESS_LOCATED) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                           (make, model, year, type, mileage, color, 'ACTIVE', capacity, transmission, mpg, cargroup, price, location))
            mydb.commit()
            return render_template('veichleadded_sucessful.html')
        except Exception as Argument:
            logging.exception("Error occurred while adding veichle") 
            return "Error occurred while adding veichle please check all fields"


@app.route('/dashboard')
def dashboard():

    cursor = mydb.cursor()
    if 'username' or 'emp' in session:
        page = request.args.get('page', 1, type=int)
        location = request.args.get('location')
        per_page = 10
        offset = (page - 1) * per_page
        is_employee_logged_in='false'

        if 'emp' in session:
            is_employee_logged_in = 'true'

        if location:
            location = int(location)

            cursor.execute("SELECT * FROM VEHICLE WHERE ADDRESS_LOCATED= %s and STATUS='ACTIVE' LIMIT %s OFFSET %s", (location ,per_page, offset))
            vehicles = cursor.fetchall()

            # Check if there are more results
            cursor.execute("SELECT COUNT(*) FROM VEHICLE WHERE ADDRESS_LOCATED=%s and STATUS='ACTIVE'", (location,))
            total_records = cursor.fetchone()[0]
            has_next = (offset + per_page) < total_records
            has_prev = page > 1
        else:
            cursor.execute("SELECT * FROM VEHICLE where STATUS='ACTIVE' LIMIT %s OFFSET %s", (per_page, offset))
            vehicles = cursor.fetchall()

            # Check if there are more results
            cursor.execute("SELECT COUNT(*) FROM VEHICLE where STATUS='ACTIVE'")
            total_records = cursor.fetchone()[0]
            has_next = (offset + per_page) < total_records
            has_prev = page > 1

        return render_template('dashboard.html', vehicles=vehicles, page=page, per_page=per_page, has_next=has_next, has_prev=has_prev, is_employee_logged_in=is_employee_logged_in)
    else:
        return redirect('/')
    
@app.route('/reservations')
def reservations():
    cursor = mydb.cursor()
    is_employee_logged_in='false'

    if 'emp' in session:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        is_employee_logged_in = 'true'

        cursor.execute("SELECT * FROM RESERVATION order by UPDATED_AT DESC LIMIT %s OFFSET %s", (per_page, offset))
        reservations = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM RESERVATION")
        total_records = cursor.fetchone()[0]
        has_next = (offset + per_page) < total_records
        has_prev = page > 1

        return render_template('reservations.html', reservations=reservations, page=page, per_page=per_page, has_next=has_next, has_prev=has_prev, is_employee_logged_in=is_employee_logged_in)
        

    if 'username' in session:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        cursor = mydb.cursor()
        # Get customer id
        cursor.execute("select USER_ID from LOGIN_INFO where USERNAME = %s;",(session['username'],))
        customer_id = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM RESERVATION where CUSTOMER_ID= %s  order by UPDATED_AT DESC LIMIT %s OFFSET %s", (customer_id ,per_page, offset))
        reservations = cursor.fetchall()

        # Check if there are more results
        cursor.execute("SELECT COUNT(*) FROM RESERVATION where CUSTOMER_ID= %s",(customer_id,))
        total_records = cursor.fetchone()[0]
        has_next = (offset + per_page) < total_records
        has_prev = page > 1

        return render_template('reservations.html', reservations=reservations, page=page, per_page=per_page, has_next=has_next, has_prev=has_prev)
        

    else:
        return redirect('/')
    
@app.route('/complete_reservation/<int:reservation_id>' , methods=['POST'])
def completeReservation(reservation_id):
    mileage = request.form['mileage']
    location = request.form['location']

    cursor = mydb.cursor()
    cursor.execute ("update RESERVATION set R_STATUS = 'COMPLETED' where RESERVATION_ID = %s;", (reservation_id,))

    cursor.execute ("select VEHICLE_ID from RESERVATION where RESERVATION_ID = %s;",(reservation_id,))
    vehicle_id = cursor.fetchone()[0]
    
    cursor.execute ("update VEHICLE set STATUS='ACTIVE', MILEAGE = %s, ADDRESS_LOCATED = %s WHERE VEHICLE_ID = %s;",(mileage, location, vehicle_id,))
    mydb.commit()

    return render_template('reservation_completed_sucessful.html')


@app.route('/reservation/<int:reservation_id>')
def reservation(reservation_id):
    # Fetching individual record details
    cursor = mydb.cursor()
    cursor.execute("select R.RESERVATION_ID, CONCAT(C.FIRST_NAME,' ',C.LAST_NAME) AS Name, V.MAKE, V.MODEL, V.YEAR ,R.R_STATUS ,R.PICKUP_LOCATION, R.PICKUP_DATE, R.DROP_LOCATION, R.DROP_DATE, R.PAYMENT_AMOUNT, R.PAYMENT_METHOD from RESERVATION AS R JOIN CUSTOMER C on C.CUSTOMER_ID = R.CUSTOMER_ID JOIN VEHICLE V on R.VEHICLE_ID = V.VEHICLE_ID WHERE R.RESERVATION_ID = %s;", (reservation_id,))
    reservation_details = cursor.fetchone()

    if 'emp' in session:
        if reservation_details:
            return render_template('reservationdetails.html', reservation=reservation_details, is_employee_logged_in='true')
        else:
            return "Vehicle not found"

    if reservation_details:
        return render_template('reservationdetails.html', reservation=reservation_details)
    else:
        return "Vehicle not found"
    
@app.route('/confirm_reservation/<int:reservation_id>', methods=['POST'])
def confirm_reservation(reservation_id):
    cursor = mydb.cursor()

    cursor.execute("select VEHICLE_ID from RESERVATION where RESERVATION_ID= %s;",(reservation_id,))
    vehicle_id = cursor.fetchone()[0]

    cursor.execute("update VEHICLE set STATUS='IN-RESERVATION' WHERE VEHICLE_ID = %s;", (vehicle_id,))

    cursor.execute("update RESERVATION set R_STATUS = 'IN_PROGRESS' where RESERVATION_ID = %s;",(reservation_id,))
    
    mydb.commit()
    return render_template('checkedin_sucessful.html')
    
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

@app.route('/remove_vehicle/<int:vehicle_id>', methods=['POST'])
def remove_vehicle(vehicle_id):
    cursor = mydb.cursor()
    cursor.execute("update VEHICLE set STATUS='INACTIVE' WHERE VEHICLE_ID = %s", (vehicle_id,))
    mydb.commit()
    return render_template('vehicle_removed_successfully.html')
    
@app.route('/register')
def register():
    return render_template('register.html')
    
@app.route('/make_reservation/<int:vehicle_id>', methods=['GET', 'POST'])
def make_reservation(vehicle_id):
    if 'username' not in session:
        return redirect('/')

    if request.method == 'POST':
        pickup_date = request.form['pickup_date']
        drop_date = request.form['drop_date']
        drop_location = request.form['drop_location']
        comments = request.form['comments']
        price = request.form['price']
        payment_method = request.form['payment_method']
        # Add more form fields as needed above

        cursor = mydb.cursor()

        # Get Veichle info
        cursor.execute("SELECT * FROM VEHICLE WHERE VEHICLE_ID = %s", (vehicle_id,))
        vehicle_details = cursor.fetchone()

        # Get customer id
        cursor.execute("select USER_ID from LOGIN_INFO where USERNAME = %s;",(session['username'],))
        customer_id = cursor.fetchone()[0]

        # Insert the reservation details into the database
        cursor.execute("insert into RESERVATION (CUSTOMER_ID, PICKUP_DATE, PICKUP_LOCATION, DROP_DATE, DROP_LOCATION, R_STATUS, VEHICLE_ID, TRIP_TYPE, COMMENTS, PAYMENT_AMOUNT,PAYMENT_METHOD) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (customer_id, pickup_date, vehicle_details[13], drop_date ,drop_location, 'RESERVED',  vehicle_id, 'SHORT_TERM', comments, price, payment_method))
        
        cursor.execute("update VEHICLE set STATUS='IN-RESERVATION' WHERE VEHICLE_ID = %s;",(vehicle_id,))

        mydb.commit()
        return render_template('reservation_sucessful.html')

    # Fetch vehicle details to display on reservation page
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM VEHICLE WHERE VEHICLE_ID = %s", (vehicle_id,))
    vehicle_details = cursor.fetchone()
    if vehicle_details:
        return render_template('make_reservation.html', vehicle=vehicle_details)
    else:
        return "Vehicle not found"

@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    cursor = mydb.cursor()
    cursor.execute("update RESERVATION set R_STATUS = 'CANCELLED' where RESERVATION_ID = %s;", (reservation_id,))
    
    cursor.execute("select VEHICLE_ID from RESERVATION where RESERVATION_ID= %s;",(reservation_id,))
    vehicle_id = cursor.fetchone()[0]
    
    cursor.execute("update VEHICLE set STATUS='ACTIVE' WHERE VEHICLE_ID = %s;",(vehicle_id,))
    mydb.commit()
    return render_template('cancel_sucessful.html')

@app.route('/export_vehicles')
def export_vehicles():
    cursor = mydb.cursor()

    cursor.execute("SELECT MAKE, MODEL, YEAR, TYPE, MILEAGE ,COLOR, MPG, TRANSMISSION, CAR_GROUP, CAPACITY, RL.LOCATION_NAME FROM VEHICLE join RENTAL_LOCATION RL on RL.RENTAL_LOCATION_ID = VEHICLE.ADDRESS_LOCATED;")
    vehicles = cursor.fetchall()

    # Generate CSV file
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Make', 'Model', 'Year', 'Type', 'Mileage' ,'Color', 'Mpg', 'Transmission', 'Car Group', 'Capasity' ,'Location'])
    writer.writerows(vehicles)

    # Return CSV file as response
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=vehicles.csv"}
    )

@app.route('/export_reservations')
def export_reservations():
    cursor = mydb.cursor()

    cursor.execute("SELECT RESERVATION_ID, C.FIRST_NAME, C.LAST_NAME, V.MAKE, V.MODEL, RESERVATION.CREATED_AT ,PICKUP_DATE, DROP_DATE, PAYMENT_AMOUNT, PAYMENT_METHOD FROM RESERVATION JOIN CUSTOMER C on C.CUSTOMER_ID = RESERVATION.CUSTOMER_ID JOIN VEHICLE V on RESERVATION.VEHICLE_ID = V.VEHICLE_ID;")
    reservations = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Reservation Id', 'Customer First Name','Customer Last Name', 'Make', 'Model', 'Reservation Date', 'Pickup Date', 'Drop Date', 'Price', 'Payment Method'])
    writer.writerows(reservations)
    
    # Return CSV file as response
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=reservations.csv"}
    )

@app.route('/realtime_dashboard')
def realtime_dashboard():
    cursor = mydb.cursor()

    # Query to get total reservations
    cursor.execute("SELECT COUNT(*) FROM RESERVATION")
    total_reservations = cursor.fetchone()[0]

    # Query to get total vehicles
    cursor.execute("SELECT COUNT(*) FROM VEHICLE")
    total_vehicles = cursor.fetchone()[0]

    # Query to get total locations available
    cursor.execute("SELECT COUNT(*) FROM RENTAL_LOCATION")
    total_locations = cursor.fetchone()[0]

    # Query to get total customers available
    cursor.execute("SELECT COUNT(*) FROM CUSTOMER")
    total_customers = cursor.fetchone()[0]

    return render_template('realtime_dashboard.html', total_reservations=total_reservations,
                           total_vehicles=total_vehicles, total_locations=total_locations,
                           total_customers=total_customers)


if __name__ == '__main__':
    app.run(debug=True)
