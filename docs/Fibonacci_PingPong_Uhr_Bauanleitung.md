---
title: "Fibonacci Ping-Pong-Ball-Uhr – Bauanleitung & Entwurf"
date: 2026-09-14
author: "Paul Simmen (mit Vibe / GLM-5-2)"
project: "Fibonacci Clock – Ping-Pong-Ball Edition (8×5 Raster)"
hardware: "Raspberry Pi Zero WH + 40 NeoPixel + TM1637 6-stellig"
purpose: "Bauanleitung mit Hardware-Liste, Verdrahtung, LED-Mapping und Code-Entwürfen"
related: "Base4 Clock (Schwesterprojekt), Fibonacci-Uhr Arduino-Analyse"
license: "GNU GPL (abgeleitet von Philippe Chretien / Fabian Steppat)"
---

# 🏓 Fibonacci Ping-Pong-Ball-Uhr – Bauanleitung & Entwurf

> Bauanleitung von Paul Simmen, erstellt mit Vibe (GLM-5-2).
> Eine Fibonacci-LED-Uhr mit 40 Ping-Pong-Bällen in einem 8×5-Raster,
> gesteuert durch einen Raspberry Pi Zero WH, mit zusätzlichem
> 0,36″ TM1637 6-stelligem LED-Display als Klartext-Anzeige.

---

## 1. Funktionsprinzip (Konfidenz: hoch)

### 1.1 Fibonacci-Verlegung im 8×5-Raster

Die fünf Fibonacci-Felder (Werte 1, 1, 2, 3, 5) kacheln lückenlos in ein
8×5-Rechteck. Jedes Feld besteht aus mehreren gleich gefärbten Bällen:

| Feld | Wert | Bälle | Lage (Spalten × Zeilen)  |
|------|------|-------|--------------------------|
| A    | 5    | 25    | Spalten 0–4 × Zeilen 0–4 |
| B    | 3    |  9    | Spalten 5–7 × Zeilen 0–2 |
| C    | 2    |  4    | Spalten 5–6 × Zeilen 3–4 |
| D    | 1    |  1    | Spalte 7 × Zeile 3       |
| E    | 1    |  1    | Spalte 7 × Zeile 4       |
| **Total** | **12** | **40** | 8×5 = 40 Bälle      |

### 1.2 Farbcodierung

| Farbe  | Bedeutung                         |
|--------|-----------------------------------|
| rot    | Feld zählt zur Stunde             |
| grün   | Feld zählt zu den Minuten (×5)    |
| blau   | Feld zählt zu Stunde UND Minute   |
| aus    | Feld zählt nicht                  |

### 1.3 Ablesen

- **Stunde** = Summe(rote Felder) + Summe(blaue Felder)
- **Minute** = (Summe(grüne Felder) + Summe(blaue Felder)) × 5

Anzeige bewusst nur **5-Minuten-genau** (wie im Original).

### 1.4 Beispiel 08:10

| Wert | Stunde | Minute |
|------|--------|--------|
| 5    | ja     | –      |
| 3    | ja     | –      |
| 2    | –      | ja     |
| 1    | –      | –      |
| 1    | –      | –      |

→ Stunde = 5+3 = 8, Minute = 2×5 = 10 → **08:10**

Feld 5 (25 Bälle) und Feld 3 (9 Bälle) leuchten **rot**,
Feld 2 (4 Bälle) leuchtet **grün**, die beiden Einer bleiben **aus**.

### 1.5 Zufallszerlegung (setBits)

Für jede Zahl 1–12 gibt es mehrere gültige Fibonacci-Summen. Die Software
wählt per `random()` eine davon → die Uhr sieht bei jedem 5-Minuten-Wechsel
anders aus (keine Mehrdeutigkeit-Auflösung wie bei Base4 nötig; **Konfidenz: hoch**,
übernommen aus der Original-Arduino-Firmware von Philippe Chretien).

---

## 2. Systemübersicht

```mermaid
graph TD
    A[Raspberry Pi Zero WH] -->|GPIO 18 PWM| B[40× WS2812B NeoPixel]
    A -->|GPIO 23/24| C[TM1637 6-stellig Display]
    A -->|WLAN| D[NTP-Zeitquelle]
    D --> A
    B --> E[8×5 Ping-Pong-Ball-Raster]
    C --> F[Klartext HH:MM:SS]
```

