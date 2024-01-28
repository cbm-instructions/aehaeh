# Team Äähh? - Bauanleitung Tisch-Reservierungs-Tool

## Challenge
    Wie können wir durch smarte Devices Leonie dabei helfen, dass die Aufenthaltsqualität an der Hochschule steigt?

Ziel ist es, eine Lösung zu entwickeln, die die Aufenthaltsqualität an der Hochschule steigert.
Um mögliche Probleme an der Hochschule zu identifizieren, haben wir uns mit den Studierenden und Proffesoren unterhalten
und eine Umfrage durchgeführt. Dabei haben wir einige Probleme identifiziert, die wir zu unserer Personas zusammengefasst haben.

![Persona](media/Leonie_Empathy_Map.png)

### Problem
Mit hilfe der Persona Leonie haben wir volgende POV erstellt:


    Wie können wir Leonie dabei helfen ihre Gruppenarbeit an der Hochschule stattfinden zu lassen, um effektiver ihre Aufgaben in Gruppen zu bearbeiten.

Leonie kann einen Tisch reservieren, damit sie Planen kann, wo und wann die Gruppenarbeit stattfinden kann und damit sie zu Beginn der Gruppenarbeit nicht erst einen freien Tisch suchen muss.

### Lösung
Um Leonie zu helfen, haben wir eine Tisch-Reservierungs-Tool entschieden. Damit kann Leonie einen Tisch reservieren und die Gruppenarbeit planen.  
Dazu haben wir einige Prototypen erstellt und mit Leonie getestet. Dabei haben wir die Prototypen immer weiter verbessert, bis wir eine Lösung gefunden haben, die Leonie gefällt.

![Tisch-Reservierungs-Tool](media/20231026_110512.jpg)

## Bauanleitung

### Material
- Raspberry Pi 3 Model B
- 4:3 Monitor
- 2x RFID Reader
- 2x Druckschalter
- Drehschalter
- Sperrholzplatten 3.5mm
- Holzbretter 10mm (Resteverwertung)
- MakerBeams
- Heißkleber
- Holzöl
- Acrylglasscheibe
- Neopixel LED Ring
- 1,3 " HD-IPS-TFT-LCD DISPLAY 
- 3D Druck Filament
- 2x ESP32
- 9V Batterie
- 5V Netzteil
- Kippschalter
- 2x 10k Ohm Widerstand
- Kabel
- WD40
- Lötzinn
- Unterlegscheiben
- Moosgummi
- Schraubfüße
- 5V Spannungswandler
- HDMI auf VGA Adapter
- Mehrfachsteckdose

### Werkzeug
- 3D Drucker
- Lasercutter
- Lötkolben
- Schraubenzieher
- Bohrmaschine
- Säge
- Schleifpapier
- Schraubzwingen
- Schrauben
- Gewindeschneider
- Zange
- Multitool

### Software
- Arduino IDE für beide ESP's mit Arduino interner Programmiersprache (C).
- Inkspace (Laser Cutter)
- Fusion 360 & Cura (3D-Drucker)
- Mosquitto
- Python3 auf dem Raspberry Pi

### Empfohlene Vorkenntnisse
- Erfahrung in den Programmiersprachen C, Python und JavaScript.
- Erfahrung mit Lötkolben
- Erfahrung mit Lasercutter
- Erfahrung mit 3D-Druckern
- Erfahrung mit verteilten Systemen (Speziell Broker und Socketverbindungen)

### Schritt 1: Schaltung bauen
#### Schaltung für das Wanddisplay mit RFID Reader, Druckschalter und Drehschalter
Wir haben den RFID Reader wie folgt eingebaut:
![Schaltplan RFID](media/schaltplan_drehknopf.png)

