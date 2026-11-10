# 🏓 Fibonacci Ping-Pong-Ball-Uhr

Eine Fibonacci-LED-Uhr mit **40 Ping-Pong-Bällen**, gesteuert durch einen
**Raspberry Pi Zero WH**, mit zusätzlichem **TM1637 6-stelligem LED-Display**
(0,36″) als Klartext-Anzeige HH:MM:SS. Das Raster steht **hochkant als sich
öffnende Fibonacci-Schnecke (5 Spalten × 8 Zeilen)** – Layout der realen Anzeigetafel.

> Schwesternprojekt der 9-Bälle-Ping-Pong-Uhr: <https://github.com/Paul-3400/ping-pong-ball-clock>

## Funktionsprinzip

Die fünf Fibonacci-Felder (Werte 1, 1, 2, 3, 5) kacheln lückenlos 40 Bälle
in die öffnende Fibonacci-Schnecke (5×8 hochkant): Feld A (5×5) oben über die
volle Breite, B (3×3) unten rechts, C (2×2) unten links, D (A5) und E (B5)
nebeneinander links in Zeile 5 – die Quadrate wachsen vom Zentrum nach aussen
wie eine Spirale. Positionsangaben wie «C5» = Spalte C, Zeile 5 (Beschriftung
der realen Tafel; Spaltenbuchstaben ≠ Fibonacci-Felder).

| Feld | Wert | Bälle | Lage (5 Spalten × 8 Zeilen) |
|------|------|-------|------------------------------|
| A    | 5    | 25    | Spalten A–E, Zeilen 0–4 (oben) |
| B    | 3    |  9    | Spalten C–E, Zeilen 5–7 (unten rechts) |
| C    | 2    |  4    | Spalten A–B, Zeilen 6–7 (unten links) |
| D    | 1    |  1    | Spalte A, Zeile 5 (A5) |
| E    | 1    |  1    | Spalte B, Zeile 5 (B5) |

- **rot** = Feld zählt zur Stunde
- **grün** = Feld zählt zu den Minuten (×5)
- **blau** = Feld zählt zu Stunde UND Minute
- **aus** = Feld zählt nicht

