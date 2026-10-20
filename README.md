# 🏓 Fibonacci Ping-Pong-Ball-Uhr

Eine Fibonacci-LED-Uhr mit **40 Ping-Pong-Bällen in einem 8×5-Raster** (⌀ 40 mm),
gesteuert durch einen **Raspberry Pi Zero WH**, mit zusätzlichem **TM1637 6-stelligem
LED-Display** (0,36″) als Klartext-Anzeige HH:MM:SS.

> Schwesternprojekt der 9-Bälle-Ping-Pong-Uhr: <https://github.com/Paul-3400/ping-pong-ball-clock>

## Funktionsprinzip

Die fünf Fibonacci-Felder (Werte 1, 1, 2, 3, 5) kacheln lückenlos das 8×5-Rechteck:

| Feld | Wert | Bälle |
|------|------|-------|
| A    | 5    | 25    |
| B    | 3    |  9    |
| C    | 2    |  4    |
| D    | 1    |  1    |
| E    | 1    |  1    |

- **rot** = Feld zählt zur Stunde
- **grün** = Feld zählt zu den Minuten (×5)
- **blau** = Feld zählt zu Stunde UND Minute
- **aus** = Feld zählt nicht

Anzeige bewusst 5-Minuten-genau (wie im Original von Philippe Chretien);
die Zerlegung wird pro Zeitstempel per Zufall aus allen gültigen
Fibonacci-Summen gewählt.

## Hardware (Kurzfassung)

| Komponente              | Funktion                          |
|------------------------|-----------------------------------|
| Raspberry Pi Zero WH   | Steuerung, NTP, Farb-/Zeitlogik   |
| 40× WS2812B NeoPixel   | 1 LED pro Ball (Schlangenlinie)   |
| TM1637 0,36″ 6-stellig | Klartext HH:MM:SS                 |
| 5V-Netzteil ≥3 A       | Pi + LEDs                         |
| Level-Shifter 74AHCT125| 3,3V→5V Datenpegel (empfohlen)    |

Geschätzte Gesamtkosten: ~95–100 CHF.

## Dokumentation

- 📄 **[Bauanleitung & Entwurf](docs/Fibonacci_PingPong_Uhr_Bauanleitung.md)** –
  Funktionsprinzip, Hardware-Liste, Verdrahtung, LED-Mapping, Code-Entwürfe
  (config, mapping, fibonacci, display, tm1637, ntp_time, main), systemd-Autostart,
  Fallstricke, Gehäuse-Konstruktion, Fahrplan und offene Fragen.

- 🧪 **[Wokwi-Prototyp](wokwi/)** – vollständige Simulation der Uhr mit dem
  **Seeed XIAO ESP32-S3** statt dem Raspberry Pi Zero WH (Wokwi kennt den Pi nicht):
  [sketch.ino](wokwi/sketch.ino), [diagram.json](wokwi/diagram.json)
  (40 NeoPixel im 8×5-Raster, sauber verlegte Daisy-Chain) und
  [libraries.txt](wokwi/libraries.txt). Details: [wokwi/README.md](wokwi/README.md)

- 🎛️ **[Demo-Variante mit 5 Tastern](wokwidemo/)** – für Demonstrationszwecke:
  Taster 1 schaltet die Felder A–E durch, Taster 2–4 stellen im Handbetrieb
  +1 Minute / +5 Minuten / +1 Stunde, Taster 5 ruft den Normalbetrieb
  (NTP-Zeit) zurück. Details: [wokwidemo/README.md](wokwidemo/README.md)

## Status

Projekt in der Entwurfs-/Beschaffungsphase – siehe Fahrplan in der Bauanleitung.

✅ Der Wokwi-Prototyp (XIAO ESP32-S3) läuft: komplette Anzeige- und NTP-Logik
   ist simulierbar, die Code-Dateien aus der Bauanleitung werden daraus
   schrittweise als lauffähige Module für den Pi eingecheckt.

✅ Demo-Variante mit 5 Tastern (Feld-Durchschaltung, Handbetrieb, Normalbetrieb)
   für Demonstrationen der Fibonacci-Codierung.

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

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 18.10.2026
