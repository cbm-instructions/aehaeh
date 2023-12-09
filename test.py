# from RPi import GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO
# from mfrc522 import SimpleMFRC522
import sqlite3
import paho.mqtt.client as mqtt
import threading
import json
from datetime import datetime
import time


class MQTTThread(threading.Thread):
    def __init__(self, broker_address, port, username, password):
        super(MQTTThread, self).__init__()
        self.broker_address = broker_address
        self.port = port
        self.username = username
        self.password = password
        self.interval = 60

    def does_a_reservation_exist(self, tischnummer):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT Tischnummer, Datum, Uhrzeit, Dauer, S FROM Reservations WHERE Tischnummer=?",
                           tischnummer)
            rows = cursor.fetchall()
            if not rows:
                return False
            else:
                return True
        finally:
            cursor.close()
            connection.close()

    def send_time_message(self, client):
        while True:
            aktuelle_zeit = datetime.now()
            datum = aktuelle_zeit.strftime("%d.%m.%Y")
            uhrzeit = aktuelle_zeit.strftime("%H:%M")
            wochentag = aktuelle_zeit.strftime("%A")

            match wochentag:
                case "Monday":
                    wochentag = "Montag"
                case "Tuesday":
                    wochentag = "Dienstag"
                case "Wednesday":
                    wochentag = "Mittwoch"
                case "Thursday":
                    wochentag = "Donnerstag"
                case "Friday":
                    wochentag = "Freitag"
                case "Saturday":
                    wochentag = "Samstag"
                case "Sunday":
                    wochentag = "Sonntag"

            message = {"Uhrzeit": uhrzeit, "Datum": datum, "Wochentag": wochentag}
            client.publish("time", json.dumps(message))
            print("Time sent")
            time.sleep(self.interval)

    def send_all_reservations(self, client):
        while True:
            print("Reservations sent")
            connection = sqlite3.connect("reservations.db")
            cursor = connection.cursor()

            topics = ["denkraum/tisch1/reservierung",
                      "denkraum/tisch2/reservierung",
                      "denkraum/tisch3/reservierung",
                      "denkraum/tisch4/reservierung",
                      "denkraum/tisch5/reservierung",
                      "denkraum/tisch6/reservierung",
                      "denkraum/tisch7/reservierung",
                      "denkraum/tisch8/reservierung",
                      ]

            try:
                for i in range(0, len(topics)):
                    reservations = []
                    cursor.execute(
                        "SELECT ID, Tischnummer, Datum, Uhrzeit, Dauer, Statuscode FROM Reservations WHERE Tischnummer=?",
                        str(i + 1))
                    rows = cursor.fetchall()
                    for row in rows:
                        reservation = {"Matrikelnummer": row[0], "Tischnummer": row[1], "Datum": row[2],
                                       "Uhrzeit": row[3], "Dauer": row[4], "Statuscode": row[5]}
                        reservations.append(reservation)
                    json_reservations = json.dumps(reservations)
                    client.publish(topics[i], json_reservations)
                time.sleep(60)
            finally:
                cursor.close()
                connection.close()

    def on_connect(self, client, userdata, flags, rc):
        create_table_reservations()
        print("Verbunden mit dem MQTT Broker mit dem Result Code: " + str(rc))
        threading.Thread(target=self.send_time_message, args=(client,), daemon=True).start()
        threading.Thread(target=self.send_all_reservations, args=(client,), daemon=True).start()

    def on_message(self, client, userdata, msg):
        decoded_payload = msg.payload.decode()
        if isinstance(decoded_payload, str):
            print("Received plain text message:", decoded_payload)
        else:
            try:
                message = json.loads(decoded_payload)
                # versions_nummer = message["Versionsnummer"]
                # tisch_nummer = message["Tischnummer"]
                print("Received JSON message:", message)

                # TODO: Prüfe erhaltene Anfrage nach dem erhaltenen Statuscode und
                #       sende eine entsprechende Response mit Versionsnummer, Tischnummer,
                #       Dauer der Reservierung und Uhrzeit der Reservierung zurück

            except json.decoder.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print("Invalid JSON format.")

    def run(self):

        # Verbindung zum MQTT-Broker herstellen und Benutzername/Passwort übergeben
        client = mqtt.Client()
        client.username_pw_set(self.username, self.password)
        client.connect(self.broker_address, self.port)

        client.on_message = self.on_message
        client.on_connect = self.on_connect
        client.loop_forever()


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# os.system('clear')  # clear screen, this is just for the OCD purposes
#  os.system('cls')
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

id_counter = 0
current_user_values = {
    "ID": id_counter,
    "Tisch Nr.": "",
    "Datum": "",
    "Uhrzeit": "",
    "Dauer": "",
}


def reset_current_user_values():
    current_user_values["ID"] = id_counter
    current_user_values["Tisch Nr."] = ""
    current_user_values["Datum"] = ""
    current_user_values["Uhrzeit"] = ""
    current_user_values["Dauer"] = ""
    current_user_values["Statuscode"] = "0"

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
                           ID INTEGER AUTO_INCREMENT,
                           Tischnummer TEXT,
                           Datum TEXT,
                           Uhrzeit TEXT,
                           Dauer TEXT,
                           Statuscode TEXT DEFAULT 0,
                           UNIQUE(ID, Tischnummer, Datum, Uhrzeit)
                       )''')
    finally:
        cursor.close()
        connection.close()


def read_all_reservations_for_user(user_id):
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    entry_found = False

    try:
        while not entry_found:
            # text = read_from_rfid()
            user_id = user_id
            cursor.execute(
                "SELECT ID,Tischnummer, Datum, Uhrzeit, Dauer, Statuscode FROM Reservations WHERE ID=?",
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
                    print("Uhrzeit: ", row[2])
                    print("Dauer: ", row[3])
                    print("Statuscode: ", row[4])
                    print("---------------")
                entry_found = True
    finally:
        cursor.close()
        connection.close()


def write_reservation_to_database():
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    try:
        query = "INSERT INTO Reservations(ID,Tischnummer, Datum, Uhrzeit, Dauer) VALUES (?,?,?,?,?)"
        values = (
            current_user_values["ID"],
            current_user_values["Tisch Nr."],
            current_user_values["Datum"],
            current_user_values["Uhrzeit"],
            current_user_values["Dauer"],
        )
        cursor.execute(query, values)
        connection.commit()
        print("Record inserted successfully!")
    except Exception as e:
        print("Error inserting record:", e)
    finally:
        cursor.close()
        connection.close()


def remove_reservation_from_database(user_id, tischnummer, datum, uhrzeit, dauer, statuscode):
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    try:
        cursor.execute(
            "DELETE FROM Reservations WHERE ID=? AND Tischnummer=? AND Datum=? AND Uhrzeit=? AND Dauer=? AND  Statuscode=?",
            (user_id, tischnummer, datum, uhrzeit, dauer, statuscode))
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
        global id_counter
        read_all_reservations_for_user(id_counter)
        id_counter += 1
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
    broker_address = "localhost"
    port = 1883
    username = "user"
    password = "Test123"

    mqtt_thread = MQTTThread(broker_address, port, username, password)
    mqtt_thread.start()
    app.run(debug=False, host='0.0.0.0')
    mqtt_thread.join()

# GPIO.cleanup()