Zusätzlich ist der **Base4-Modus** der 9-Bälle-Ping-Pong-Uhr wählbar:
9 Bälle als 3×3-Matrix (Zeilen 0–2, Spalten B–D) zeigen die Zeit **minutengenau**
in rot/grün/**gelb** – wählbar über Taster T2 (Anzeige-Modus 2); Details in der
Bauanleitung, Kapitel 1.6. Mit der Erweiterung «Anzeige-Modi» (10.11.2026) wählen
T1–T5 die Anzeige-Modi 1–5, T6 wirkt als Shift für die Platz 6–10 –
siehe [docs/Erweiterungen_Anzeigemodi.md](docs/Erweiterungen_Anzeigemodi.md).

Anzeige bewusst 5-Minuten-genau (wie im Original von Philippe Chretien);
die Zerlegung wird pro Zeitstempel per Zufall aus allen gültigen
Fibonacci-Summen gewählt. Mapping: `LED-Index = Spalte*8 + Zeile` – die
Datenkette läuft spaltenweise (IN an A0), genau wie die reale Tafel verkabelt
ist (Daten- und Stromkette: A0–A7 → B0–B7 → … → E0–E7).

## Hardware (Kurzfassung)

| Komponente              | Funktion                          |
|------------------------|-----------------------------------|
| Raspberry Pi Zero WH   | Steuerung, NTP, Farb-/Zeitlogik   |
| 40× WS2812B NeoPixel   | 1 LED pro Ball (spaltenweise Kette im 5×8-Raster) |
| TM1637 0,36″ 6-stellig | Klartext HH:MM:SS                 |
| 6× Taster (GPIO 5/6/12/13/16 + 26) | Anzeige-Modi 1–5 (T1–T5), Shift (T6), Langdruck-Zeitverstellung |
| Shift-Taster T6 (GPIO 26) | Shift für Anzeige-Modi 6–10 (Toggle, Timeout 10 s) |
| 5V-Netzteil ≥3 A       | gemeinsame Versorgung beider Gehäuse |
| Level-Shifter 74AHCT125| 3,3V→5V Datenpegel (in der Anzeigebox) |
| GX12-Kupplungspaar 4-polig | Verbindungskabel Steuerbox ↔ Anzeigebox |
| Lochplatte 200×320 mm  | Ball-Halterung, hochkant (5×8 Bälle à 40 mm) |

Aufbau in zwei Gehäusen (Steuerbox: Pi, 6 Taster, TM1637;
Anzeigebox: Tafel, NeoPixel, Level-Shifter, 5V-DC-Buchse 5,5×2,1) – verbunden
über das 4-adrige Kabel mit GX12-Kupplungspaar.

Geschätzte Gesamtkosten: ~115 CHF.

## Die sechs Taster

| Taster | GPIO (Pi) | Funktion (Erweiterung Anzeige-Modi, 10.11.2026) |
|---|---|---|
| T1 | 5  | Anzeige-Modus 1 (Fibonacci) wählen |
| T2 | 6  | Modus 2 (Base4) wählen; **lang**: +1 Minute |
| T3 | 12 | Modus 3 (Binärzähler h/m/s) wählen; **lang**: +5 Minuten |
| T4 | 13 | Modus 4 (grosse Ziffern) wählen; **lang**: +1 Stunde |
| T5 | 16 | Modus 5 (reserviert); **lang**: Normalbetrieb (Offset auf 0) |
| T6 | 26 | **Shift** für die Modi 6–10 (Toggle; nach 10 s automatisch aus) |

Kurzer Druck = Moduswahl (TM1637 zeigt kurz «M n»; reservierte Plätze «- n»),
langer Druck (≥ 1 s) = Zeitverstellung (wiederholend bei gehaltener Taste).
Nach dem Boot: Modus 1 (Fibonacci), Shift aus, Offset 0.

## Software

Die Module liegen einsatzbereit im Repo (aus der Bauanleitung, Kap. 7):
`config.py`, `mapping.py`, `buttons.py`, `fibonacci.py`, `base4.py`, `modes.py` (Registry der Anzeige-Modi),
`font5x7.py` (5×7-Ziffernfont für Modus 4), `display.py`, `tm1637_display.py`, `ntp_time.py`, `main.py`. Zum Allein-Test
der Steuerbox (Uhrzeit + Tasten, ohne Anzeigebox): `steuerbox_test.py`.
Zum Test der Anzeige-Tafel (T6 = Anzeige ein/aus, T1–T5 = Felder einzeln): `anzeige_test.py`.
Setup auf dem Pi
(Raspberry Pi OS Lite 32-bit, Trixie):

```bash
sudo apt update && sudo apt install -y git   # Raspberry Pi OS Lite enthält kein git
git clone https://github.com/Paul-3400/fibonacci-ping-pong-clock.git ~/fibonacci-clock
cd ~/fibonacci-clock
python3 -m venv --system-site-packages venv   # Trixie: PEP 668 -> venv nötig
source venv/bin/activate
pip install rpi_ws281x raspberrypi-tm1637 ntplib
sudo venv/bin/python3 main.py
```

## Dokumentation

- 📄 **[Bauanleitung & Entwurf](docs/Fibonacci_PingPong_Uhr_Bauanleitung.md)** –
  5×8-Schnecken-Layout mit 6 Tastern: Funktionsprinzip, Hardware-Liste,
  Verdrahtung, LED-Mapping, Code-Entwürfe (config, mapping, buttons, fibonacci,
  display, tm1637, ntp_time, main), systemd-Autostart, Fallstricke,
  Gehäuse-Konstruktion (200×320 mm hochkant), Fahrplan und offene Fragen.

- ⌨️ **[Betriebsbefehle](docs/Betriebsbefehle.md)** – Kurzreferenz für den
  Betrieb auf dem Pi: systemd-Steuerung, Logs (journalctl), manuelle Tests,
  NTP-Kontrolle, Software-Update, System-Überwachung, Notfall-Anker.

- 🧭 **[Erweiterungen: Anzeige-Modi](docs/Erweiterungen_Anzeigemodi.md)** – Planung + Umsetzung Stufe 1 (10.11.2026): zehn Zeitdarstellungen auf dem 5×8-Raster, gewählt mit T1–T5 direkt und T6 als Shift + T1–T5. Behandelt: Shift-Varianten (entschieden: Toggle mit 10-s-Timeout), Taster-Konflikt (entschieden: Langdruck), Modus-Beschreibungen mit Beispielen, Software-Skizze, Umsetzungs-Stand, offene Fragen und Fahrplan.

- 🧪 **[Wokwi-Prototyp](wokwi/)** – vollständige Simulation der Uhr mit dem
  **Seeed XIAO ESP32-S3** statt dem Raspberry Pi Zero WH (Wokwi kennt den Pi nicht):
  40 NeoPixel im 5×8-Schnecken-Raster hochkant, NTP-Zeitsync, TM1637, Self-Test –
  ohne Taster. Details: [wokwi/README.md](wokwi/README.md)

- 🎛️ **[Demo-Variante mit 5 Tastern](wokwidemo/)** – dieselbe Uhr mit den fünf
  Tastern des echten Aufbaus: Feld-Durchschaltung A–E, Handbetrieb
  (+1 Minute / +5 Minuten / +1 Stunde als Offset zur NTP-Zeit), Normalbetrieb.
  Die Demo zeigt noch den Planungsstand vom 21.10.2026 (Felder B/C ungespiegelt,
  Kette zeilenweise) und wird nicht weiter angepasst – die reale Tafel ist
  gespiegelt und spaltenweise verkettet (siehe Bauanleitung).
  Details: [wokwidemo/README.md](wokwidemo/README.md)

> *Ordner-Umbenennung 20.10.2026:* Bis dahin hiess die Schnecken-Demo
> `wokwidemo2` und die ältere 8×5-Demo `wokwidemo`. Nach der Entscheidung für
> das Schnecken-Layout wurde die 8×5-Demo gelöscht und die Schnecken-Demo in
> `wokwidemo` umbenannt.

## Status

Aufbau fertig, Uhr im Regelbetrieb mit systemd-Autostart – siehe Fahrplan in der Bauanleitung.

✅ Layout-Entscheidung gefallen: 5×8-Schnecke hochkant (bessere Lesbarkeit,
   Anordnung wie bei der [Nerdiy-Fibonacci-Uhr](https://www.nerdiy.de/fibonacciClock)).

✅ Wokwi-Prototyp (XIAO ESP32-S3) läuft: Anzeige- und NTP-Logik simulierbar,
   die Python-Module aus der Bauanleitung werden daraus portiert.

✅ Demo-Variante mit 5 Tastern im Schnecken-Layout (Feld-Durchschaltung,
   Handbetrieb, Normalbetrieb) – zeigt den Planungsstand vom 21.10.2026.

✅ Reale Anzeigetafel vermessen, Unterlagen angepasst (07.11.2026): B (3×3)
   unten rechts (Spalten C–E), C (2×2) unten links (Spalten A–B), D = A5,
   E = B5; Daten- und Stromkette spaltenweise → `LED = Spalte×8+Zeile`.
   Die Wokwi-Demos bleiben beim früheren Planungsstand (keine weitere
   Simulation) – massgeblich ist die Bauanleitung.

✅ Modus-Umschalter auf Taster umgestellt (07.11.2026): T6 (GPIO 26) statt
   Kippschalter – nur Momentary-Taster an Lager; gleiche Verdrahtung (Öffner
   gegen GND), Software-Toggle pro Druck, Start nach Boot = Fibonacci.

✅ Code-Module ins Repo eingecheckt und verifiziert (08.11.2026): Syntax- und
   Logiktest bestanden (288 Fibonacci- + 1440 Base4-Zerlegungen, 40 LEDs
   lückenlos) – Setup jetzt per git clone (siehe Software).

✅ Steuerbox-Selbsttest auf dem Pi bestanden (08.11.2026): TM1637 zeigte
   HH:MM:SS, alle 6 Tasten T1–T6 geprüft – Steuerbox funktionsfähig
   (Anzeigebox noch im Bau).

✅ Pi-Setup komplett (08.11.2026): git installiert, Clone + venv + alle
   Pakete (rpi_ws281x, raspberrypi-tm1637, ntplib aus piwheels) – bereit für
   den Regelbetrieb, sobald die Anzeigebox fertig ist.

✅ Anzeige-Test bestanden (08.11.2026): alle 5 Felder korrekt
   (Farben/Positionen/Wertigkeiten), T1–T6 geprüft – Uhr startklar.

⚠️ Achtung (09.11.2026): Absturz beim Start um 10:04 – Pi und Tafel hingen
   am selben Netzteil; bei Minuten 0–4 gehen sofort alle 40 LEDs an
   (Volllast-Schlag). Soft-Start-Rampe ergänzt (Fallstrick 29);
   Stromversorgung gem. Kap. 5 auf getrennte Netzteile umbauen –
   ✅ erledigt 09.11.2026: Pi am 5V/3A-Netzteil (Micro-USB), Tafel am
   5V/4A-Netzteil, GND beider Netzteile verbunden.

🔧 NTP-Bug behoben (09.11.2026, Fallstrick 30): sync_ntp() verwendete die
   NTP-Antwort nicht – die Uhr lief still auf der (nach SD-Neuflash oft
   falschen) Systemzeit. get_local_time() rechnet jetzt aus der
   NTP-Referenz (Europe/Zurich inkl. Sommerzeit).

✅ systemd-Autostart in Betrieb (10.11.2026): fibonacci-clock.service
   (Bauanleitung Kap. 7.10), Reboot-Test bestanden – die Uhr startet nach
   dem Einschalten autonom.

✅ TM1637-Anzeige-Bug behoben (10.11.2026, Fallstrick 31 endgültig): Das
   6-stellige Modul spiegelt die Segmentliste je Hälfte – Roh-Befehl
   '123456' zeigte «321654». Fix: _modul_segments() kehrt jede 3-Zeichen-
   Hälfte vor write() um (tm1637_display.py + steuerbox_test.py).
   Fibonacci-Anzeige verifiziert korrekt (14:05 → Feld C rot + E grün).

✅ Erweiterung Anzeige-Modi (10.11.2026): 10 Darstellungen auf dem 5×8-Raster über T1–T5 (direkt) und T6 als Shift + T1–T5. Entscheidungen: Shift = Toggle mit 10-s-Timeout, Zeitverstellung per Langdruck (T2–T5). Stufe 1 am Gerät bestätigt (Tasten inkl. Shift); Stufe 2 umgesetzt: Modus 3 (Binärzähler h/m/s, T3) und Modus 4 (grosse Ziffern, T4) mit font5x7.py; Platz 5–10 folgen in Stufe 3–4. Details: [docs/Erweiterungen_Anzeigemodi.md](docs/Erweiterungen_Anzeigemodi.md).

## Lizenz

GNU GPL (Version 2 oder später) – abgeleitet von der Arduino-Fibonacci-Uhr
[Philippe Chretien](https://github.com/pchretien/fibo). Siehe [LICENSE](LICENSE).

## Quellen

- Original Fibonacci Clock Firmware: <https://github.com/pchretien/fibo>
- Nerdiy Fibonacci Clock: <https://www.nerdiy.de/fibonacciClock>
- rpi_ws281x: <https://github.com/jgarff/rpi_ws281x>
- raspberrypi-tm1637: <https://github.com/depklyon/raspberrypi-tm1637>
- Raspberry Pi Pinout: <https://pinout.xyz/>

---

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026