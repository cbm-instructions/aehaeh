#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#ifdef __AVR__

 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

#define RST_PIN         D3          // Configurable, see typical pin layout above
#define SS_PIN          D4          // Configurable, see typical pin layout above
#define PIN             D1          // NeoPixel PIN
#define NUMPIXELS       24          // Number of NeoPixels

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
String currentCardID = "0";   // Variable to store the ID of the current card
bool cardPresent = false;          // Flag to check if card is present

const char* ssid = "raspi";
const char* password = "Test1234";
const char* mqtt_server = "10.3.141.1";

// MQTT-Benutzername und Passwort
const char* mqtt_username = "user";
const char* mqtt_password = "Test123";

const int tischnnr = 1; 
unsigned long currentRequestVersion = 0;   // Variable to store the ID of the current card

int cardNotFoundCounter = 0;
String cardNotPresentTime = "";

String currentTime="";
String currentDate="1.1.1970";
String currentDay="DerTag";

int sendStatusCount = -1;

bool showPercentage = false;
int percentage = 50;
bool doCheckout = true;
String mode = "none";

///////////////////////// New Vars
unsigned long cardRemovedTimestamp = 0;  // Timestamp when the card is removed
bool isWaitingForCardReturn = false;     // Flag to indicate if we are in waiting mode
const unsigned long waitDuration = 60000; // 5 minutes in milliseconds
bool checkinSent = false; // This flag is true when check-in is sent, false otherwise
String lastCardID = "0"; // store the last card ID

// Global variables section
String lastKnownStatus = "none"; // Initialize with "none" or any default value
String lastKnownInfo = ""; // To store additional information if needed

unsigned long previousMillis = 0;
const long interval = 1000;

//Start end time for reservations()
String reservationStartTime="";
String reservationEndTime="1.1.1970";

///////////////////////// New Vars :END


WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
    delay(10);
    Serial.print("Connecting to WiFi");

 // Set a static IP address
    IPAddress staticIP(10, 3, 141, 121); // Your static IP
    IPAddress gateway(10, 3, 141, 1);    // Your gateway
    IPAddress subnet(255, 255, 255, 0);   // Your subnet
    IPAddress dns(1, 1, 1, 1);        // Your DNS

    WiFi.config(staticIP, gateway, subnet, dns);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        flashRed();
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        // Verwende den Benutzernamen und das Passwort für die Verbindung
        if (client.connect("ESP32Client", mqtt_username, mqtt_password)) {
            Serial.println("connected");
            
            // Nach erfolgreicher Verbindung zum Broker, abonniere das RFID-Topic
            client.subscribe("denkraum/response");
            client.subscribe("time");

        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            
            delay(1000);
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

    if(strcmp(topic, "time") == 0){
      Serial.print("Time set");
      currentTime = doc["Uhrzeit"].as<String>();
      currentDate = doc["Datum"].as<String>();
      currentDay = doc["Wochentag"].as<String>();
      //updatePercentage();
    }else{
      // Process the JSON message
      bool is_reserved = doc["reserviert"];
      int user_id = doc["ID"];
      int table_number = doc["Tischnummer"];
      int version_number = doc["Versionsnummer"];

      if (strcmp(topic, "denkraum/response") == 0) {
        int status_code = doc["Statuscode"].as<int>(); // Neues Feld für Statuscode
        int user_id = doc["ID"].as<int>();
        int table_number = doc["Tischnummer"].as<int>();
        Serial.println(status_code);


    switch (status_code) {
        case -1: {// Reservierung gefunden und Check-in rechtzeitig
          setColor(16,18,2);

          Serial.println("sent nextAT");

          char jsonBuffer[512];
          serializeJson(doc, jsonBuffer); // Serialize JSON data to buffer
          client.publish(("denkraum/tisch" + String(tischnnr) + "/display").c_str(), jsonBuffer);
          Serial.println("Reserveriung gefunden und aber zu früh");
          const char* reservation_date = doc["Reservierungsdatum"];
          const char* reservation_time = doc["Reservierungsuhrzeit"];
          int reservation_duration = doc["Reservierungsdauer"];
          //setColor(16,18,2);
          lastKnownStatus = "reservationAt";
          lastKnownInfo = String(reservation_time);
          reservationEndTime = reservation_time;
          reservationStartTime = currentTime;
          doCheckout=false;
          flashBlue();
                          //setColor(16,18,2);
          //setColor(0,10,0);
          }
        case 5: { // Reservierung gefunden, aber User zu spät
            Serial.println("Reserveriung gefunden aber zu spät");
            DynamicJsonDocument doc(1024);
            doc["next"] = doc[""];
            doc["status"] = "reservationClosed";

            char jsonBuffer[512];
            serializeJson(doc, jsonBuffer); // Serialize JSON data to buffer
            client.publish(("denkraum/tisch" + String(tischnnr) + "/display").c_str(), jsonBuffer);
            
            break;
          }
        case 1: {// Reservierung bereits abgeschlossen Todo status //TODO: 
            // Keine weiteren Aktionen erforderlich
            Serial.println("Reservierung bereits abgeschlossen");
            DynamicJsonDocument doc(1024);
            doc["next"] = doc[""];
            doc["status"] = "reservationInvalid";

            char jsonBuffer[512];
            serializeJson(doc, jsonBuffer); // Serialize JSON data to buffer
            client.publish(("denkraum/tisch" + String(tischnnr) + "/display").c_str(), jsonBuffer);
            flashBlue();
            delay(1000);
            flashRed();
            delay(1000);
            flashRed();
            delay(1000);
            doCheckout=false;
            break;
          }
        case 2: {// Reservierung jetzt checkedin
            // Keine weiteren Aktionen erforderlich
            Serial.println("Reservierung gefunden! checking in!");
            const char* reservation_date = doc["Reservierungsdatum"];
            const char* reservation_time = doc["Reservierungsuhrzeit"];
            int reservation_duration = doc["Reservierungsdauer"];
            /*DynamicJsonDocument doc(1024);
            doc["next"] = doc[""];
            doc["status"] = "reservationClosed";

            char jsonBuffer[512];
            serializeJson(doc, jsonBuffer); // Serialize JSON data to buffer
            client.publish(("denkraum/tisch" + String(tischnnr) + "/display").c_str(), jsonBuffer);*/
            lastKnownStatus = "reservationSet"; // or any other appropriate status
            lastKnownInfo = ""; // Store additional info if needed
            setDisplay("reservationSet","");
            flashBlue();
            //Reservierung erfolgreich angenommen!!
            //setColor(16,18,2);
            lastKnownStatus = "elapsedTime";
            String reservationEndTimLocal = addMinutesToTime(reservation_time,String(reservation_duration));
            reservationEndTime = reservationEndTimLocal;
            reservationStartTime = reservation_time;
            String diff = timeDifferenceString(reservationEndTime, currentTime);
            lastKnownInfo = diff;
            doCheckout=true;

            break;
          }
        case 0: {// Keine Reservierung gefunden
            Serial.println("Keine Reserveriung gefunden");
            // Nächste Reservierung abfragen und verarbeiten
            const char* next_reservation = doc["Nächste Reservierung"].as<const char*>();
              if (strcmp(next_reservation, "None") == 0) { //Keine Reserveirung heute für den Tisch
                Serial.print("Keine Reservierung für disen Tisch an dem Tag");
                DynamicJsonDocument doc(1024);
                doc["next"] = doc["Nächste Reservierung"];
                doc["status"] = "free";

                char jsonBuffer[512];
                serializeJson(doc, jsonBuffer); // Serialize JSON data to buffer
                client.publish(("denkraum/tisch" + String(tischnnr) + "/display").c_str(), jsonBuffer);
                lastKnownStatus = "noReservation";
                lastKnownInfo = "";
                doCheckout=false;
                flashBlue();
                setColor(0, 10, 0);

              
              }else{ //Eine Reservierung für den Tisch:
                setColor(16,18,2);
                DynamicJsonDocument doc(1024);
                doc["next"] = doc["Nächste Reservierung"];
                doc["status"] = "nextAt";
                Serial.println("sent nextAT");

                char jsonBuffer[512];
                serializeJson(doc, jsonBuffer); // Serialize JSON data to buffer
                client.publish(("denkraum/tisch" + String(tischnnr) + "/display").c_str(), jsonBuffer);
                lastKnownStatus = "reservationAt";
                lastKnownInfo = String(next_reservation);
                reservationEndTime = next_reservation;
                reservationStartTime = currentTime;
                doCheckout=false;

              }
            break;
          }
      }
    }
    checkinSent=true;
    cardPresent=true;
    lastCardID=currentCardID;
    setDisplay(lastKnownStatus,lastKnownInfo);
  }
}

