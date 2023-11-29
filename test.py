import os
from RPi import GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO
from mfrc522 import SimpleMFRC522
import sqlite3
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

os.system('clear') #clear screen, this is just for the OCD purposes
 
step = 5 #linear steps for increasing/decreasing volume
 
#tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
GPIO.setmode(GPIO.BCM) 
#set up the pins we have been using
clk = 17
dt = 18
back = 27
ok = 22
 
#set up the GPIO events on those pins
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(back, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ok, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
#get the initial states
counter = 0
clkLastState = GPIO.input(clk)
dtLastState = GPIO.input(dt)
backLastState = GPIO.input(back)
okLastState = GPIO.input(back)

# database list
current_user_values = {
    "ID" : "",
    "Datum" : "",
    "Uhrzeit" : "",
    "Dauer" : "",
}

def read_from_rfid():
    reader = SimpleMFRC522()
    text = ""
    try:
        while True:
            text = reader.read()
            time.sleep(0.5)
            if text != "":
                break
    return text



def create_table_reservations_for_database():
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Reservations(
                   ID TEXT PRIMARY KEY,
                   Datum TEXT,
                   Uhrzeit TEXT,
                   Dauer TEXT)
                   ''')

    cursor.close()
    connection.close()

def read_from_database():
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    entryFound = False

    try:
        while entryFound == False:
            text = read_from_rfid()
            cursor.execute("SELECT ID, Datum, Uhrzeit, Dauer FROM Reservations WHERE ID=?", str(text))
            rows = cursor.fetchall()

            if not rows:
                print("No reservations found")
            else:
                print("---------------")
                for row in rows:
                    print("ID: ", row[0])
                    print("Datum: ", row[1])
                    print("Uhrzeit: ", row[2])
                    print("Dauer: ", row[3])
                entryFound = True
    finally:
        cursor.close()
        connection.close()

def write_reservation_to_database():
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO Reservations(ID, Datum, Uhrzeit, Dauer) VALUES (?,?,?,?)",
            (current_user_values["ID"],current_user_values["Datum"],current_user_values["Uhrzeit"],current_user_values["Dauer"],))
    finally:
        cursor.close()
        connection.close()

def remove_reservation_from_database(id,datum,zeit,dauer):
     connection = sqlite3.connect("reservations.db")
     cursor = connection.cursor()
     try:
        cursor.execute("DELETE FROM Reservations WHERE ID=? AND Datum=? AND Uhrzeit=? AND Dauer=?", (id,datum,zeit,dauer))
     finally:
        cursor.close()
        connection.close()

#define functions which will be triggered on pin state changes
@socketio.on('update_value')
def update_value():
        print("Auto update!")
        socketio.emit('new_value', {'value': 'false'})

def clkClicked(channel):
        global counter
        global step
 
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
 
        if clkState == 0 and dtState == 1:
                counter = counter + step
                socketio.emit('new_value', {'left': 'true'})
                print ("Counter ", counter)
 ß
def dtClicked(channel):
        global counter
        global step
 
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
         
        if clkState == 1 and dtState == 0:
                counter = counter - step
                socketio.emit('new_value', {'right': 'true'})
                print ("Counter ", counter)
 
def backClicked(channel):
        socketio.emit('new_value', {'back': 'true'})
        print ("Back clicked")

def okClicked(channel):
        socketio.emit('new_value', {'ok': 'true'})
        print ("Ok clicked")
 
GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=300)
GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=300)
GPIO.add_event_detect(back, GPIO.FALLING, callback=backClicked, bouncetime=300)
GPIO.add_event_detect(ok, GPIO.FALLING, callback=okClicked, bouncetime=300)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

 
GPIO.cleanup()