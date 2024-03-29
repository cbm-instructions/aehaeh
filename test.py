#from RPi import GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO
#from mfrc522 import SimpleMFRC522
import sqlite3
import paho.mqtt.client as mqtt
import threading
import json
from datetime import datetime, timedelta
import time
import os

weekday_translations = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag"
}


class MQTTThread(threading.Thread):
    def __init__(self, broker_address, port, username, password):
        super(MQTTThread, self).__init__()
        self.broker_address = broker_address
        self.port = port
        self.username = username
        self.password = password
        self.interval = 15

    @staticmethod
    def find_next_reservation_if_exists(table_number, check_in_date, check_in_time):
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

            # Runde die aktuelle Uhrzeit auf das nächste 15-Minuten-Intervall auf
            minutes_remainder = check_in_time.minute % 15
            if minutes_remainder != 0:
                current_time_rounded += timedelta(minutes=15 - minutes_remainder)

            # Durchsuche die Reservierungen und finde die nächste freie Uhrzeit im 15-Minuten-Intervall.
            next_reservation_time = current_time_rounded
            while next_reservation_time not in times_with_reservations:
                next_reservation_time += timedelta(minutes=15)
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
            # Rundet die aktuelle Uhrzeit im 15-Minuten-Takt auf
            check_in_time_dt = datetime.strptime(check_in_time, "%H:%M")
            check_in_time_rounded = check_in_time_dt

            minutes_remainder = check_in_time_rounded.minute % 15
            if minutes_remainder != 0:
                check_in_time_rounded += timedelta(minutes=(15 - minutes_remainder))
            print("Aktuelle Uhrzeit:", check_in_time_dt.strftime("%H:%M"))

            cursor.execute(
                "SELECT ID, Tischnummer, Datum, Uhrzeit, Dauer, Statuscode "
                "FROM Reservations "
                "WHERE ID=? AND Tischnummer=? AND Datum=?",
                (user_id, table_number, check_in_date))
            rows = cursor.fetchall()

            # Es existiert keine Reservierung. Der Tisch kann verwendet werden bis eine neue Reservierung ansteht.
            # WICHTIG: next_reservation_time kann auch den Typen None haben
            if not rows:
                print("Reservierung existiert nicht")
                next_reservation_time = self.find_next_reservation_if_exists(table_number, check_in_date,
                                                                             check_in_time_rounded)
                return {"Statuscode": "0","reserviert": False, "Nächste Reservierung": next_reservation_time}

            # Es wurden Reservierungen zu dem Nutzer für diesen Tag gefunden. Es wird geprüft, ob
            # es sich um die Reservierung des Nutzers handelt. Dieser darf maximal 20 Minüten zu spät auftauchen.
            for row in rows:
                reservation_time = datetime.strptime(row[3], "%H:%M")  # Move this line here
                max_time = reservation_time + timedelta(minutes=20)
                reservation_date = datetime.strptime(row[2], "%d.%m.%Y")
                reservation_duration = row[4]
                reservation_statuscode = row[5]
                print(reservation_statuscode)
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

                    return {"Statuscode": reservation_statuscode, "reserviert": True, "Datum": str(reservation_date.strftime("%d.%m.%Y")),
                            "Uhrzeit": reservation_time.strftime("%H:%M"), "Dauer": str(reservation_duration)}

            print("No criteria found")
            next_reservation_time = self.find_next_reservation_if_exists(table_number, check_in_date,
                                                                         check_in_time_rounded)
            return {"Statuscode": reservation_statuscode, "reserviert": False, "Nächste Reservierung": next_reservation_time,
            "Datum": str(reservation_date.strftime("%d.%m.%Y")),
                            "Uhrzeit": reservation_time.strftime("%H:%M"), "Dauer": str(reservation_duration)
            }

        finally:
            cursor.close()
            connection.close()

    def send_time_message(self, client):
        while True:
            current_time = datetime.now()
            date = current_time.strftime("%d.%m.%Y")
            clock_time = current_time.strftime("%H:%M")
            weekday = weekday_translations[current_time.strftime("%A")]
            message = {"Uhrzeit": clock_time, "Datum": date, "Wochentag": weekday}
            client.publish("time", json.dumps(message))
            print("Time sent")
            time.sleep(self.interval)

    @staticmethod
    def send_all_reservations(client):
        while True:
            # print("Reservations sent")
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
                        "SELECT ID, Tischnummer, Datum, Uhrzeit, Dauer, Statuscode "
                        "FROM Reservations "
                        "WHERE Tischnummer=?",
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


    def check_out_from_reservation(self, user_id, table_number, reservation_date, reservation_time):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        try:
            cursor.execute(
                "UPDATE Reservations SET Statuscode = '1' WHERE ID=? AND Tischnummer=? AND Datum=? AND Uhrzeit=?",
                (user_id, str(table_number), str(reservation_date), str(reservation_time))
            )

            connection.commit()
            print("Statuscode was set to value 1")
        finally:
            cursor.close()
            connection.close()
            
    def check_in_to_reservation(self, user_id, table_number, reservation_date, reservation_time):
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()

        try:
            cursor.execute(
                "UPDATE Reservations SET Statuscode = '2' WHERE ID=? AND Tischnummer=? AND Datum=? AND Uhrzeit=?",
                (user_id, str(table_number), str(reservation_date), str(reservation_time))
            )

            connection.commit()
            print("Statuscode was set to value 2")
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

                    reservation_time = message["Reservierungsuhrzeit"]

                    self.check_out_from_reservation(user_id, table_number, reservation_date, reservation_time)

                elif msg.topic == "denkraum/checkin":
                    user_id = message["ID"]
                    version_number = message["Versionsnummer"]
                    table_number = message["Tischnummer"]
                    current_datetime = datetime.now()

                    check_in_date = current_datetime.strftime("%d.%m.%Y")
                    check_in_time = current_datetime.strftime("%H:%M")

                    reservation = self.get_reservation_from_reservations(user_id, table_number, check_in_date,
                                                                         check_in_time)

                    statuscode = reservation["Statuscode"]

                    if statuscode == "-1":
                        reservation_date = reservation["Datum"]
                        reservation_time = reservation["Uhrzeit"]
                        reservation_duration = reservation["Dauer"]
                        statuscode = reservation["Statuscode"]

                        reservierungs_dateobject = datetime.strptime(reservation_time, "%H:%M")
                        checkin_dateobject = datetime.strptime(check_in_time, "%H:%M")

                        difference_in_minutes = int(
                            (checkin_dateobject - reservierungs_dateobject).total_seconds() / 60)
                        print(str(difference_in_minutes) + " Minuten später da als reserviert wurde.")

                        if difference_in_minutes <= 15 and difference_in_minutes >= 0:
                            self.check_in_to_reservation(user_id, table_number, reservation_date, reservation_time)
                            statuscode = "2"

                        response = {"ID": user_id, "Tischnummer": table_number, "Versionsnummer": version_number,
                                    "Reservierungsdatum": reservation_date, "Reservierungsuhrzeit": reservation_time,
                                    "Reservierungsdauer": reservation_duration, "Statuscode": statuscode}

                    else:
                        statuscode = reservation["Statuscode"]

                        # Rundet die aktuelle Uhrzeit im 15-Minuten-Takt auf
                        check_in_time_dt = datetime.strptime(check_in_time, "%H:%M")
                        check_in_time_rounded = check_in_time_dt

                        minutes_remainder = check_in_time_rounded.minute % 15
                        if minutes_remainder != 0:
                            check_in_time_rounded += timedelta(minutes=(15 - minutes_remainder))
                        next_reservation_time = self.find_next_reservation_if_exists(table_number, check_in_date,
                                                                                     check_in_time_rounded)
                        if next_reservation_time is None:
                            next_reservation_time = "None"

                        response = {"ID": user_id, "Tischnummer": table_number, "Versionsnummer": version_number,
                                    "Nächste Reservierung": next_reservation_time, "Statuscode": statuscode}

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


