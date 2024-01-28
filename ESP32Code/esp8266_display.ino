#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>
#include <ArduinoJson.h>
#include <stdio.h>



#define CS -1 // beclaration of Chip Sel
#define DC 5 // Declaration of Data / Command Pin
#define RST 4 // Declaration of RESET Pin

// Initialize display
Adafruit_ST7789 lcd = Adafruit_ST7789(CS, DC, RST);


const char* ssid = "raspi";
const char* password = "Test1234";
const char* mqtt_server = "10.3.141.1";

// MQTT-Benutzername und Passwort
const char* mqtt_username = "raspi";
const char* mqtt_password = "Test1234";

const int tischnnr = 1; 

String currentTime="";
String currentDate="1.1.1970";
String currentDay="DerTag";

WiFiClient espClient;
PubSubClient client(espClient);

String displayStatus = "none";
String displayNextTime = "";
int updateCounter=0;

String lastTimeOuput = "";
String timeToDisplay = "";

String lastKnownStatus = "";
String lastKnownInfo = "";


unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void setup_wifi() {
    delay(10);
    Serial.print("Connecting to WiFi(display)");

 // Set a static IP address
  /*  IPAddress staticIP(10, 3, 141, 151); // Your static IP
    IPAddress gateway(10, 3, 141, 1);    // Your gateway
    IPAddress subnet(255, 255, 255, 0);   // Your subnet
    IPAddress dns(1, 1, 1, 1);        // Your DNS

    WiFi.config(staticIP, gateway, subnet, dns);*/

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi(Display) connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        // Verwende den Benutzernamen und das Passwort für die Verbindung
        if (client.connect("ESP32ClientDisplay", mqtt_username, mqtt_password)) {
            Serial.println("connected");
            
            // Nach erfolgreicher Verbindung zum Broker, abonniere das RFID-Topic
            client.subscribe("denkraum/response");
            client.subscribe("time");
            String displayTopic = "denkraum/tisch" + String(tischnnr) + "/display";
            //const char* topic = displayTopic.c_str();

            client.subscribe(displayTopic.c_str());


        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 1 seconds");
        }
    }
}

void onMessage(char* topic, byte* payload, unsigned int length) {
    // Convert byte array to a string
    char message[length + 1];
    for (int i = 0; i < length; i++) {
        message[i] = (char)payload[i];
    }
    message[length] = '\0';

    // Check if the message is a valid JSON
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, message);

    if (error) {
        Serial.print("Error decoding JSON: ");
        Serial.println(error.c_str());
        return;
    }

    // Process the JSON message
    bool is_reserved = doc["reserviert"];
    int user_id = doc["ID"];
    int table_number = doc["Tischnummer"];
    int version_number = doc["Versionsnummer"];

    if(strcmp(topic, "time") == 0){
      Serial.print("/timeSet/");
      currentTime = doc["Uhrzeit"].as<String>();
      currentDate = doc["Datum"].as<String>();
      currentDay = doc["Wochentag"].as<String>();

    }else if(strcmp(topic, ("denkraum/tisch" + String(tischnnr) + "/display").c_str()) == 0){
      String status = doc["status"];
      String info = doc["info"]; // This may be an empty string if "info" is not applicable

      updateDisplay(status, info);
    }else{
      Serial.println(topic);
    }
}

void setup(void) {
  lcd.init(240, 240, SPI_MODE2);
  lcd.setRotation(1);
  Serial.begin(115200);
  lcd.fillScreen(0x22ED);
  lcd.setCursor(20, 100);
  lcd.setTextColor(ST77XX_WHITE);
  lcd.setTextSize(2);
  setText("Connecting to Wifi",2);
  setup_wifi();
  client.setServer(mqtt_server, 8883);
  client.setCallback(onMessage);
  while (!Serial); // Wait for serial port to connect
  setText("Connected",4);

  delay(1500);
  char strNr[12]; 
  sprintf(strNr, "%d", tischnnr);
  setDoubleText("Tisch Nr:",strNr);
  // fill pisplay with a colour and a String
}

void setDoubleText(String text1,String text2){
  lcd.fillScreen(0x22ED);
  lcd.flush();
  lcd.setCursor(20, 60);
  lcd.setTextColor(ST77XX_WHITE);
  lcd.setTextSize(3);
  lcd.print(text1);
  lcd.setCursor(20, 120);
  lcd.print(text2);
}

void setText(String text, int size){
  lcd.fillScreen(0x22ED);
  lcd.flush();
  lcd.setCursor(20, 100);
  lcd.setTextColor(ST77XX_WHITE);
  lcd.setTextSize(size);
  lcd.print(text);
}

//screens
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  /*if(updateCounter>=30){
    updateCounter=0;
    if(displayStatus=="none"){
      char strNr[12]; 
      sprintf(strNr, "%d", tischnnr);
      setDoubleText("Tisch Nr:",strNr);
    }else if(displayStatus=="noReservation"){
      setNoReservation();
    }else if(displayStatus=="reservationAt"){
      setNextReservationAt(displayNextTime);
    }else{
        Serial.print(displayStatus);
    }
  }else{
    updateCounter++;
  }*/
}