String addMinutesToTime(const String& timeStr, const String& minutesStr) {
    int hours, minutes, addMinutes;

    // Parse hours and minutes from the time string
    sscanf(timeStr.c_str(), "%d:%d", &hours, &minutes);

    // Convert minutes string to integer
    addMinutes = minutesStr.toInt();

    // Add minutes
    minutes += addMinutes;

    // Adjust for overflow in minutes and hours
    hours += minutes / 60;
    minutes %= 60;
    hours %= 24; // Adjust if hours exceed 24

    // Create a new time string
    char newTime[6]; // Enough space for "HH:MM\0"
    sprintf(newTime, "%02d:%02d", hours, minutes);
    return String(newTime);
}

int timeStringToMinutes(const String& timeStr) {
    int hours, minutes;
    sscanf(timeStr.c_str(), "%d:%d", &hours, &minutes);
    return hours * 60 + minutes;
}

String timeDifferenceString(const String& endTimeStr, const String& currentTimeStr) {
    int endTime = timeStringToMinutes(endTimeStr);
    int currentTime = timeStringToMinutes(currentTimeStr);
    int diff = endTime - currentTime;

    if (diff < 0) {
        diff += 24 * 60; // Adjust for next day
    }

    int hours = diff / 60;
    int minutes = diff % 60;

    return String(hours) + " h " + String(minutes) + " min";
}

void timeExpired() {
    // This function is called when time expires
    isWaitingForCardReturn = false;
    checkinSent = false; // Allow the next check-in to be sent
    cardRemovedTimestamp = 0; // Reset timer
    Serial.println("Time expired, waiting mode off.");
    sendCheckout();
}

void setInitialView(){
  setDisplay("none","");
  setColor(0,10,0); 
  delay(250);
}

void sendCheckout(){
  //Sending checkout to server
    DynamicJsonDocument doc(1024);
  doc["next"] = "test";
  doc["status"] = "reset";

  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer); // Serialize JSON data to buffer
  client.publish(("denkraum/tisch" + String(tischnnr) + "/display").c_str(), jsonBuffer);

  doc["ID"] = currentCardID;
  doc["Tischnummer"] = tischnnr;
  doc["Reservierungsdatum"] = currentDate;
  doc["Reservierungsuhrzeit"] = reservationStartTime;

  serializeJson(doc, jsonBuffer); // Serialize JSON data to buffer
  client.publish("Denkraum/checkout", jsonBuffer);
  //Sending checkout to server :END

  currentCardID="0";
  lastCardID="0";
  cardPresent=false;
  cardNotFoundCounter=-1;
  setDisplay("reservationClosed","");
  //setColor(30,10,70);
  flashBlue();
  delay(3000);
  setInitialView();
  lastKnownStatus="none";
  lastKnownInfo="";
  reservationEndTime="";
  reservationStartTime="";
  isWaitingForCardReturn=false;
  checkinSent=false;
  delay(1000);
  setColor(0,20,0);
}

//This method will set the display state
void setDisplay(String status, String info) {
    // Create a JSON object to hold the data
    DynamicJsonDocument doc(512);
    doc["status"] = status;
    doc["info"] = info;

    // Convert JSON object to String
    String output;
    serializeJson(doc, output);

    // Publish the message to the display topic
    client.publish(("denkraum/tisch" + String(tischnnr) + "/display").c_str(), output.c_str());
}