app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

os.system('clear')  # clear screen, this is just for the OCD purposes
# os.system('cls')
step = 5  # linear steps for increasing/decreasing volume

# tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
#GPIO.setmode(GPIO.BCM)
# set up the pins we have been using
#clk = 17
#dt = 18
#back = 27
#ok = 22

# set up the GPIO events on those pins
#GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(back, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(ok, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# get the initial states
#counter = 0
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
    "Statuscode": "-1",
}


def reset_current_user_values():
    current_user_values["ID"] = id_counter
    current_user_values["Tisch Nr."] = ""
    current_user_values["Datum"] = ""
    current_user_values["Uhrzeit"] = ""
    current_user_values["Dauer"] = ""
    current_user_values["Statuscode"] = "-1"


def create_table_reservations():
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Reservations(
                           ID INTEGER AUTO_INCREMENT,
                           Tischnummer TEXT NOT NULL,
                           Datum TEXT NOT NULL,
                           Uhrzeit TEXT NOT NULL,
                           Dauer TEXT NOT NULL,
                           Statuscode TEXT DEFAULT "-1",
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
                    print("ID: ", row[0])
                    print("Tischnummer: ", row[1])
                    print("Datum: ", row[2])
                    print("Uhrzeit: ", row[3])
                    print("Dauer: ", row[4])
                    print("Statuscode: ", row[5])
                    print("---------------")
                entry_found = True
    finally:
        cursor.close()
        connection.close()


def write_reservation_to_database():
    connection = sqlite3.connect("reservations.db")
    cursor = connection.cursor()
    current_user_values["Datum"] = current_user_values["Datum"] + "2024"
    try:
        query = "INSERT INTO Reservations(ID,Tischnummer, Datum, Uhrzeit, Dauer,Statuscode) VALUES (?,?,?,?,?,?)"
        values = (
            current_user_values["ID"],
            current_user_values["Tisch Nr."],
            current_user_values["Datum"],
            current_user_values["Uhrzeit"],
            current_user_values["Dauer"],
            current_user_values["Statuscode"],
        )
        if (current_user_values["ID"] != "" and current_user_values["Tisch Nr."] != "" and
                current_user_values["Datum"] != "" and current_user_values["Uhrzeit"] != ""
                and current_user_values["Dauer"] != ""):
            cursor.execute(query, values)
            connection.commit()
            print("Record inserted successfully!")
            return True
        else:
            print("Inserting Record failed!")
            return False
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
            "DELETE FROM Reservations "
            "WHERE ID=? AND Tischnummer=? AND Datum=? AND Uhrzeit=? AND Dauer=? AND  Statuscode=?",
            (user_id, tischnummer, datum, uhrzeit, dauer, statuscode))
    finally:
        cursor.close()
        connection.close()


