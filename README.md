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

Über einen **Kippschalter** (GPIO 26) ist zusätzlich der **Base4-Modus** der
9-Bälle-Ping-Pong-Uhr zuschaltbar: 9 Bälle als 3×3-Matrix (Zeilen 0–2,
Spalten B–D) zeigen die Zeit **minutengenau** in rot/grün/**gelb** – Details
in der Bauanleitung, Kapitel 1.6.

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
| 5× Taster (GPIO 5/6/12/13/16) | Feld-Durchschaltung, Handbetrieb, Normalbetrieb |
| Kippschalter (GPIO 26) | Modus-Umschalter Fibonacci ↔ Base4 |
| 5V-Netzteil ≥3 A       | gemeinsame Versorgung beider Gehäuse |
| Level-Shifter 74AHCT125| 3,3V→5V Datenpegel (in der Anzeigebox) |
| GX12-Kupplungspaar 4-polig | Verbindungskabel Steuerbox ↔ Anzeigebox |
| Lochplatte 200×320 mm  | Ball-Halterung, hochkant (5×8 Bälle à 40 mm) |

Aufbau in zwei Gehäusen (Steuerbox: Pi, Taster, Kippschalter, TM1637;
Anzeigebox: Tafel, NeoPixel, Level-Shifter, 5V-DC-Buchse 5,5×2,1) – verbunden
über das 4-adrige Kabel mit GX12-Kupplungspaar.

Geschätzte Gesamtkosten: ~118 CHF.

## Die fünf Taster

| Taster | GPIO (Pi) | Funktion |
|---|---|---|
| T1 | 5  | Felder A–E durchschalten (weiss) |
| T2 | 6  | Handbetrieb: +1 Minute |
| T3 | 12 | Handbetrieb: +5 Minuten |
| T4 | 13 | Handbetrieb: +1 Stunde |
| T5 | 16 | Normalbetrieb (NTP-Zeit, Offset auf 0) |

## Dokumentation

- 📄 **[Bauanleitung & Entwurf](docs/Fibonacci_PingPong_Uhr_Bauanleitung.md)** –
  5×8-Schnecken-Layout mit 5 Tastern: Funktionsprinzip, Hardware-Liste,
  Verdrahtung, LED-Mapping, Code-Entwürfe (config, mapping, buttons, fibonacci,
  display, tm1637, ntp_time, main), systemd-Autostart, Fallstricke,
  Gehäuse-Konstruktion (200×320 mm hochkant), Fahrplan und offene Fragen.

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

Projekt in der Entwurfs-/Beschaffungsphase – siehe Fahrplan in der Bauanleitung.

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

## Lizenz

GNU GPL (Version 2 oder später) – abgeleitet von der Arduino-Fibonacci-Uhr
[Philippe Chretien](https://github.com/pchretien/fibo). Siehe [LICENSE](LICENSE).

## Quellen

- Original Fibonacci Clock Firmware: <https://github.com/pchretien/fibo>
- Nerdiy Fibonacci Clock: <https://www.nerdiy.de/fibonacciClock>
- rpi_ws281x: <https://github.com/jgarff/rpi_ws281x>
- raspberrypi-tm1637: <https://github.com/timofurrer/raspberrypi-tm1637>
- Raspberry Pi Pinout: <https://pinout.xyz/>

---

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 07.11.2026