| Komponente             | Funktion                              |
|-----------------------|---------------------------------------|
| Pi Zero WH            | Steuerung, NTP, Farb- und Zeitlogik    |
| 40× WS2812B NeoPixel  | Anzeige im 8×5-Ball-Raster             |
| TM1637 6-stellig      | Klartext-Uhrzeit HH:MM:SS              |
| 5V-Netzteil ≥3 A      | Strom Pi + 40 LEDs                     |
| Level-Shifter         | 3,3V→5V Datenpegel (empfohlen)         |

---

## 3. Hardware-Liste

| # | Teil                          | Zweck                          | Richtpreis CHF | Konf. |
|---|-------------------------------|--------------------------------|----------------|-------|
| 1 | Raspberry Pi Zero WH          | Steuerung + WLAN/NTP           | 25.–           | hoch  |
| 2 | MicroSD 8–16 GB               | OS (Bookworm Lite)             | 8.–            | hoch  |
| 3 | 40× WS2812B NeoPixel          | 1 LED pro Ball                 | 15.–           | hoch  |
| 4 | TM1637 0,36″ 6-stellig        | Klartext HH:MM:SS              | 5.–            | hoch  |
| 5 | 5V-Netzteil ≥3 A              | Pi + LEDs                      | 20.–           | hoch  |
| 6 | Level-Shifter 74AHCT125       | 3,3V→5V Datenpegel             | 3.–            | mittel|
| 7 | Widerstand 330–470 Ω          | Schutz am LED-Data-In          | <1.–           | hoch  |
| 8 | Elko 1000 µF / 6,3V           | Schutz/Stabilisierung          | 1.–            | hoch  |
| 9 | 40× Ping-Pong-Bälle           | Diffusor / Anzeige             | 15.–           | hoch  |
| 10| Lochplatte / Brett 8×5        | Ball-Halterung (320×200 mm)    | Bastelkiste    | hoch  |
| 11| Jumper-Wires                  | Verdrahtung TM1637             | 2.–            | hoch  |
| 12| Micro-USB-Kabel               | Strom-Pi (oder via HAT)        | 3.–            | hoch  |

**Geschätzte Gesamtkosten:** ~95–100 CHF

---

## 4. Verdrahtung

### 4.1 NeoPixel (40 LEDs)

```
Pi Zero WH               Level-Shifter            NeoPixel-Kette
─────────────            ──────────────           ──────────────
GPIO 18 (PWM0) ──[330Ω]──> 74AHCT125 IN ──>      DIN (LED 0)
                                                  DOUT → DIN(LED 1) → ... → LED 39
3,3V ──────────────────> 74AHCT125 VCC
5V  ──────────────────────────────────────>      VCC (alle LEDs, Einspeisung Anfang)
GND ───────────────────> 74AHCT125 GND ──>       GND (alle LEDs)
                                              + 1000 µF Elko über VCC/GND am Anfang
```

**Wichtig (Konfidenz: hoch):**
- GPIO 18 = PWM0, der klassische Pin für `rpi_ws281x` / Adafruit NeoPixel.
- Bei 40 LEDs ab einer Einspeisung: Spannungsabfall am Ende möglich.
  Falls das ferne Ende farblich „abdriftet" → zweite 5V-Einspeisung am Ende.
- Strom: 40 × 60 mA = 2,4 A (Volweiß) → 3A-Netzteil mit Reserve.

### 4.2 TM1637 6-stelliges Display

```
Pi Zero WH               TM1637 Modul
─────────────            ────────────
GPIO 23  ──────────────>  CLK
GPIO 24  ──────────────>  DIO
3,3V     ──────────────>  VCC
GND      ──────────────>  GND
```

**Hinweis (Konfidenz: mittel):**
- TM1637-Module sind meist 3,3V-tolerant auf den Datenpins, laufen aber
  offiziell oft mit 5V. Falls Anzeige flackert oder dunkel bleibt → VCC auf 5V
  legen, Datenpins über Level-Shifter oder direkt (meist OK bei kurzen Leitungen).
