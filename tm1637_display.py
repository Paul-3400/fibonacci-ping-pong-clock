# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
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

def show_field_text(field_idx, value):
    """
    Zeigt im Feld-Durchschalt-Modus z.B. 'C 2' auf dem Display
    (Buchstabe A–E + Wertigkeit des Feldes).
    Hinweis: Buchstaben-Support ist Library-abhängig – bei Problemen
    stattdessen Ziffern verwenden (z.B. '3 2' für Feldindex + Wert).
    """
    letter = "AbCdE"[field_idx]  # Gross-/Kleinschreibung je Segmentfont prüfen
    display.show(f"{letter} {value}")

def clear_display():
    display.clear()
