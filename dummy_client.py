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
                is_reserved = message["reserviert"]
                user_id = message["ID"]
                table_number = message["Tischnummer"]
                version_number = message["Versionsnummer"]

                if is_reserved:
                    print("Reservierung wurde gefunden mit folgenden Daten:")
                    reservation_date = message["Reservierungsdatum"]
                    reservation_time = message["Reservierungsuhrzeit"]
                    reservation_duration = message["Reservierungsdauer"]

                    print(str(user_id), "hat eine Reservierung für Tisch Nummer", str(table_number), "Reservierung am:",
                          str(reservation_date), "um", str(reservation_time), "Uhr und wurde für", str(reservation_duration), "gebucht")
                else:
                    print("Keine Reservierung gefunden")
                    print(str(user_id), str(table_number), str(version_number), "---- Nächste Reservierung ab: ", message["Nächste Reservierung"])

        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Invalid JSON format.")


def publish_message(client):
    print("Publishing a message...")
    message = {"ID": "0", "Tischnummer": "4", "Versionsnummer": "012345"}
    json_message = json.dumps(message)
    client.publish("denkraum/checkin", json_message)
    print(json_message)


client = mqtt.Client()
client.on_connect = on_connect  # Hier die Zuweisung vor dem Verbindungsaufbau
client.on_message = on_message  # Hier die Zuweisung vor dem Verbindungsaufbau
client.username_pw_set("user", "Test123")
client.connect(broker_address, port, 60)
client.subscribe("denkraum/response")
publish_message(client)
client.loop_forever()

publish_message(client)