- Die 6-stellige Variante ist seltener als die 4-stellige; darauf achten,
  dass das Modul tatsächlich 6 Ziffern hat (Typ: „TM1637 6 digit 0.36″").

### 4.3 Gesamt-Pin-Übersicht

| Pin          | Funktion           | Ziel               |
|--------------|--------------------|--------------------|
| GPIO 18      | PWM0 / NeoPixel    | Level-Shifter → DIN|
| GPIO 23      | CLK                | TM1637             |
| GPIO 24      | DIO                | TM1637             |
| 5V (Pin 2/4) | Strom              | NeoPixel + TM1637  |
| GND          | Masse              | Alle               |

---

## 5. LED-Mapping (40 LEDs → 5 Felder)

### 5.1 Verdrahtungsreihenfolge

Empfehlung: LED-Kette in **Schlangenlinie** (Zeile für Zeile, links→rechts,
dann nächste Zeile) verlegen. Dann ist die Formel einfach:

```
LED-Index = Zeile × 8 + Spalte     (Zeile 0–4, Spalte 0–7)
```

### 5.2 Mapping-Tabelle

```python
# Feld-Definition: (Wert, [Liste der LED-Indizes])
# Annahme: Schlangenlinie, Zeile 0 oben links, LED 0 = (0,0)

def led_index(row, col):
    """Schlangenlinie: Zeile für Zeile, links nach rechts."""
    return row * 8 + col

FELDER = {
    5: [led_index(r, c) for r in range(5) for c in range(5)],   # 25 LEDs
    3: [led_index(r, c) for r in range(3) for c in range(5,8)], #  9 LEDs
    2: [led_index(r, c) for r in range(3,5) for c in range(5,7)],#  4 LEDs
    1: [led_index(3, 7)],                                       #  1 LED (Feld D)
    1: [led_index(4, 7)],                                       #  1 LED (Feld E)
}
# ACHTUNG: Python-Dictionary kann keine doppelten Keys!
# Besser als Liste von Tupeln:
```

```python
# Korrekt: Liste von (Wert, [LED-Indizes])
FELDER = [
    (5, [r * 8 + c for r in range(5) for c in range(5)]),         # Feld A: 25 LEDs
    (3, [r * 8 + c for r in range(3) for c in range(5, 8)]),     # Feld B:  9 LEDs
    (2, [r * 8 + c for r in range(3, 5) for c in range(5, 7)]),   # Feld C:  4 LEDs
    (1, [3 * 8 + 7]),                                             # Feld D:  1 LED
    (1, [4 * 8 + 7]),                                             # Feld E:  1 LED
]
NUM_LEDS = 40
```

### 5.3 Verifikation

```python
assert sum(len(feld[1]) for feld in FELDER) == 40  # alle LEDs erfasst
assert sum(feld[0] for feld in FELDER) == 12       # 5+3+2+1+1 = 12
```

---

## 6. Software-Architektur

```mermaid
graph TD
    A[Main Loop] --> B[NTP-Zeit holen]
    B --> C[Stunde & Minute in Fibonacci-Zerlegung]
    C --> D[Farbe pro Feld bestimmen]
    D --> E[NeoPixel setzen 40 LEDs]
    D --> F[TM1637: HH:MM:SS ausgeben]
    E --> G[strip.show]
    F --> H[tm1637.show]
    G --> A
    H --> A
```

### 6.1 Bibliotheken

| Bibliothek     | Zweck                        | Installation                     |
|----------------|------------------------------|----------------------------------|
| `rpi_ws281x`   | NeoPixel-Ansteuerung (PWM)   | `pip install rpi_ws281x`         |
| `tm1637`      | TM1637-Display-Ansteuerung   | `pip install raspberrypi-tm1637` |
| `ntplib`      | NTP-Zeitabfrage              | `pip install ntplib`            |
| `datetime`    | Zeit-Verarbeitung            | Python Standardbibliothek       |
| `time`        | sleep, Zeit-Funktionen       | Python Standardbibliothek       |
| `random`      | Zufallsauswahl setBits       | Python Standardbibliothek       |

---

## 7. Code-Entwürfe

### 7.1 Konfiguration (`config.py`)

```python
"""Konfiguration der Fibonacci Ping-Pong-Ball-Uhr."""

# --- NeoPixel ---
LED_PIN        = 18          # GPIO 18 (PWM0)
LED_COUNT      = 40          # 8×5 Bälle
LED_FREQ_HZ    = 800000      # WS2812-Standard
LED_DMA        = 10          # DMA-Kanal
LED_BRIGHTNESS = 0.4         # 0.0–1.0 (40 Bälle: nicht zu hell!)
LED_INVERT     = False
LED_CHANNEL    = 0
LED_STRIP_TYPE = 0x00081008  # NEO_GRB + NEO_KHZ800 (PRÜFEN!)

# --- TM1637 ---
TM1637_CLK     = 23          # GPIO 23
TM1637_DIO     = 24          # GPIO 24
TM1637_BRIGHTNESS = 4        # 0–7

# --- Farben (R, G, B) ---
COLOR_OFF    = (0,   0,   0)
COLOR_HOURS  = (255, 0,   0)   # rot
COLOR_MIN    = (0,   255, 0)   # grün
COLOR_BOTH   = (0,   0,   255) # blau

# --- NTP ---
NTP_SERVER   = "ch.pool.ntp.org"
TIMEZONE     = "Europe/Zurich"

# --- Update ---
UPDATE_INTERVAL_SEC = 10      # alle 10 s aktualisieren
NTP_SYNC_INTERVAL_MIN = 30    # alle 30 min NTP neu synchronisieren
```

### 7.2 LED-Mapping (`mapping.py`)

```python
"""Mapping: 40 physische LEDs → 5 logische Fibonacci-Felder."""

# Schlangenlinie: LED-Index = Zeile × 8 + Spalte
# Raster: 8 Spalten (0–7) × 5 Zeilen (0–4)

FELDER = [
    # (Wert, [LED-Indizes])
    (5, [r * 8 + c for r in range(5) for c in range(5)]),          # A: 25 LEDs
    (3, [r * 8 + c for r in range(3) for c in range(5, 8)]),        # B:  9 LEDs
    (2, [r * 8 + c for r in range(3, 5) for c in range(5, 7)]),      # C:  4 LEDs
    (1, [3 * 8 + 7]),                                               # D:  1 LED
    (1, [4 * 8 + 7]),                                               # E:  1 LED
]

# Verifikation beim Import
assert sum(len(f[1]) for f in FELDER) == 40, "LED-Anzahl stimmt nicht!"
assert sum(f[0] for f in FELDER) == 12, "Fibonacci-Summe stimmt nicht!"
```

### 7.3 Fibonacci-Zerlegung (`fibonacci.py`)

```python
"""Fibonacci-Zerlegung mit Zufallsauswahl (portiert von Arduino setBits)."""
import random

FIB_VALUES = [1, 1, 2, 3, 5]  # Die fünf Fibonacci-Feldwerte

# Alle gültigen Kombinationen für Werte 1–12
# Jede Kombination ist eine Liste von Feld-Indizes (0–4)
# Feld 0 = Wert 1, Feld 1 = Wert 1, Feld 2 = Wert 2, Feld 3 = Wert 3, Feld 4 = Wert 5
COMBINATIONS = {
    1:  [[0], [1]],
    2:  [[2], [0, 1]],
    3:  [[3], [0, 2], [1, 2]],
    4:  [[0, 3], [1, 3], [0, 1, 2]],
    5:  [[4], [2, 3], [0, 1, 3]],
    6:  [[0, 4], [1, 4], [0, 2, 3], [1, 2, 3]],
    7:  [[2, 4], [0, 1, 4], [0, 1, 2, 3]],
    8:  [[3, 4], [0, 2, 4], [1, 2, 4]],
    9:  [[0, 3, 4], [1, 3, 4]],
    10: [[2, 3, 4], [0, 1, 3, 4]],
    11: [[0, 2, 3, 4], [1, 2, 3, 4]],
    12: [[0, 1, 2, 3, 4]],
}

def set_bits(value, offset):
    """
    Wählt per Zufall eine gültige Fibonacci-Kombination für value (1–12).
    Setzt das offset-Bit (0x01=Stunde, 0x02=Minute) in bits[].
    Gibt die Liste der gesetzten Feld-Indizes zurück.
    """
    value = max(1, min(12, value))
    combo = random.choice(COMBINATIONS[value])
    return combo

def get_field_assignment(hours, minutes):
    """
    Bestimmt für Stunde (1–12) und Minute (0–59) welche Felder
    leuchten und mit welcher Bedeutung.
    Gibt ein Dict zurück: {feld_index: 'hours'|'minutes'|'both'|'off'}
    """
    hours_12 = hours % 12
    if hours_12 == 0:
        hours_12 = 12
    min_units = minutes // 5  # 0–12 (5-Minuten-Schritte)
    if min_units == 0:
        min_units = 12  # 0 Minuten = 12 in Fibonacci-Darstellung

    field_bits = [0] * 5  # 0=off, 1=hours, 2=minutes, 3=both

    hour_fields = set_bits(hours_12, 0x01)
    min_fields  = set_bits(min_units, 0x02)

    for f in hour_fields:
        field_bits[f] |= 0x01
    for f in min_fields:
        field_bits[f] |= 0x02

    assignment = {}
    for i in range(5):
        if field_bits[i] == 0x01:
            assignment[i] = 'hours'
        elif field_bits[i] == 0x02:
            assignment[i] = 'minutes'
        elif field_bits[i] == 0x03:
            assignment[i] = 'both'
        else:
            assignment[i] = 'off'

    return assignment
```

### 7.4 NeoPixel-Ansteuerung (`display.py`)

```python
"""NeoPixel-Ansteuerung für 40 LEDs im 8×5-Ball-Raster."""
from rpi_ws281x import PixelStrip, Color
from config import *
from mapping import FELDER

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP_TYPE
)
strip.begin()

# Farb-Tabelle
COLOR_MAP = {
    'off':    Color(0, 0, 0),
    'hours':  Color(255, 0, 0),    # rot  (GRB-Reihenfolge beachten!)
    'minutes': Color(0, 255, 0),    # grün
    'both':   Color(0, 0, 255),    # blau
}

def show_time(field_assignment):
    """
    Setzt alle 40 LEDs gemäß field_assignment.
    field_assignment: {feld_index: 'hours'|'minutes'|'both'|'off'}
    """
    for feld_idx, (wert, led_liste) in enumerate(FELDER):
        role = field_assignment.get(feld_idx, 'off')
        color = COLOR_MAP[role]
        for led in led_liste:
            strip.setPixelColor(led, color)
    strip.show()

def clear_all():
    """Schaltet alle LEDs aus."""
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
```

### 7.5 TM1637-Ansteuerung (`tm1637_display.py`)

```python
"""TM1637 6-stelliges Display – zeigt HH:MM:SS."""
import tm1637
from config import *

display = tm1637.TM1637(clk=TM1637_CLK, dio=TM1637_DIO)
display.brightness(TM1637_BRIGHTNESS)

def show_clock(hours, minutes, seconds):
    """
    Zeigt HH:MM:SS auf dem 6-stelligen TM1637.
    Format: [H, H, M, M, S, S]
    """
    display.show([
        hours   // 10, hours   % 10,
        minutes // 10, minutes % 10,
        seconds // 10, seconds % 10,
    ])
    # Doppelpunkte ein/aus je nach Sekunde (Blinker)
    # Hinweis: tm1637-Library hat unterschiedliche Doppelpunkt-Steuerung
    # bei 4- vs 6-stelligen Modulen. Bei 6-stellig ggf. manuell:
    # display.show(val, colon=True) – Library-spezifisch prüfen!

def show_text(text):
    """Zeigt kurzen Text (max. 6 Zeichen)."""
    display.show(text[:6])

def clear_display():
    display.clear()
```

### 7.6 Zeit-Verwaltung (`ntp_time.py`)

```python
"""NTP-Zeitsynchronisation und lokale Zeit."""
import ntplib
import datetime
import time as time_module
from config import NTP_SERVER, TIMEZONE

_ntp_client = ntplib.NTPClient()
_last_sync = None

def sync_ntp():
    """Synchronisiert Zeit über NTP. Gibt True bei Erfolg zurück."""
    global _last_sync
    try:
        resp = _ntp_client.request(NTP_SERVER, version=3)
        _last_sync = time_module.time()
        return True
    except Exception as e:
        print(f"NTP-Fehler: {e}")
        return False

def get_local_time():
    """Gibt lokale Zeit als (hour, minute, second) zurück."""
    # Europe/Zurich: UTC+1 (Winter) oder UTC+2 (Sommer)
    # Python datetime nutzt System-Zeitzone (muss konfiguriert sein)
    now = datetime.datetime.now()
    return now.hour, now.minute, now.second

def needs_resync(interval_min=30):
    """Prüft, ob eine NTP-Resynchronisation fällig ist."""
    global _last_sync
    if _last_sync is None:
        return True
    elapsed_min = (time_module.time() - _last_sync) / 60
    return elapsed_min >= interval_min
```

### 7.7 Hauptprogramm (`main.py`)

```python
#!/usr/bin/env python3
"""Fibonacci Ping-Pong-Ball-Uhr – Hauptprogramm."""
import time
import signal
import sys

from config import *
from mapping import FELDER
from fibonacci import get_field_assignment
from display import strip, show_time, clear_all
from tm1637_display import display, show_clock, clear_display
from ntp_time import sync_ntp, get_local_time, needs_resync

running = True

def signal_handler(sig, frame):
    global running
    running = False
    clear_all()
    clear_display()
    print("Uhr gestoppt.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    print("Fibonacci Ping-Pong-Ball-Uhr startet...")

    # Erste NTP-Synchronisation
    print("Synchronisiere NTP...")
    if not sync_ntp():
        print("WARNUNG: NTP-Sync fehlgeschlagen – laufe mit Systemzeit.")

    last_display_time = ""
    last_fibo_time = None  # (hour, minute // 5)

    while running:
        # NTP gelegentlich resynchronisieren
        if needs_resync(NTP_SYNC_INTERVAL_MIN):
            sync_ntp()

        h, m, s = get_local_time()

        # --- TM1637: jede Sekunde aktualisieren ---
        current_display = f"{h:02d}{m:02d}{s:02d}"
        if current_display != last_display_time:
            show_clock(h, m, s)
            last_display_time = current_display

        # --- Fibonacci-Anzeige: nur bei 5-Minuten-Wechsel ---
        current_fibo = (h, m // 5)
        if current_fibo != last_fibo_time:
            assignment = get_field_assignment(h, m)
            show_time(assignment)
            last_fibo_time = current_fibo
            print(f"Zeit: {h:02d}:{m:02d} – Felder: {assignment}")

        # Kurze Pause
        time.sleep(UPDATE_INTERVAL_SEC)

if __name__ == "__main__":
    main()
```

### 7.8 Autostart (systemd-Service)

Datei: `/etc/systemd/system/fibonacci-clock.service`

```ini
[Unit]
Description=Fibonacci Ping-Pong-Ball-Uhr
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /home/pi/fibonacci-clock/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fibonacci-clock
sudo systemctl start fibonacci-clock
sudo systemctl status fibonacci-clock
```

> **Wieso root?** `rpi_ws281x` braucht Zugriff auf PWM/DMA → root-Rechte.
> Alternative: udev-Regel für nicht-root (fortgeschritten).

---

## 8. OS-Konfiguration (Raspberry Pi OS)

```bash
# 1. Audio abschalten (PWM-Konflikt!)
sudo nano /boot/config.txt
# Einfügen / sicherstellen:
#   dtparam=audio=off

# 2. Zeitzone setzen
sudo timedatectl set-timezone Europe/Zurich

# 3. NTP aktivieren
sudo timedatectl set-ntp true

# 4. Neustart
sudo reboot

# 5. Bibliotheken installieren
pip3 install rpi_ws281x raspberrypi-tm1637 ntplib

# 6. Test
sudo python3 main.py
```

---

## 9. Fallstricke & Tipps

| # | Problem | Lösung | Konf. |
|---|---------|--------|-------|
| 1 | **GRB vs. RGB** | WS2812B sind meist GRB. `LED_STRIP_TYPE` auf `NEO_GRB` setzen, sonst ist Rot=Grün | hoch |
| 2 | **rpi_ws281x braucht root** | `sudo python3` oder systemd als `User=root` | hoch |
| 3 | **PWM kollidiert mit Audio** | `dtparam=audio=off` in `/boot/config.txt` | hoch |
| 4 | **3,3V-Datenpegel** | Bei 40 LEDs oft OK ohne Shifter, sauberer mit 74AHCT125 | mittel |
| 5 | **Spannungsabfall am Ende** | Bei 40 LEDs ab einer Seite: ggf. zweite 5V-Einspeisung | mittel |
| 6 | **Farbstreuung LED zu LED** | Bälle sortieren oder Kalibrierungs-Array pro LED | mittel |
| 7 | **Hotspot im Ball** | LED in den Ball hinein (Loch schneiden) oder ~5 mm Abstand | mittel |
| 8 | **Feld 5 dominant** | Großes Feld ggf. auf 70% dimmen (separate Helligkeit) | mittel |
| 9 | **TM1637 6-stellig Library** | `raspberrypi-tm1637` unterstützt 6 Ziffern; ältere Libs nur 4 | hoch |
| 10 | **Sommer-/Winterzeit** | `timedatectl set-timezone Europe/Zurich` → automatisch | hoch |
| 11 | **LED-Verdrahtung ≠ Raster** | Schlangenlinie → einfache Formel `row*8+col` | hoch |
| 12 | **Ball-Qualität** | Matte, weiß-transluzente Bälle, keine opaken/weißen Trainingsbälle | hoch |

---

## 10. Gehäuse / Konstruktion

### 10.1 Lochplatte

- Maße: **320 × 200 mm** (8×5 Bälle à 40 mm) + Rand ~20 mm pro Seite
- Löcher: ⌀ 37 mm (Ping-Pong-Ball ⌀ 40 mm presspassen)
- Material: MDF, Sperrholz, 3D-Druck
- Stege zwischen Feldern: 2–3 mm dunkle Trennstege für Fibonacci-Lesbarkeit

### 10.2 LED-Halterung

- Jede LED sitzt **hinter** einem Ball im Loch
- Variante A: LED auf Trägerplatte hinter der Lochplatte (~5 mm Abstand)
- Variante B: LED **in** den Ball geschoben (Loch schneiden, LED einkleben)
  → gleichmäßigeres Licht, aber schwerer zu warten

### 10.3 Zugänglichkeit

- Bälle herausnehmbar (Presspassung)
- LED-Knoten/Verbindungen erreichbar (Klappe oder Schrauben)
- Pi auf separater Trägerplatte hinten, nicht hinter den Bällen

---

## 11. Erweiterungsideen

| Idee | Beschreibung | Aufwand |
|------|--------------|--------|
| LDR (Helligkeitssensor) | Auto-Dim je Raumbeleuchtung | gering |
| Nachtabschaltung | 22:00–06:00 LEDs dimmen/aus | gering |
| Web-Interface | Uhrzeit/Modus im Browser stellen | mittel |
| Modus-Umschalter | Fibonacci ↔ Base4 (gemeinsames Framework) | mittel |
| Farbpaletten | 10 Paletten wie im Original | gering |
| Regenbogen-Modus | Demo-Modus wie Original | gering |
| Second-Precision | Sekunden auf TM1637 (Ball-Anzeige bleibt 5-Min) | bereits geplant |

---

## 12. Fahrplan

1. [x] Konzept und Anzeigeprinzip (diese Bauanleitung)
2. [ ] OS einrichten (Bookworm Lite, Audio off, Zeitzone, NTP)
3. [ ] Hardware beschaffen (siehe Bauteilliste)
4. [ ] LED-Kette verlegen + Mapping-Tabelle verifizieren
5. [ ] Lochplatte bohren + Bälle einpassen
6. [ ] Software testen (NeoPixel-Test, TM1637-Test, NTP-Test)
7. [ ] `main.py` integrieren und testen
8. [ ] systemd-Service einrichten
9. [ ] Gehäuse fertigstellen
10. [ ] In Core-Framework integrieren (gemeinsam mit Base4-Uhr)

---

## 13. Quellen

- Original Fibonacci Clock Firmware: https://github.com/pchretien/fibo
- Nerdiy Fibonacci Clock: https://www.nerdiy.de/fibonacciClock
- Basbrun (Inspiration): http://basbrun.com/
- rpi_ws281x Bibliothek: https://github.com/jgarff/rpi_ws281x
- TM1637 Python Library: https://github.com/timofurrer/raspberrypi-tm1637
- Raspberry Pi Pinout: https://pinout.xyz/

---

## 14. Offene Fragen

- [ ] LEDs pro Ball: 1 (Standard) oder mehr für größere Felder?
- [ ] TM1637-Modul: exaktes Modell/Hersteller spezifizieren?
- [ ] Level-Shifter: zwingend oder „try without first"?
- [ ] Zweite 5V-Einspeisung nötig? (am Aufbau messen)
- [ ] Ball-Orientierung: Naht-Äquator ausrichten?
- [ ] Integration ins Core-Framework mit Base4-Uhr: ja/nein jetzt?

---

*Erstellt von Paul Simmen mit Vibe (GLM-5-2), 14.09.2026*
*Abgeleitet von der Arduino-Fibonacci-Uhr (Philippe Chretien, GNU GPL)*
