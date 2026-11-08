# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""TM1637 6-stelliges Display – zeigt HH:MM:SS."""
import tm1637
from config import *

display = tm1637.TM1637(clk=TM1637_CLK, dio=TM1637_DIO)
display.brightness(TM1637_BRIGHTNESS)

# Wichtig (08.11.2026, Library-Quellcode geprueft): raspberrypi-tm1637 ist
# auf 4-stellige Module ausgelegt - show() nimmt Strings (4 Zeichen laut
# Doku), und clear() existiert NICHT. Fuer 6 Stellen: write(segments, 0)
# mit encode_digit()/encode_string() - write() schreibt bis 6 Segmente.

def show_clock(hours, minutes, seconds):
    """Zeigt HH:MM:SS auf dem 6-stelligen TM1637 (fuehrende Nullen inkl.)."""
    display.write([
        display.encode_digit(hours   // 10), display.encode_digit(hours   % 10),
        display.encode_digit(minutes // 10), display.encode_digit(minutes % 10),
        display.encode_digit(seconds // 10), display.encode_digit(seconds % 10),
    ], 0)
    # Doppelpunkte/Dezimalpunkte stecken im MSB je Segment - deren Lage ist
    # modulabhaengig; fuer HH:MM:SS reicht die 6-Ziffern-Anzeige ohne
    # Colon-Steuerung (die Doppelpunkte des Moduls bleiben aus).

def show_text(text):
    """Zeigt kurzen Text (max. 6 Zeichen)."""
    display.write(display.encode_string(str(text)[:6]), 0)

def show_field_text(field_idx, value):
    """Zeigt im Feld-Durchschalt-Modus z.B. 'A 5' (Buchstabe + Wertigkeit)."""
    letter = "AbCdE"[field_idx]
    display.write(display.encode_string(f"{letter} {value}"[:6]), 0)

def clear_display():
    display.write([0, 0, 0, 0, 0, 0], 0)
