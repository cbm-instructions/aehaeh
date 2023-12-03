import os
# from RPi import GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO
# from mfrc522 import SimpleMFRC522
import sqlite3
import time

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

#os.system('clear')  # clear screen, this is just for the OCD purposes
os.system('cls')
step = 5  # linear steps for increasing/decreasing volume

# tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
# GPIO.setmode(GPIO.BCM)
# set up the pins we have been using
clk = 17
dt = 18
back = 27
ok = 22

# set up the GPIO events on those pins
# GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(back, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(ok, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# get the initial states
counter = 0
# clkLastState = GPIO.input(clk)
# dtLastState = GPIO.input(dt)
# backLastState = GPIO.input(back)
# okLastState = GPIO.input(back)

# database list

id_counter = 0
current_user_values = {
    "ID": id_counter,
    "Tisch Nr.": "",
    "Datum": "",
    "Stunde": "",
    "Minute": "",
    "Dauer": "",
}

def reset_current_user_values():
    current_user_values["ID"] = str(id_counter+1)
    current_user_values["Tisch Nr."] = ""
    current_user_values["Datum"] = ""
    current_user_values["Stunde"] = ""
    current_user_values["Minute"] = ""
    current_user_values["Dauer"] = ""

# def read_from_rfid():
#    reader = SimpleMFRC522()
#    text = ""
#    try:
#        while True:
#            text = reader.read()
#            time.sleep(0.5)
#            if text != "":
#                break;
#    return text


def create_table_reservations():
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Reservations(
                           ID TEXT,
                           Tischnummer TEXT,
                           Datum TEXT,
                           Stunde TEXT,
                           Minute TEXT,
                           Dauer TEXT,
                           PRIMARY KEY (ID, Tischnummer, Datum)
                       )''')
    finally:
        cursor.close()
        connection.close()


def read_all_reservations_for_user(user_id):
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    entryFound = False

    try:
        while not entryFound:
            # text = read_from_rfid()
            user_id = user_id
            cursor.execute(
                "SELECT Tischnummer, Datum, Stunde, Minute, Dauer FROM Reservations WHERE ID=?",
                (user_id,)
            )
            rows = cursor.fetchall()

            if not rows:
                print("No reservations found")
            else:
                print("---------------")
                for row in rows:
                    print("Tischnummer: ", row[0])
                    print("Datum: ", row[1])
                    print("Stunde: ", row[2])
                    print("Minute: ", row[3])
                    print("Dauer: ", row[4])
                    print("---------------")
                entryFound = True
    finally:
        cursor.close()
        connection.close()
def write_reservation_to_database():
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    try:
        query = "INSERT INTO Reservations(ID, Tischnummer, Datum, Stunde, Minute, Dauer) VALUES (?,?,?,?,?,?)"
        values = (current_user_values["ID"], current_user_values["Tisch Nr."], current_user_values["Datum"],
                  current_user_values["Stunde"], current_user_values["Minute"],
                  current_user_values["Dauer"])

        cursor.execute(query, values)
        connection.commit()
        print("Record inserted successfully!")
    except Exception as e:
        print("Error inserting record:", e)
    finally:
        cursor.close()
        connection.close()


def remove_reservation_from_database(user_id, tischnummer, datum, stunde, minute, dauer):
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    try:
        cursor.execute(
            "DELETE FROM Reservations WHERE ID=? AND Tischnummer=? AND Datum=? AND Stunde=? AND 'Minute'=? AND Dauer=?",
            (user_id, tischnummer, datum, stunde, minute, dauer))
    finally:
        cursor.close()
        connection.close()


# define functions which will be triggered on pin state changes
@socketio.on('update_value')
def update_value():
    print("Auto update!")
    socketio.emit('new_value', {'value': 'false'})

@socketio.on('update_current_user_values')
def update_current_user_values(data):
    key = data['key']
    value = data['value']
    current_user_values[key] = value
    print(f"Updated current_user_values[{key}] to {value}")

    if key == 'Dauer':
        create_table_reservations()
        write_reservation_to_database()
        read_all_reservations_for_user(id_counter)
        reset_current_user_values()

# def clkClicked(channel):
#        global counter
#        global step
#
#        clkState = GPIO.input(clk)
#        dtState = GPIO.input(dt)
#
#        if clkState == 0 and dtState == 1:
#                counter = counter + step
#                socketio.emit('new_value', {'left': 'true'})
#                print ("Counter ", counter)
# def dtClicked(channel):
#        global counter
#        global step
#
#        clkState = GPIO.input(clk)
#        dtState = GPIO.input(dt)
#
#        if clkState == 1 and dtState == 0:
#                counter = counter - step
#                socketio.emit('new_value', {'right': 'true'})
#                print ("Counter ", counter)
#
# def backClicked(channel):
#        socketio.emit('new_value', {'back': 'true'})
#        print ("Back clicked")
#
# def okClicked(channel):
#        socketio.emit('new_value', {'ok': 'true'})
#        print ("Ok clicked")
#
# GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=300)
# GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=300)
# GPIO.add_event_detect(back, GPIO.FALLING, callback=backClicked, bouncetime=300)
# GPIO.add_event_detect(ok, GPIO.FALLING, callback=okClicked, bouncetime=300)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    #create_table_reservations()
    #current_user_values["ID"] = "2120548"
    #current_user_values["Tischnummer"] = "4"
    #current_user_values["Datum"] = "15.12.2022"
    #current_user_values["Stunde"] = "14"
    #current_user_values["Minute"] = "30"
    #current_user_values["Dauer"] = "240"
    #write_reservation_to_database()
    #read_all_reservations_for_user("2120548")

# GPIO.cleanup()
