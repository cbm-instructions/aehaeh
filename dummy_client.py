import paho.mqtt.client as mqtt
import json
from datetime import datetime

broker_address = "localhost"
port = 1883
response_topic = "response_topic"
is_reservation = False


def on_connect(client, userdata, flags, rc):
    print("Verbunden mit dem MQTT Broker.")


def on_message(client, userdata, msg):
    if isinstance(msg, str):
        print("Received plain text message:", msg)
    else:
        try:
            decoded_payload = msg.payload.decode()
            message = json.loads(decoded_payload)
            print("Received JSON message:", message)
            print(msg.topic)

            if msg.topic == "denkraum/response":
                statuscode = message["Statuscode"]
                user_id = message["ID"]
                table_number = message["Tischnummer"]
                version_number = message["Versionsnummer"]

                if statuscode == "0":
                    print("Keine Reservierung gefunden.")
                    print("User ID: ", str(user_id), "---", "Tisch Nummer:", str(table_number), "---",
                          "Versions Nummer:", str(version_number), "---", "Nächste Reservierung für diesen Tisch:",
                          message["Nächste Reservierung"])

                elif statuscode == "-1":
                    print("Reservierung wurde gefunden mit folgenden Daten:")
                    reservation_date = message["Reservierungsdatum"]
                    reservation_time = message["Reservierungsuhrzeit"]
                    reservation_duration = message["Reservierungsdauer"]

                    print("Willkommen", str(user_id), "Du hast eine Reservierung für Tisch Nummer", str(table_number),
                          "betätigt. Die Reservierung ist für den",
                          str(reservation_date), "um", str(reservation_time), "Uhr registriert worden und wurde für",
                          str(reservation_duration), "Minuten gebucht!")
                else:
                    print("Reservierung ist entweder abgelaufen oder findet erst später statt.")
                    print("User ID: ", str(user_id), "---", "Tisch Nummer:", str(table_number), "---",
                          "Versions Nummer:", str(version_number), "---", "Nächste Reservierung für diesen Tisch:",
                          message["Nächste Reservierung"])


        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Invalid JSON format.")


def checkin_to_reservation(client):
    print("Publishing a message...")
    message = {"ID": "0", "Tischnummer": "1", "Versionsnummer": "012345"}
    json_message = json.dumps(message)
    client.publish("denkraum/checkin", json_message)
    print(json_message)


def checkout_from_reservation(client):
    message = {"ID": "0", "Tischnummer": "4", "Reservierungsdatum": "20.01.2024", "Reservierungsuhrzeit": "10:45"}
    json_message = json.dumps(message)
    client.publish("Denkraum/checkout", json_message)
    print(json_message)


client = mqtt.Client()
client.on_connect = on_connect  # Hier die Zuweisung vor dem Verbindungsaufbau
client.on_message = on_message  # Hier die Zuweisung vor dem Verbindungsaufbau
client.username_pw_set("user", "Test123")
client.connect(broker_address, port, 60)
client.subscribe("denkraum/response")
checkin_to_reservation(client)
#checkout_from_reservation(client)
client.loop_forever()

checkin_to_reservation(client)
