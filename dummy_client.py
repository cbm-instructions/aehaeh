import paho.mqtt.client as mqtt
import json

broker_address = "localhost"
port = 1883
response_topic = "response_topic"
is_reservation = False


def on_connect(client, userdata, flags, rc):
    print("Verbunden mit dem MQTT Broker.")


def on_message(client, userdata, msg):
    decoded_payload = msg.payload.decode()
    if isinstance(decoded_payload, str):
        if msg.topic == "time":
            message = json.loads(decoded_payload)
            aktuelle_uhrzeit = message["Uhrzeit"]
            aktuelles_datum = message["Datum"]
            print("Aktuelle Uhrzeit: ", aktuelle_uhrzeit, " ; Aktuelles Datum: ", aktuelles_datum)
    else:
        try:
            message = json.loads(decoded_payload)
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Invalid JSON format.")


client = mqtt.Client()
client.on_connect = on_connect  # Hier die Zuweisung vor dem Verbindungsaufbau
client.on_message = on_message  # Hier die Zuweisung vor dem Verbindungsaufbau
client.username_pw_set("user", "Test123")
client.connect(broker_address, port, 60)
client.subscribe("time")
client.loop_forever()