void setup() {
  pixels.begin(); // Initialize NeoPixel

  Serial.begin(115200);
  SPI.begin(); // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(onMessage);
  while (!Serial); // Wait for serial port to connect
  SPI.begin();
  mfrc522.PCD_Init(); // Init MFRC522
  delay(4);
  mfrc522.PCD_DumpVersionToSerial(); // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
  setColor(0, 20, 0);
}

void loop() {
    maintainMQTTConnection();  // Ensure the device stays connected to the MQTT broker

    if(!currentTime.equals("")){
    static int lastPrintedSecond = -1;
    MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
    mfrc522.PCD_Init(); // Init MFRC522
    delay(100);                // Small delay to prevent overwhelming the loop
    readRFID();                // Read the RFID card and handle presence/absence

    if (isWaitingForCardReturn) {
        unsigned long currentTime = millis();
        unsigned long elapsedTime = currentTime - cardRemovedTimestamp;
        unsigned long timeLeft = waitDuration - elapsedTime;

        // Calculate minutes and seconds remaining
        int minutesLeft = timeLeft / 60000;
        int secondsLeft = (timeLeft % 60000) / 1000;

        // Calculate the percentage of time left
        float percentLeft = (float)timeLeft / (float)waitDuration * 100.0;
        // Print once every 5 seconds to Serial

      if(!doCheckout){
          Serial.println("setting everything to 0");
          checkinSent = false; // Allow the next check-in to be sent
          cardRemovedTimestamp = 0; // Reset timer
          currentCardID="0";
          lastCardID="0";
          cardPresent=false;
          cardNotFoundCounter=-1;
          setColor(30,10,30);
          delay(1000);
          setInitialView();
          lastKnownStatus="none";
          lastKnownInfo="";
          reservationEndTime="";
          reservationStartTime="";
          isWaitingForCardReturn=false;
          checkinSent=false;
          setColor(0,50,0);
          doCheckout=true;
        }else if (secondsLeft % 5 == 0 && lastPrintedSecond != secondsLeft) {
            Serial.print("Time left: ");
            Serial.print(minutesLeft);
            Serial.print(" minutes ");
            Serial.print(secondsLeft);
            Serial.println(" seconds");
            Serial.print("Percent time left: ");
            Serial.println(percentLeft);
            lastPrintedSecond = secondsLeft;
            publishTimeLeft(minutesLeft, secondsLeft);
            displayRedPercentage((int)percentLeft);
        }
        
        // Check if time has expired
        if (currentTime - cardRemovedTimestamp >= waitDuration && doCheckout) {
            timeExpired(); // Handle time expiration
        }
    }else if(strcmp(lastKnownStatus.c_str(), "reservationAt") == 0){
        int difference_between_start_and_and = time_difference(reservationStartTime.c_str(), reservationEndTime.c_str());
        int difference_between_current_and_and = time_difference(currentTime.c_str(), reservationEndTime.c_str());
        float percentLeft = (float)difference_between_current_and_and / (float)difference_between_start_and_and * 100.0;
        if(percentLeft<=0){
          sendCheckout();
        }
        //Serial.println(percentLeft);
        displayGreenPercentage(percentLeft);
        //reservationEndTime = next_reservation;
        //reservationStartTime = currentTime;
    }else if(strcmp(lastKnownStatus.c_str(), "elapsedTime") == 0){
        int difference_between_start_and_and = time_difference(reservationStartTime.c_str(), reservationEndTime.c_str());
        int difference_between_current_and_and = time_difference(currentTime.c_str(), reservationEndTime.c_str());
        float percentLeft = (float)difference_between_current_and_and / (float)difference_between_start_and_and * 100.0;
        if(percentLeft<=0){
          sendCheckout();
        }
        String diff = timeDifferenceString(reservationEndTime, currentTime);

        Serial.println("Time difference: " + diff);
        lastKnownInfo = diff;
        Serial.println(percentLeft);
        displayPercentage(percentLeft);
    }

    updateDisplayIfNeeded();   // Update display and LED ring if necessary
    }else{
      Serial.print("-");
      delay(200);
    }
}

void maintainMQTTConnection() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
}

void readRFID() {
    String readID = getID();
    if (readID != "0") {
        cardIsPresent(readID);
    } else {
        handleCardAbsent();
    }
}

