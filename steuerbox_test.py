#!/usr/bin/env python3
# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2
"""
Steuerbox-Selbsttest - laeuft ohne Anzeigebox und ohne Clone der Projektsoftware.

  * 6-stelliges TM1637 zeigt die Uhrzeit als HH:MM:SS (mit fuehrenden Nullen)
  * Tastendruck: Display zeigt 2 s lang 'TEST n' (n = Nummer der Taste, 1-6)
  * Strg+C beendet und fasst zusammen, welche Tasten geprueft wurden

Benoetigt: raspberrypi-tm1637 (pip install), gpiozero (auf Raspberry Pi OS
vorhanden). Kein sudo noetig - nur Taster-Eingaenge und das TM1637.

Technik-Hinweis: Die tm1637-Library ist auf 4-stellige Module ausgelegt
(show() = max. 4 Zeichen, clear() existiert nicht). Fuer 6 Stellen:
write(segments, 0) mit encode_digit() - write() schreibt bis 6 Segmente.

Modul-Hinweis (10.11.2026, Fallstrick 31, endgueltig): Das verwendete
6-stellige Modul zeigt die an write() uebergebene Segmentliste spiegelt
je Haelfte (Roh-Befehl '123456' zeigte «321654»). modul_segments()
kehrt deshalb jede 3-Zeichen-Haelfte vor write() um.
"""
import time
import tm1637
from gpiozero import Button

# --- Pins laut Bauanleitung Kap. 4 ---
CLK = 23            # GPIO 23 (Pin 16) -> TM1637 CLK
DIO = 24            # GPIO 24 (Pin 18) -> TM1637 DIO
TASTER = [
    (1, 5),         # T1: GPIO 5  (Pin 29)  Felder A-E durchschalten
    (2, 6),         # T2: GPIO 6  (Pin 31)  +1 Minute
    (3, 12),        # T3: GPIO 12 (Pin 32)  +5 Minuten
    (4, 13),        # T4: GPIO 13 (Pin 33)  +1 Stunde
    (5, 16),        # T5: GPIO 16 (Pin 36)  Normalbetrieb
    (6, 26),        # T6: GPIO 26 (Pin 37)  Modus Fibonacci/Base4
]

ZEIGE_DAUER = 2.0   # so lange bleibt 'TEST n' stehen (s)

display = tm1637.TM1637(clk=CLK, dio=DIO, brightness=7)
buttons = {nr: Button(pin, bounce_time=0.03) for nr, pin in TASTER}
geprueft = set()
_letzte_ziffern = None


def modul_segments(segments):
    """6-stelliges Modul: zeigt die Liste spiegelt je Haelfte (Fallstrick
    31) - Haelften umkehren, damit der Text richtig erscheint."""
    s = list(segments[:6]) + [0] * (6 - len(segments))
    return [s[2], s[1], s[0], s[5], s[4], s[3]]


def zeige_uhr():
    """HH:MM:SS mit fuehrenden Nullen; schreibt nur bei Sekundenwechsel."""
    global _letzte_ziffern
    t = time.localtime()
    ziffern = (t.tm_hour // 10, t.tm_hour % 10,
               t.tm_min // 10, t.tm_min % 10,
               t.tm_sec // 10, t.tm_sec % 10)
    if ziffern != _letzte_ziffern:
        display.write(modul_segments([display.encode_digit(z) for z in ziffern]), 0)
        _letzte_ziffern = ziffern


def zeige_test(nr):
    """'TEST n' (6 Zeichen) anzeigen."""
    global _letzte_ziffern
    display.write(modul_segments(display.encode_string("TEST " + str(nr))), 0)
    _letzte_ziffern = None


if __name__ == "__main__":
    print("Steuerbox-Selbsttest: Uhr laeuft - Tasten T1-T6 druecken, Strg+C beendet.")
    try:
        zeige_bis = 0.0
        while True:
            jetzt = time.time()
            for nr, b in buttons.items():
                if b.is_pressed:
                    zeige_test(nr)
                    geprueft.add(nr)
                    zeige_bis = jetzt + ZEIGE_DAUER
                    break
            if jetzt >= zeige_bis:
                zeige_uhr()
            time.sleep(0.05)
    except KeyboardInterrupt:
        display.write([0] * 6, 0)
        fehlen = sorted(set(range(1, 7)) - geprueft)
        print("\nGepruefte Tasten:", ", ".join("T" + str(n) for n in sorted(geprueft)) or "keine")
        if fehlen:
            print("NICHT geprueft:", ", ".join("T" + str(n) for n in fehlen))
