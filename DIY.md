# Team Äähh? - Bauanleitung Tisch-Reservierungs-Tool

## Challenge
    Wie können wir durch smarte Devices dabei helfen, dass die Aufenthaltsqualität an der Hochschule steigt?

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
![Frontplatte](media/IMG_20231129_162638781.jpg)
5. 
