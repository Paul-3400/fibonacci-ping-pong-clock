#!/usr/bin/env python3
# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Anzeige-Test der 40-Ball-Tafel
"""Anzeige-Test der Fibonacci-Tafel - Schritt für Schritt, ohne Uhr-Logik.

- Taster 6 (T6): Anzeige ein/aus.
  EIN  = Demo: alle 5 Felder gleichzeitig, jedes in eigener Farbe
        (A=rot, B=grün, C=blau, D=gelb, E=magenta).
  AUS = Tafel dunkel, Einzeltest aktiv (siehe unten).
- Bei AUSgeschalteter Anzeige schalten Taster 1–5 die Felder einzeln
  ein und aus (T1=A, T2=B, T3=C, T4=D, T5=E - in der Demo-Farbe).
- TM1637 zeigt die Summe der leuchtenden Feld-Werte (0–12):
  A=5, B=3, C=2, D=1, E=1 - alle zusammen ergeben 12.
- Strg+C: Tafel aus + Zusammenfassung der geprüften Taster.
"""
import time
from gpiozero import Button
from rpi_ws281x import Color

from config import (BTN_FIELD_PIN, BTN_MIN_PIN, BTN_MIN5_PIN,
                    BTN_HOUR_PIN, BTN_NORM_PIN, BTN_MODE_PIN, BTN_BOUNCE_SEC)
from mapping import FELDER
import display                                   # erzeugt strip + begin()
from tm1637_display import display as tm, clear_display

FELD_INFO = ["A (25 Baelle, Wert 5)", "B (9 Baelle, Wert 3)",
             "C (4 Baelle, Wert 2)", "D (A5, Wert 1)", "E (B5, Wert 1)"]
FELD_FARBE = [
    Color(255, 0, 0),      # A: rot
    Color(0, 255, 0),      # B: grün
    Color(0, 0, 255),      # C: blau
    Color(255, 255, 0),    # D: gelb
    Color(255, 0, 255),    # E: magenta
]

# Test-Zustand
zustand = {"demo": False, "feld": [False] * 5, "gedrueckt": set()}


def zeige_summe(summe):
    """Rechtsbündige Summe (0–12) auf dem 6-stelligen TM1637."""
    segs = [tm.encode_digit(int(z)) for z in str(summe)]
    tm.write([0] * (6 - len(segs)) + segs, 0)


def render():
    """Zeichnet Tafel + TM1637 gemäß Zustand."""
    for i, (_, leds) in enumerate(FELDER):
        farbe = (FELD_FARBE[i] if (zustand["demo"] or zustand["feld"][i])
                 else Color(0, 0, 0))
        for led in leds:
            # Fallstrick 33: logische LED -> physische LED spiegeln
            display.strip.setPixelColor(display._PHYS_LED[led], farbe)
    display.strip.show()
    if zustand["demo"]:
        summe = 12
    else:
        summe = sum(FELDER[i][0] for i in range(5) if zustand["feld"][i])
    zeige_summe(summe)


def handle_event(nr):
    """Taster-Ereignis: 1–5 = Feld an/aus (nur wenn Anzeige aus), 6 = Demo."""
    zustand["gedrueckt"].add(nr)
    if nr == 6:
        zustand["demo"] = not zustand["demo"]
        if not zustand["demo"]:
            zustand["feld"] = [False] * 5
        print("T6: Anzeige " +
              ("EIN - Demo: alle 5 Felder in eigenen Farben"
               if zustand["demo"] else "AUS - T1-T5 schalten einzelne Felder"))
    elif zustand["demo"]:
        print("T%d: ignoriert - Anzeige ist im Demo-Modus (erst T6 fuer AUS)"
              % nr)
        return
    else:
        i = nr - 1
        zustand["feld"][i] = not zustand["feld"][i]
        print("T%d: Feld %s %s" %
              (nr, FELD_INFO[i], "EIN" if zustand["feld"][i] else "AUS"))
    render()


def main():
    pins = [BTN_FIELD_PIN, BTN_MIN_PIN, BTN_MIN5_PIN,
            BTN_HOUR_PIN, BTN_NORM_PIN]
    taster = [Button(p, bounce_time=BTN_BOUNCE_SEC) for p in pins]
    t6 = Button(BTN_MODE_PIN, bounce_time=BTN_BOUNCE_SEC)
    ereignisse = []
    for i, b in enumerate(taster):
        b.when_pressed = lambda nr=i + 1: ereignisse.append(nr)
    t6.when_pressed = lambda: ereignisse.append(6)

    print("Anzeige-Test: T6 = Anzeige ein/aus (alle 5 Felder in Farben)")
    print("              T1-T5 = einzelne Felder ein/aus (bei Anzeige AUS)")
    print("              Strg+C beendet.")
    clear_display()
    render()
    try:
        while True:
            while ereignisse:
                handle_event(ereignisse.pop(0))
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        display.clear_all()
        clear_display()
        geprueft = sorted(zustand["gedrueckt"])
        print("\nGepruefte Taster: " +
              (", ".join("T%d" % g for g in geprueft) if geprueft
               else "keine"))
        print("Anzeige aus. Test beendet.")


if __name__ == "__main__":
    main()