void updateDisplayIfNeeded() {
  unsigned long currentMillis = millis();
    if ((unsigned long)(currentMillis - previousMillis) >= interval) {
      if(!isWaitingForCardReturn){
        //Serial.println("Updating display due to time interval");
        setDisplay(lastKnownStatus,lastKnownInfo);
        previousMillis = currentMillis;
      }
  }
}
/////// Card states
void cardIsPresent(String readID) {
    if (!lastCardID.equals(readID) && !currentCardID.equals("0")) {
      setColor(100,0,0);
      setDisplay("wrongHSCard","");
      delay(2000);
      isWaitingForCardReturn = true;
      handleCardAbsent();
    }else{
        // New card detected or same card returned after removal
        currentCardID = readID;
      if (isWaitingForCardReturn && lastCardID.equals(readID)) {            // Same card has returned, reset the waiting mode and timers
            isWaitingForCardReturn = false;
            setColor(0,20,0); // Change color or any indication of card detection
            //checkinSent = false; // Allow check-in to be sent again
            cardRemovedTimestamp = 0; // Reset timer
            cardPresent=true;
            Serial.println("Card returned, resetting timer.");
        } else {
            // New card detected, proceed with normal check-in
            //Serial.println("Card Detected: " + String(readID));
            //setColor(0,20,0); // Change color or any indication of card detection
            if(!checkinSent){
                publishCardPresent(currentCardID); // Check-in with server
                //Serial.println("sendingcheckin");
            }else{
                //Serial.println("chekinalreadysent");
            }
        }
        cardNotFoundCounter = 0;
        cardNotPresentTime = "";
        lastCardID = readID;
    }
    // Reset card not found counter and not present time
    
}

void handleCardAbsent() {
    cardNotFoundCounter++;
    if (cardNotFoundCounter >= 5 && cardPresent && doCheckout) {
        enterWaitMode();  // Enter a mode that waits 5 minutes or handles absence
        //Serial.println("null waiting mode");

    }else if(cardNotFoundCounter >= 10 && cardPresent && !lastCardID.equals("0")){
          Serial.println("bigger tgan 5 and iswaitingforcardreturn");
          Serial.println("setting everything to 0");
          checkinSent = false; // Allow the next check-in to be sent
          cardRemovedTimestamp = 0; // Reset timer
          currentCardID="0";
          lastCardID="0";
          cardPresent=false;
          cardNotFoundCounter=-1;
          lastKnownStatus="none";
          lastKnownInfo="";
          reservationEndTime="";
          reservationStartTime="";
          isWaitingForCardReturn=false;
          checkinSent=false;
          doCheckout=true;
          setInitialView();
    }

}

void enterWaitMode() {
    cardPresent = false;
    isWaitingForCardReturn = true;
    cardRemovedTimestamp = millis(); // Start the timer
    Serial.println("Waiting mode started.");
    //publishWaitMode();
}

void resetCardAbsentState() {
    cardNotFoundCounter = 0;
    if (cardNotPresentTime != "") {
        cardNotPresentTime = "";  // Reset the absent time tracker
    }
}

void publishTimeLeft(int minutes, int seconds) {
    Serial.println("Would publish the time left");
    String timeLeftStr = String(minutes) + "min " + String(seconds) + "sec";
    setDisplay("reservationDeletesIn",timeLeftStr);
}

/// Publishing MQTT Messages
void publishCardPresent(String cardID) {
    checkinSent=true;
    currentCardID=cardID;
    String jsonData = createJson(cardID, "Card Present");
    Serial.println("Publishing check-in for card ID: " + String(cardID));
    client.publish("denkraum/checkin", jsonData.c_str());
}

void publishWaitMode() {
    // Send a message indicating the system is waiting due to card absence
    DynamicJsonDocument doc(256);
    doc["status"] = "waiting";
    doc["info"] = "Waiting for card to return or timeout";

    char jsonBuffer[512];
    serializeJson(doc, jsonBuffer);
    client.publish("denkraum/status", jsonBuffer);
}

