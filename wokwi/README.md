# 🧪 Wokwi-Prototyp – Fibonacci Ping-Pong-Ball-Uhr

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 18.10.2026

Vollständige Simulation der Fibonacci-Uhr im Browser, mit dem **Seeed XIAO ESP32-S3**
statt dem Raspberry Pi Zero WH – Wokwi kennt den Pi Zero nicht. Die komplette Logik
(Fibonacci-Zerlegung mit Zufallsauswahl, NTP-Zeitsync, TM1637-Klartext) ist im
Prototyp lauffähig und wird später auf den Pi portiert.

## Dateien

| Datei | Inhalt |
|---|---|
| `sketch.ino` | Firmware: 40 NeoPixel (8×5-Raster), Fibonacci-Zerlegung (setBits-Portierung), TM1637, WLAN+NTP, Self-Test |
| `diagram.json` | Aufbau: XIAO ESP32-S3, 40 NeoPixel als 8×5-Raster mit durchgängiger Daisy-Chain, TM1637, Legende |
| `libraries.txt` | `Adafruit NeoPixel`, `TM1637` (Avishay Orpaz) |

## Pin-Mapping: Pi Zero WH (Bauanleitung) ↔ XIAO ESP32-S3 (Prototyp)

| Funktion | Pi Zero WH | XIAO ESP32-S3 |
|---|---|---|
| NeoPixel-Daten | GPIO 18 (PWM0) | **D3 = GPIO4** |
| TM1637 CLK | GPIO 23 | **D4 = GPIO5** |
| TM1637 DIO | GPIO 24 | **D5 = GPIO6** |
| Level-Shifter 74AHCT125 | nötig (3,3 V → 5 V) | entfällt (Prototyp) |

Hinweis: GPIO18 existiert am XIAO nicht; D2/GPIO3 ist Strapping-Pin und wurde vermieden.

## Unterschiede zum Ziel-Aufbau

- **TM1637 nur 4-stellig** im Sim (Wokwi hat kein 6-stelliges Modul) → zeigt **HH:MM**
  statt HH:MM:SS. Ziel-Hardware bleibt das 6-stellige Modul.
- **NTP funktioniert in der Simulation mit echter Zeit** (`Wokwi-GUEST` + `pool.ntp.org`,
  Zeitzone Europe/Zurich inkl. Sommerzeit).
- Helligkeit auf ~35 % gedimmt; am echten Aufbau wären 40 LEDs in Vollelweiss ~2,4 A.

## So startest du die Simulation

1. Neues Projekt auf [wokwi.com](https://wokwi.com) anlegen, Board **XIAO ESP32-S3**.
2. Die drei Dateien aus diesem Ordner übernehmen (bei Copy-Paste-Gefahr: Datei auf
   GitHub öffnen und über den **Raw**-Button kopieren – abgeschnittene Sketches
   kompilieren erst beim Linken falsch).
3. Play drücken. Beim Start leuchten die Felder A–E nacheinander:
   **A rot → B grün → C blau → D gelb → E magenta** (Self-Test für Mapping und Kette).
4. Danach: WLAN+NTP verbinden, TM1637 zeigt HH:MM (Doppelpunkt blinkt), das Raster
   zeigt die Fibonacci-Zerlegung.

## Verdrahtung im Diagramm

- **Daisy-Chain:** LED0 → LED1 → … → LED39, Reihenfolge = Mapping `LED-Index = Zeile*8 + Spalte`.
- **Farbschema** (auch im Diagramm als Legende): Daten **grün**, 5 V **rot**, GND **schwarz**,
  TM1637 CLK **orange**, DIO **blau**.
- Strom als Daisy-Chain von Part zu Part (keine Einzeladern vom Board);
  Zeilenwechsel-Leitungen laufen mit festem Versatz im Kanal zwischen den Zeilen.

## Offene Punkte für den Prototyp

- [ ] Simulation starten und Self-Test prüfen (leuchten alle 40 LEDs, Felder korrekt?)
- [ ] Anzeige mit bekannter Zeit gegenrechnen (z. B. 08:10 → A+B rot, C grün)
- [ ] Zufallszerlegung beobachten: wechselt das Bild bei 5-Minuten-Schritten?
- [ ] Danach Portierung der Module auf den Pi (Python, siehe Bauanleitung Kap. 7)
