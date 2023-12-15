#from RPi import GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO
# from mfrc522 import SimpleMFRC522
import sqlite3
import paho.mqtt.client as mqtt
import threading
import json
from datetime import datetime, timedelta
import time
import os


class MQTTThread(threading.Thread):
    def __init__(self, broker_address, port, username, password):
        super(MQTTThread, self).__init__()
        self.broker_address = broker_address
        self.port = port
        self.username = username
        self.password = password
        self.interval = 60

    def find_next_reservation_if_exists(self, table_number, check_in_date, check_in_time):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        try:
            # Uhrzeit aller Reservierungen an der übergebenen Tischnummer und an dem übergebenen Datum
            cursor.execute(
                "SELECT Uhrzeit FROM Reservations WHERE Tischnummer=? AND Datum=? ORDER BY Uhrzeit",
                (table_number, str(check_in_date)))
            rows = cursor.fetchall()

            # An diesem Tag ist keine Reservierung mehr für diesen Tisch geplant worden.
            if not rows:
                return None
            current_time_rounded = check_in_time
            times_with_reservations = [datetime.strptime(row[0], "%H:%M") for row in rows]

            # Runde die aktuelle Uhrzeit auf das nächste 5-Minuten-Intervall auf
            minutes_remainder = check_in_time.minute % 5
            if minutes_remainder != 0:
                current_time_rounded += timedelta(minutes=5 - minutes_remainder)

            # Durchsuche die Reservierungen und finde die nächste freie Uhrzeit im 5-Minuten-Intervall.
            next_reservation_time = current_time_rounded
            while next_reservation_time not in times_with_reservations:
                next_reservation_time += timedelta(minutes=5)
                print(next_reservation_time)
                if next_reservation_time.strftime("%H:%M") == "00:00":
                    break

            return "None" if next_reservation_time.strftime("%H:%M") == "00:00" else next_reservation_time.strftime(
                "%H:%M")
        finally:
            cursor.close()
            connection.close()

    def get_reservation_from_reservations(self, user_id, table_number, check_in_date, check_in_time):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        try:
            ## Rundet die aktuelle Uhrzeit im 5 Minuten Takt auf
            check_in_time_dt = datetime.strptime(check_in_time, "%H:%M")
            check_in_time_rounded = check_in_time_dt

            minutes_remainder = check_in_time_rounded.minute % 5
            if minutes_remainder != 0:
                check_in_time_rounded += timedelta(minutes=(5 - minutes_remainder))
            print("Aktuelle Uhrzeit:", check_in_time_dt.strftime("%H:%M"))

            cursor.execute(
                "SELECT ID, Tischnummer, Datum, Uhrzeit, Dauer, Statuscode FROM Reservations WHERE ID=? AND Tischnummer=? AND Datum=?",
                (user_id, table_number, check_in_date))
            rows = cursor.fetchall()

            # Es existiert keine Reservierung. Der Tisch kann verwendet werden bis eine neue Reservierung ansteht.
            # WICHTIG: next_reservation_time kann auch den Typen None haben
            if not rows:
                next_reservation_time = self.find_next_reservation_if_exists(table_number, check_in_date,
                                                                             check_in_time_rounded)
                return {"reserviert": False, "Nächste Reservierung": next_reservation_time}

            # Es wurden Reservierungen zu dem Nutzer für diesen Tag gefunden. Es wird geprüft, ob
            # es sich um die Reservierung des Nutzers handelt. Dieser darf maximal 20 Minüten zu spät auftauchen.
            for row in rows:
                reservation_time = datetime.strptime(row[3], "%H:%M")  # Move this line here
                max_time = reservation_time + timedelta(minutes=20)
                reservation_date = datetime.strptime(row[2], "%d.%m.%Y")
                reservation_duration = row[4]
                print("Reservierung gefunden.")
                # Eine Reservierung ist dann gültig, wenn
                # - Die Reservierung vor oder zur selben Zeit des check-ins stattfindet
                # - Der Check-in nicht die max_time überschreitet
                print("Reservierungs-Uhrzeit:", reservation_time.strftime("%H:%M"), "Aktuelle-Uhrzeit:",
                      check_in_time,
                      "Maximale-Uhrzeit", max_time.strftime("%H:%M"))

                if reservation_time <= check_in_time_dt <= max_time:
                    print("Reservierungs-Uhrzeit:", reservation_time.strftime("%H:%M"), "Aktuelle-Uhrzeit:",
                          check_in_time,
                          "Maximale-Uhrzeit", max_time.strftime("%H:%M"))
                    return {"reserviert": True, "Datum": str(reservation_date.strftime("%d.%m.%Y")),
                            "Uhrzeit": reservation_time.strftime("%H:%M"), "Dauer": str(reservation_duration)}

            print("No criteria found")
            next_reservation_time = self.find_next_reservation_if_exists(table_number, check_in_date,
                                                                         check_in_time_rounded)
            return {"reserviert": False, "Nächste Reservierung": next_reservation_time}

        finally:
            cursor.close()
            connection.close()

    def send_time_message(self, client):
        while True:
            current_time = datetime.now()
            date = current_time.strftime("%d.%m.%Y")
            clock_time = current_time.strftime("%H:%M")
            weekday = weekday_translations(current_time.strftime("%A"))
            message = {"Uhrzeit": clock_time, "Datum": date, "Wochentag": weekday}
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
                time.sleep(5)
            finally:
                cursor.close()
                connection.close()

    def check_out_from_reservation(self, user_id, table_number, reservation_date, reservation_clock_time):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        try:
            cursor.execute(
                "UPDATE Reservations SET Statuscode = '1' WHERE ID=? AND Tischnummer=? AND Datum=? AND Uhrzeit=?",
                (user_id, table_number, reservation_date, reservation_clock_time)
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def on_connect(self, client, userdata, flags, rc):
        create_table_reservations()
        print("Verbunden mit dem MQTT Broker mit dem Result Code: " + str(rc))
        threading.Thread(target=self.send_time_message, args=(client,), daemon=True).start()
        threading.Thread(target=self.send_all_reservations, args=(client,), daemon=True).start()

    def on_message(self, client, userdata, msg):
        if isinstance(msg, str):
            print("Received plain text message:", msg)
        else:
            try:
                decoded_payload = msg.payload.decode()
                message = json.loads(decoded_payload)
                print("Received JSON message:", message)

                if msg.topic == "Denkraum/checkout":
                    user_id = message["ID"]
                    table_number = message["Tischnummer"]
                    reservation_date = message["Reservierungsdatum"]
                    reservation_clock_time = message["Reservierungsuhrzeit"]

                    self.check_out_from_reservation(user_id, table_number, reservation_date, reservation_clock_time)

                    print("Reservation was marked as completed!")

                elif msg.topic == "denkraum/checkin":
                    user_id = message["ID"]
                    version_number = message["Versionsnummer"]
                    table_number = message["Tischnummer"]
                    current_datetime = datetime.now()
                    check_in_date = current_datetime.strftime("%d.%m.%Y")
                    check_in_time = current_datetime.strftime("%H:%M")

                    reservation = self.get_reservation_from_reservations(user_id, table_number, check_in_date,
                                                                         check_in_time)

                    is_reserved = reservation["reserviert"]

                    if is_reserved:
                        reservation_date = reservation["Datum"]
                        reservation_time = reservation["Uhrzeit"]
                        reservation_duration = reservation["Dauer"]

                        response = {"ID": user_id, "Tischnummer": table_number, "Versionsnummer": version_number,
                                    "Reservierungsdatum": reservation_date, "Reservierungsuhrzeit": reservation_time,
                                    "Reservierungsdauer": reservation_duration, "reserviert": is_reserved}

                    else:
                        next_reservation_time = reservation["Nächste Reservierung"]
                        if next_reservation_time is None:
                            next_reservation_time = "None"

                        response = {"ID": user_id, "Tischnummer": table_number, "Versionsnummer": version_number,
                                    "Nächste Reservierung": next_reservation_time, "reserviert": is_reserved}

                    client.publish("denkraum/response", json.dumps(response))
                    print("Response sent. Result of Reservation", response)

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
        client.subscribe("denkraum/checkin")
        client.subscribe("Denkraum/checkout")
        client.loop_forever()


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

os.system('clear')  # clear screen, this is just for the OCD purposes
#  os.system('cls')
step = 5  # linear steps for increasing/decreasing volume

# tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
#GPIO.setmode(GPIO.BCM)
# set up the pins we have been using
clk = 17
dt = 18
back = 27
ok = 22

# set up the GPIO events on those pins
#GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(back, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(ok, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# get the initial states
counter = 0
#clkLastState = GPIO.input(clk)
#dtLastState = GPIO.input(dt)
#backLastState = GPIO.input(back)
#okLastState = GPIO.input(back)

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
#   reader = SimpleMFRC522()
#   text = ""
#   try:
#       while True:
#           text = reader.read()
#           time.sleep(0.5)
#           if text != "":
#               break;
#   return text


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
                           Statuscode TEXT DEFAULT "0",
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


reservation_time = ""


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


@socketio.on('button')
def update_current_user_values(data):
    print("update button")
    if data == "back":
        socketio.emit('new_value', {'right': 'true'})
    else:
        socketio.emit('new_value', {'left': 'true'})

def clkClicked(channel):
    global counter
    global step

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState == 0 and dtState == 1:
        counter = counter + step
        socketio.emit('new_value', {'left': 'true'})
        print("Counter ", counter)


def dtClicked(channel):
    global counter
    global step

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)

    if clkState == 1 and dtState == 0:
        counter = counter - step
        socketio.emit('new_value', {'right': 'true'})
        print("Counter ", counter)


def backClicked(channel):
    socketio.emit('new_value', {'back': 'true'})
    print("Back clicked")


def okClicked(channel):
    socketio.emit('new_value', {'ok': 'true'})
    print("Ok clicked")


#GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=300)
#GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=300)
#GPIO.add_event_detect(back, GPIO.FALLING, callback=backClicked, bouncetime=300)
#GPIO.add_event_detect(ok, GPIO.FALLING, callback=okClicked, bouncetime=300)


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

GPIO.cleanup()

weekday_translations = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag"
}