///
void sendCardID(){
  if (!client.connected()) {
        reconnect();
    }
    String exampleData = "hgallo"; // Example string data

    // Create JSON string
    String jsonData = createJson(currentCardID, exampleData);
    client.subscribe("denkraum/response");
    client.publish("denkraum/checkin", jsonData.c_str());
    MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

}

String createJson(String id, const String& dataString) {
    // Create a JSON object
    StaticJsonDocument<200> doc; // Adjust size based on your data requirements
    currentRequestVersion = random(1000,9999);
    // Add data to the JSON object
    doc["ID"] = currentCardID;
    doc["Tischnummer"] = tischnnr;
    doc["Versionsnummer"] = currentRequestVersion;


    // Convert JSON object to String
    String jsonString;
    serializeJson(doc, jsonString);

    return jsonString;
}


void flashRed() {
  for (int i = 0; i < 2; i++) { // Flash 3 times
    setColor(10, 0, 0); // Red color
    delay(100);
    pixels.clear();
    pixels.show();
    delay(100);
  }
}

void setYellow() {
    pixels.clear();
    pixels.show();
    setColor(26,18,3);
}

void flashBlue() {
  for (int i = 0; i < 3; i++) { // Flash 3 times
    setColor(0, 0, 255); // Red color
    delay(200);
    pixels.clear();
    pixels.show();
    delay(200);
  }
}

void setLoading(){
      // Turn on LEDs from 0 to 23 with random delays
    for (int i = 0; i < NUMPIXELS; ++i) {
        pixels.setPixelColor(i, pixels.Color(0, 150, 0)); // Red color, adjust as needed
        pixels.show();
        delay(random(50, 200)); // Random delay between 50ms to 200ms
    }

    // Turn off LEDs from 23 to 0 with random delays
    for (int i = NUMPIXELS - 1; i >= 0; --i) {
        pixels.setPixelColor(i, pixels.Color(0, 0, 0)); // Turn off LED
        pixels.show();
        delay(random(50, 200)); // Random delay between 50ms to 200ms
    }
}

void displayPercentage(int percent) {
    pixels.clear(); // Clear all LEDs

    // Calculate the number of LEDs to light up based on the percentage
    int ledsToLight = (NUMPIXELS * percent) / 100;

    // Light up the calculated number of LEDs in green
    for (int i = 0; i < ledsToLight; ++i) {
        pixels.setPixelColor(NUMPIXELS - i, pixels.Color(10, 0, 0)); // Beige
    }

    pixels.show();
}

void displayGreenPercentage(int percent) {
    pixels.clear(); // Clear all LEDs

    // Calculate the number of LEDs to light up based on the percentage
    int ledsToLight = (NUMPIXELS * percent) / 100;

    // Light up the calculated number of LEDs in green
    for (int i = 0; i < ledsToLight; ++i) {
        pixels.setPixelColor(NUMPIXELS - i, pixels.Color(0, 10, 0)); // Beige
    }

    pixels.show();
}

void displayRedPercentage(int percent) {
    pixels.clear(); // Clear all LEDs

    int ledsToLight = (NUMPIXELS * percent) / 100;
    for (int i = 0; i < NUMPIXELS; ++i) {
        if (i < ledsToLight) {
            pixels.setPixelColor(NUMPIXELS-i, pixels.Color(40, 0, 0)); // Green color
        } else {
            //pixels.setPixelColor(NUMPIXELS-i, pixels.Color(10, 10, 10));
        }
    }
    pixels.show();
}

void setColor(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < NUMPIXELS; i++) {
    pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
  pixels.show();
}

void lightUpNeopixels() {
  // Example: Light up NeoPixels with a random color (modify as needed)
  int r = random(10, 255);
  int g = random(10, 255);
  int b = random(10, 255);
  setColor(r, g, b);
}

int timeDifference(String startTime, String endTime) {
    // Parse hours and minutes from start time
    int startHours = startTime.substring(0, 2).toInt();
    int startMinutes = startTime.substring(3, 5).toInt();

    // Parse hours and minutes from end time
    int endHours = endTime.substring(0, 2).toInt();
    int endMinutes = endTime.substring(3, 5).toInt();

    // Convert both times to minutes
    int startTimeInMinutes = startHours * 60 + startMinutes;
    int endTimeInMinutes = endHours * 60 + endMinutes;

    // Calculate the difference
    int difference = endTimeInMinutes - startTimeInMinutes;

    // Return the absolute value of difference
    return abs(difference);
}