void updateDisplay(String status, String info) {
  Serial.print(status);
  Serial.println(info);
    if (status != lastKnownStatus || info != lastKnownInfo) {
      // Update the display based on the current status and additional information
      if (status == "none") {
          // When there is no specific status, perhaps default to showing table number or some welcome message
        setHeading();
        char strNr[12]; 
        sprintf(strNr, "%d", tischnnr);
        setDoubleText("Tisch Nr:",strNr);
      } else if (status == "noReservation") {
          // Handle the no reservation status
          setNoReservation();
      } else if (status == "reservationAt") {
          // Display the next reservation time
          setNextReservationAt(info); // Assuming info contains the next reservation time
      } else if (status == "reservationDeletesIn") {
          // Display the time until the reservation is deleted
          setReservationDeletesIn(info); // Assuming info contains the time until reservation deletes
      } else if (status == "wrongHSCard") {
          // Display an error message for wrong HS card
          setWrongHSCard();
      } else if (status == "reservationSet") {
          // Display a confirmation message for reservation set
          setReservationSet();
      } else if (status == "elapsedTime") {
          // Display the elapsed time of current reservation
          setElapseTime(info); // Assuming info contains the elapsed time
      } else if (status == "cardMissing") {
          // Display a message for missing card with remaining time
          setCardMissing(info); // Assuming info contains the time until the card is considered missing
      } else if (status == "reservationClosed") {
          // Display a message that the reservation is closed
          setReservationClosed();
      } else if (status == "reservationExited") {
          // Display a message that the reservation is exited or cancelled
          setReservationExited();
      } else {
          // Handle unknown status or log an error
          Serial.println("Unknown status received!");
          Serial.println(status);
      }
      lastKnownStatus = status;
      lastKnownInfo = info;
    }else{
      Serial.println("nothing changed");
    }
}


void setHeading(){
  lcd.fillScreen(0x22ED);
  lcd.flush();
  lcd.setCursor(10, 10);
  lcd.setTextColor(ST77XX_WHITE);
  lcd.setTextSize(3);
  lcd.print("Tisch1");
  lcd.setCursor(145, 10); //x y
  lcd.setTextColor(ST77XX_WHITE);
  lcd.setTextSize(3);
  lcd.print(currentTime);
  lcd.drawLine(0, 40, 240, 40, 0x07E0);
}
void setNoReservation(){
  setHeading();
  lcd.setTextSize(3);
  lcd.setCursor(10, 80);
  lcd.print("Aktuell");
  lcd.setCursor(10, 120);
  lcd.print("keine");
  lcd.setCursor(10, 160);
  lcd.print("Reservierung");
}

void setNextReservationAt(String time){
  setHeading();
  lcd.setTextSize(3);
  lcd.setCursor(10, 80);
  lcd.print("Naechste");
  lcd.setCursor(10, 120);
  lcd.print("Reservierung");
  lcd.setCursor(10, 160);
  lcd.print(time);
}

void setReservationDeletesIn(String time){
  setHeading();
  lcd.setTextSize(3);
  lcd.setCursor(10, 70);
  lcd.print("Reservierung");
  lcd.setCursor(10, 100);
  lcd.print("verfaellt");
  lcd.setCursor(10, 130);
  lcd.print("in");
  lcd.setTextColor(ST77XX_ORANGE);
  lcd.setCursor(10, 160);
  lcd.print(time);
}

void setWrongHSCard(){
  setHeading();
  lcd.setTextColor(ST77XX_RED);
  lcd.setTextSize(5);
  lcd.setCursor(10, 80);
  lcd.print("Falsche");
  lcd.setCursor(10, 120);
  lcd.print("HS-");
  lcd.setCursor(10, 160);
  lcd.print("Karte");
}

void setReservationSet(){
  setHeading();
  lcd.setTextColor(ST77XX_GREEN);
  lcd.setTextSize(3);
  lcd.setCursor(10, 80);
  lcd.print("Reservierung");
  lcd.setCursor(10, 120);
  lcd.print("gesetzt");
  lcd.setCursor(10, 160);
  lcd.print("(check)");
}

void setElapseTime(String time){
  setHeading();
  lcd.setTextColor(ST77XX_WHITE);
  lcd.setTextSize(3);
  lcd.setCursor(10, 80);
  lcd.print("Verbleibende");
  lcd.setCursor(10, 120);
  lcd.print("Zeit");
  lcd.setCursor(10, 160);
  lcd.print(time);
}

void setCardMissing(String time){
  setHeading();
  lcd.setTextSize(3);
  lcd.setCursor(10, 70);
  lcd.print("Bitte legen");
  lcd.setCursor(10, 100);
  lcd.print("sie ihre HS-");
  lcd.setCursor(10, 130);
  lcd.print("Karte auf");
  lcd.setTextColor(ST77XX_ORANGE);
  lcd.setCursor(10, 160);
  lcd.print(time);
}

void setReservationClosed(){
  setHeading();
  lcd.setTextSize(3);
  lcd.setCursor(10, 80);
  lcd.print("Reservation");
  lcd.setCursor(10, 120);
  lcd.print("aufgehoben");
  //lcd.setCursor(10, 160);
  //lcd.print(time);
}

void setReservationExited(){
  setHeading();
  lcd.setTextSize(3);
  lcd.setCursor(10, 80);
  lcd.print("Ihre Reserva");
  lcd.setCursor(10, 120);
  lcd.print("tion ist nun");
  lcd.setCursor(10, 160);
  lcd.print("aufgehoben");
}