Der Drehknopf wurde wie folgt eingebaut: [Bildquelle](https://tutorials-raspberrypi.de/raspberry-pi-ky040-drehregler-lautstaerkeregler/)
![Schaltplan Drehknopf](media/Raspberry-Pi-ky040_Steckplatine.webp)

Die Buttons wurden mit einem Pulldown-Widerstand an noch freie GPIO-Pins des Raspberry Pi angeschlossen.
Am Ende sah die Schaltung wie folgt aus:

![Finale Schaltung](media/IMG_20231127_174057268.jpg)
Zum Testen der Buttons wurden hier noch zusätzliche LEDs angeschlossen. Diese sind in der finalen Version jedoch nicht mehr eingebaut.

#### Schaltung für das Tischgerät mit RFID Reader, TFT Panel und Neopixel LED Ring
Der ESP32 wurde mit dem 1,3 " HD-IPS-TFT-LCD Display verbunden: [Bildquelle](https://joy-it.net/files/files/Produkte/SBC-LCD01/SBC-LCD01-Anleitung-29.09.2020.pdf)
![Schaltplan ESP32](media/schaltung_esp.png)

Der Neopixel LED Ring wurde wie folgt an den zweiten ESP32 eingebaut: [Bildquelle](https://blog.berrybase.de/neopixel-ring-mit-arduino-ansteuern-so-wirds-gemacht/)
![Schaltplan Neopixel](media/esp_led_ring.png)

Der RFID Reader wurde auch an den zweiten ESP32 angeschlossen: [Bildquelle](https://www.electronicwings.com/esp32/rfid-rc522-interfacing-with-esp32)
![Schaltplan RFID](media/rfid_schaltplan.webp)

### Schritt 2: Gehäuse bauen
#### Gehäuse für das Wanddisplay mit RFID Reader, Druckschalter und Drehschalter
1. Display aus Monitor ausbauen
2. Display, Druckschalter und Drehschalter vermessen und Frontplatte in Inkscape zeichnen
3. Frontplatte mit dem Lasercutter aus Sperrholz schneiden
4. Display und Drehschalter in die Frontplatte einbauen
5. Aufsatz für den Drehschalter in Autodesk Fusion 360 zeichnen
6. Aufsatz für den Drehschalter mit dem 3D Drucker drucken
7. Aufsatz für den Drehschalter mit dem Drehschalter verkleben
![Frontplatte](media/IMG_20231129_162638781.jpg)
8. Standfuß für das Display aus zwei Holzbrettern zusägen und mit einer Holzleiste im 90° Winkel verschrauben
9. Unterseite des Standfußes mit Moosgummi bekleben, um rutschen zu verhindern
10. Hintere Abdeckung des Displays abschrauben und montagelöcher auf den Standfuß übertragen
11. Montagelöcher in den Standfuß bohren und mit dem Display verschrauben
12. 3 mm breite Nut mit 2 mm Abstand zum Rand in alle vier Seitenkanten auf Vorder- und Rückseite der Frontplatte fräsen, damit die Frontplatte in die Zwischenräume der MakerBeams passt
13. MakerBeams auf die richtige Länge für das Gehäuse zusägen
14. Abgesägten Enden der MakerBeams mit WD40 einsprühen und mit einem Gewindeschneider ein Gewinde schneiden
15. Frontplatte mit den MakerBeams verschrauben
16. Seitenwände und Rückwand aus Sperrholz zusägen, dabei gravieren wir gleich eine Nut für die MakerBeams auf alle Seitenkanten ein.
Hierbei ist zu beachten, dass der Lasercutter in x-Richtung schneller gravieren kann als in y-Richtung. Daher drehen wir die zurechtgeschnittenen Platten um 90°, um die Nut in y-Richtung zu gravieren.
17. RFID Reader Logo auf Seitenwand gravieren
18. MakerBeams Rahmen mit dem Standfuß verschrauben
19. RFID Reader an die Seitenwand mit dem Logo kleben
![RFID-Reader](media/20240108_170227.jpg)
20. Seitenwände und Rückwand zwischen die MakerBeams einsetzen und mit den Schrauben der MakerBeams verschrauben
21. Raspberry Pi mit Schraubfüßen auf die Rückseite der Frontplatte kleben
22. Knöpfe und Widerstände an den Raspberry Pi anschließen und mit Lötzinn verlöten
23. Monitor Steuerplatine an die Seite des Standfußes kleben
24. HDMI auf VGA Adapter an Monitor anschließen
25. Monitor mit dem Raspberry Pi verbinden
26. Mehrfachsteckdose auf die Oberseite des Standfußes kleben
27. Raspberry Pi und Monitor an die Mehrfachsteckdose anschließen
28. Rückwand mit dem Standfuß verschrauben
29. Gehäuse mit Holzöl einölen
![Fertiges Grät](media/trt_display.jpg)

#### Gehäuse für das Tischgerät mit RFID Reader, TFT Panel und Neopixel LED Ring
1. LED Ring, TFT Panel und RFID Reader vermessen
2. Gehäuse in Autodesk Fusion 360 zeichnen, hierbei Nut zum Verschließen des Gehäuses nicht vergessen und genügend Platz für Kabel, ESP32 und Batterie lassen
![3D Modell](media/img.png)
3. Testdruck des oberen Teils des Gehäuses mit dem 3D Drucker machen, damit der LED Ring, zwei Plexiglasringe und das TFT Panel in das Gehäuse passen
![Gehäuse-Test](media/IMG_20231220_113028362.jpg)
5. Gehäuse mit dem 3D Drucker drucken
5. Stützmaterial entfernen und vergessenes Loch für Batterieschalter nachbohren
![Gehäuse](media/WhatsApp Bild 2024-01-17 um 18.04.37_9747e687.jpg)
6. Plexiglasringe mit dem Lasercutter ausschneiden
7. TFT Panel, LED Ring, RFID Reader und Plexiglasringe in das Gehäuse einbauen und mit Heißkleber fixieren
![Gehäuse](media/WhatsApp Bild 2024-01-17 um 18.05.11_c0da240e.jpg)
8. ESP32 mit dem TFT Panel verbinden
9. ESP32 mit dem RFID Reader und dem LED Ring verbinden
10. ESPs mit Heißkleber im Gehäuse befestigen
![Gehäuse](media/IMG_20240108_161101907.jpg)
11. 9V Batterie mit dem Batterieschalter verbinden und mit Spannungswandler auf 5V herunterregeln
12. 5V Spannungswandler mit dem ESPs verbinden
13. Batterieschalter durch das Loch im Gehäuse führen und mit dem Gehäuse verschrauben
![Batterieschalter](media/20240115_140532.jpg)
14. Deckel für das Gehäuse in Inkscape zeichnen, hierbei Aussparung zum Öffnen des Gehäuses nicht vergessen
15. Deckel mit dem Lasercutter aus dunklem Acrylglas schneiden
16. Deckel in das Gehäuse einsetzen
17. RFID Reader Logo mit Schneidplotter ausschneiden und auf das Gehäuse kleben
![Fertiges Grät](media/20240115_140523.jpg)

### Code
#### Frontend - Display
Die Benutzeroberflächen im Frontend werden alle mit HTML, CSS und JavaScript realisiert. Die Verbindung zum Backend geschieht über Socket.IO Socket-Verbindungen.
![Startseite](media/Startseite.png)
Der Nutzer kann hier zu den einzelnen Tischen im Denkraum navigieren und damit aktuelle Reservierungen einsehen.
![Reservierungsansicht](media/Reservierungsansicht.png)
Durch diese Webansicht navigiert der Nutzer, um seine Reservierung zu konfigurieren.
![Reservierungsverifizierung](media/Reservierungsverifizierung.png)
Diese Webansicht zeigt die vom Nutzer ausgewählte Reservierungskonfiguration an. Der Nutzer kann nun seine Reservierung abschließen.

#### Backend
Das Backend wird auf dem Raspberry Pi ausgeführt. Es wurde vollständig in Python geschrieben und verwendet das Webframework Flask mit Socket.IO. Zur Speicherung und Verwaltung von Reservierungen wird eine SQLite Datenbank verwendet. Weiterhin wird die MQTT Library paho-mqtt benötigt, damit das Tischgerät mit dem Backend kommunizieren kann.

Folgende Libraries werden mit den aufgelisteten Versionen als Requirements benötigt:

```
Flask>=2.2.2
Flask-SocketIO==5.3.6
RPi.GPIO==0.7.0
paho-mqtt~=1.6.1
```

#### Das Tischgerät
Das Tischgerät besteht aus zwei ESP8266 Boards. Diese haben einen Chip um sich mit dem Wlan zu verbinden und darüber die Information auszutauschen. Der Code ist in der Arduino IDE mit C++ geschrieben worden und wird auch darüber auf die beiden ESP8266 hochgeladen. 



## Programmierung und Hochladen des Quellcodes auf den ESP8266 (RFID + Ring)-Modul

### Funktionsweise des RFID-Moduls(ESP8266 mit angeschlossenem RFID-Leser und LED-Ring)
Der bereitgestellte Quellcode ist für ein Tischgerät entworfen, das RFID-Karten liest. Abhängig von der Karteninformation und der Backend-Reservierung werden verschiedene Aktionen ausgeführt. Zusätzlich sendet das Gerät Statusinformationen an ein ESP-basiertes Display. Bevor der Code auf den ESP8266 hochgeladen wird, ist es wichtig, ihn entsprechend den spezifischen Anforderungen des Projekts anzupassen.

### Funktionsweise des Displaymoduls(ESP8266 mit angeschlossenem Display)
- Das Displaymodul empfängt über MQTT Nachrichten mit Statusupdates und der aktuellen Uhrzeit.
- Abhängig von den empfangenen Nachrichten zeigt das Display verschiedene Inhalte an.
- Die Anzeige wird dynamisch aktualisiert, basierend auf den neuesten empfangenen Daten.

### Schritte zum Hochladen des Codes auf den ESP8266(mit angeschlossenem RFID-Leser und LED-Ring)

1. **Installieren der Arduino IDE**:
   - Die Arduino IDE ist erforderlich, um den Code auf den ESP8266 hochzuladen. Sie kann von der [offiziellen Arduino-Website](https://www.arduino.cc/en/Main/Software) heruntergeladen werden.

2. **Einrichten des ESP8266 in der Arduino IDE**:
   - Wähle in der Arduino IDE unter `Tools > Board` den ESP8266 als Zielplattform aus.
   - Wähle unter `Tools > Port` den entsprechenden COM-Port aus, an den der ESP8266 angeschlossen ist.

3. **Öffnen des Quellcodes**:
   - Öffne die Datei mit der Endung `.ino` des Projekts über `File > Open...`.

4. **Installieren erforderlicher Bibliotheken**:
   - Folgende Bibliotheken müssen über den Bibliotheksmanager (`Tools > Manage Libraries...`) installiert werden:
     - `PubSubClient` für MQTT-Kommunikation.
     - `ESP8266WiFi` für WLAN-Funktionen.
     - `Adafruit_NeoPixel` zur Steuerung von NeoPixel LEDs(hier den 24 LED Ring).
     - `ArduinoJson` für JSON-Verarbeitung.
     - `MFRC522` zur RFID-Kartenlesefunktion.
     - `SPI.h` für die SPI-Kommunikation.
     - `Adafruit_GFX` als Basisgrafikbibliothek für Displays.
     - `Adafruit_ST7789` zur Ansteuerung des ST7789-basierten Displays.

5. **Anpassen des Quellcodes**:
   - Überprüfe und ändere den Quellcode nach Bedarf.
   - Die Netzwerkeinstellungen (SSID, Passwort) sind zu den tatsächlichen zu ändern.
   - MQTT-Servereinstellungen (IP, Username + Passwort) sollten bearbeitet werden.

6. **Hochladen des Quellcodes**:
   - Klicke auf den Upload-Button in der Arduino IDE, um den Code auf den ESP8266 zu übertragen.

7. **Debugging**:
   - Nutze das serielle Monitorfenster in der Arduino IDE, um Debug-Informationen einzusehen und zu überprüfen, ob das Gerät ordnungsgemäß funktioniert.
   - Alle Ereignisse werden über diesen Monitor ausgegeben.
  



## Programmierung und Hochladen des Quellcodes auf das ESP8266 Displaymodul
Das ESP8266 Displaymodul ist Teil eines größeren Systems, das Informationen über MQTT kommuniziert. Es empfängt Statusaktualisierungen und Uhrzeitinformationen über MQTT und zeigt diese auf einem Display an. Der Code für das Displaymodul ist in der Arduino IDE mit C++ geschrieben und wird von dort auf das ESP8266 hochgeladen.

### Schritte zum Hochladen des Codes auf das ESP8266 Displaymodul

1. **Voraussetzungen überprüfen**:
   - Stelle sicher, dass die Arduino IDE bereits installiert ist, da sie benötigt wird, um den Code auf das ESP8266 Displaymodul zu übertragen.

2. **ESP8266 in der Arduino IDE einrichten**:
   - Falls notwendig, ändere in der Arduino IDE unter `Tools > Port` den COM-Port, um den aktuellen Anschluss des ESP8266 Displaymoduls zu reflektieren.

3. **Öffnen des Quellcodes**:
   - Öffne die Datei mit der Endung `.ino` des Displaymoduls über `File > Open...`.

4. **Installieren erforderlicher Bibliotheken**:
   - Die Bibliotheken `PubSubClient`, `ESP8266WiFi`, `Adafruit_GFX`, `Adafruit_ST7789`, `ArduinoJson` und `SPI.h` sollten bereits installiert sein, wie in vorherigen Schritten beschrieben.

5. **Anpassung des Quellcodes**:
   - Es sollte überprüft werden, ob der Quellcode Änderungen benötigt. 
   - Netzwerkeinstellungen: SSID und Passwort sind gegebenenfalls zu aktualisieren.
   - MQTT-Servereinstellungen: IP-Adresse, Benutzername und Passwort sind bei Bedarf anzupassen.

6. **Hochladen des Quellcodes**:
   - Klicke auf den Upload-Button in der Arduino IDE, um den Code auf das ESP8266 Displaymodul zu übertragen.

7. **Debugging**:
   - Verwende das serielle Monitorfenster in der Arduino IDE, um Debug-Informationen einzusehen und zu überprüfen, ob das Displaymodul ordnungsgemäß funktioniert.

### Hinweise
- Stelle sicher, dass der ESP8266 während des Hochladevorgangs korrekt mit dem PC verbunden ist.
- Möglicherweise musst du den Boot-Modus des ESP8266 aktivieren, indem du GPIO 0 mit Ground verbindest (nur bei einigen Boards üblich).