int time_difference(const char* time1, const char* time2) {
    int hours1, minutes1, hours2, minutes2;

    // Extract hours and minutes from the time strings
    sscanf(time1, "%d:%d", &hours1, &minutes1);
    sscanf(time2, "%d:%d", &hours2, &minutes2);

    // Convert both times to minutes
    int total_minutes1 = hours1 * 60 + minutes1;
    int total_minutes2 = hours2 * 60 + minutes2;

    // Calculate the difference in minutes
    int difference = total_minutes1 - total_minutes2;

    // Return the absolute value of the difference
    return (difference >= 0) ? difference : -difference;
}

//Cardlogic

String getID() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return "0";
  }
  /*unsigned long cardID = 0;
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    cardID <<= 8;
    cardID |= mfrc522.uid.uidByte[i];
  }*/
  char str[32] = "";
    int size = sizeof(mfrc522.uid.uidByte) / sizeof(mfrc522.uid.uidByte[0]);
   //array_to_string(mfrc522.uid.uidByte, size, str); //Insert (byte array, length, char array for output)
   //Serial.println(str); //Print the output uid string
  // Serial.println(hex_to_int(str));
   byte nuidPICC[size];

    for (byte i = 0; i < size; i++) {
      nuidPICC[i] = mfrc522.uid.uidByte[i];
    }
   
  String hexval = getHexValue(mfrc522.uid.uidByte, mfrc522.uid.size);
     //Serial.print(mfrc522.PICC_ReadCardSerial());
    //mfrc522.PICC_DumpToSerial(&(mfrc522.uid));

    long code=0; 
    for (byte i = 0; i < mfrc522.uid.size; i++){
      code=((code+mfrc522.uid.uidByte[i])*10); 
    }
    //Serial.println(code);

  mfrc522.PICC_HaltA();
  return hexval;
}
void printArray(int arr[], int size) {
    printf("Array elements: ");
    for(int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

void array_to_string(byte array[], unsigned int len, char buffer[])
{
   for (unsigned int i = 0; i < len; i++)
   {
      byte nib1 = (array[i] >> 4) & 0x0F;
      byte nib2 = (array[i] >> 0) & 0x0F;
      buffer[i*2+0] = nib1  < 0xA ? '0' + nib1  : 'A' + nib1  - 0xA;
      buffer[i*2+1] = nib2  < 0xA ? '0' + nib2  : 'A' + nib2  - 0xA;
   }
   buffer[len*2] = '\0';
}

unsigned long hex_to_int(const char *hex_value) {
    return strtoul(hex_value, NULL, 16);
}
void printHex(byte *buffer, byte bufferSize) { //Loops as big as UID size
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " "); //Ternary returns 0 if < 0x10
    Serial.print(buffer[i], HEX);
  }
}

String getHexValue(byte *buffer, byte bufferSize) {
  String hexString = ""; // Erstellen eines leeren String-Objekts
  // Schleife so groß wie die Puffergröße
  for (byte i = 0; i < bufferSize; i++) {
    // Ternärer Operator gibt " 0" zurück, wenn der Wert < 0x10 ist, sonst " "
    hexString += (buffer[i] < 0x10 ? " 0" : " ");
    // Konvertiere den Byte-Wert in einen Hexadezimal-String und füge ihn zum String hinzu
    char hexChar[3]; // 2 Zeichen für Hex-Bytes und 1 für '\0'
    sprintf(hexChar, "%02X", buffer[i]); // Konvertiere Byte zu Hexadezimal-String
    hexString += hexChar;
  }

  hexString.replace(" ", "");
  if (hexString.startsWith("0")) {
    hexString = hexString.substring(1);
  }

  int index = 6;//hexString.indexOf("48");
  if (index != -1) {
    hexString = hexString.substring(0, index);
  }

  return hexString; // Gebe den gesammelten Hexadezimal-String zurück
}