def get_all_reservations():
    while True:
        # print("Reservations sent")
        connection = sqlite3.connect("reservations.db")
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT ID, Tischnummer, Datum, Uhrzeit, Dauer, Statuscode FROM Reservations")
            rows = cursor.fetchall()
            # print(rows)
            return rows
        finally:
            cursor.close()
            connection.close()


# define functions which will be triggered on pin state changes
@socketio.on('update_value')
def update_value():
    print("Auto update!")
    socketio.emit('new_value', {'value': 'false'})


@socketio.on('request_database_values')
def request_database_values(value):
    if value == "receive":
        data_base_entries = get_all_reservations()
        socketio.emit("data_base_entries", {"value": data_base_entries})


@socketio.on('update_current_user_values')
def update_current_user_values(data):
    key = data['key']
    value = data['value']
    current_user_values[key] = value
    print(f"Updated current_user_values[{key}] to {value}")


@socketio.on('request_current_user_values')
def request_current_user_values(data):
    socketio.emit('display_current_user_values', current_user_values)


@socketio.on('finish_reservation')
def finish_reservation(value):
    if value == "finish":
        create_table_reservations()
        if write_reservation_to_database():
            global id_counter
            read_all_reservations_for_user(current_user_values["ID"])
            id_counter += 1
        reset_current_user_values()


#def read_rfid_thread():
#   reader = SimpleMFRC522()
#   try:
#       while True:
#           id = reader.read_id()
#           print("I am reading")
#           current_user_values["ID"] = str((hex(id)))[4:10]
#           # current_user_values["ID"] = hex(id)
#           # print(current_user_values["ID"])
#           if current_user_values["ID"] != "":
#               break
#   finally:
#       socketio.emit("rfid_id", {"id": current_user_values["ID"]})

#@socketio.on('read_rfid')
#def read_rfid(data):
#   if data == "read":
#       print("Read from RFID")
#       threading.Thread(target=read_rfid_thread).start()


@socketio.on('button')
def update_current_user_values(data):
    # print("update button")
    if data == "left":
        socketio.emit('new_value', {'left': 'true'})
    elif data == "right":
        socketio.emit('new_value', {'right': 'true'})
    elif data == "back":
        socketio.emit('new_value', {'back': 'true'})
    elif data == "ok":
        socketio.emit('new_value', {'ok': 'true'})


#def clkClicked(channel):
#   global counter
#   global step

#   clkState = GPIO.input(clk)
#   dtState = GPIO.input(dt)

#   if clkState == 0 and dtState == 1:
#       counter = counter + step
#       socketio.emit('new_value', {'left': 'true'})
#       print("Counter ", counter)


#def dtClicked(channel):
#   global counter
#   global step

#   clkState = GPIO.input(clk)
#   dtState = GPIO.input(dt)

#   if clkState == 1 and dtState == 0:
#       counter = counter - step
#       socketio.emit('new_value', {'right': 'true'})
#       print("Counter ", counter)


#def backClicked(channel):
#    socketio.emit('new_value', {'back': 'true'})
#    print("Back clicked")


#def okClicked(channel):
#    socketio.emit('new_value', {'ok': 'true'})
#    print("Ok clicked")


#GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=300)
#GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=300)
#GPIO.add_event_detect(back, GPIO.FALLING, callback=backClicked, bouncetime=300)
#GPIO.add_event_detect(ok, GPIO.FALLING, callback=okClicked, bouncetime=300)


@app.route('/reservation_page')
def reservation_page():
    return render_template('reservation_page.html')


@app.route('/reservation_completed')
def reservation_completed():
    return render_template('reservation_completed.html')


@app.route('/')
def start_screen():
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

#GPIO.cleanup()
