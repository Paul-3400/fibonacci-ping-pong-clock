# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""NeoPixel-Ansteuerung für 40 LEDs im 5×8-Schnecken-Raster.

Erweiterung Anzeige-Modi (10.11.2026, Stufe 1): show_frame() ist die
generische Schnittstelle für die Modus-Registry (modes.py) - sie setzt
alle 40 LEDs direkt aus einer Liste von (R, G, B)-Tupeln. Die älteren
Feld-Funktionen (show_time/show_field/show_base4) bleiben für
anzeige_test.py und die Bauanleitung erhalten.
"""
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
    'both':   Color(0, 0, 255),    # blau (Fibonacci: Stunde + Minute)
    'both4':  Color(255, 255, 0),  # gelb (Base4: Stunde + Minute)
    'field':  Color(255, 255, 255), # weiss (Feld-Durchschaltung)
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

def show_field(field_idx):
    """
    Zeigt genau ein Feld (0–4 = A–E) in weiss, alle anderen aus.
    Für den Feld-Durchschalt-Modus (Taster 1).
    """
    for i in range(LED_COUNT):
        strip.setPixelColor(i, COLOR_MAP['off'])
    wert, led_liste = FELDER[field_idx]
    for led in led_liste:
        strip.setPixelColor(led, COLOR_MAP['field'])
    strip.show()

def show_base4(ball_states):
    """
    Zeigt die Base4-Matrix: 9 Bälle gemäß ball_states
    ({led_index: 'hours'|'minutes'|'both'|'off'}), alle übrigen LEDs aus.
    'both' = gelb (im Base4-Modus), nicht blau!
    """
    role_color = {'hours': 'hours', 'minutes': 'minutes',
                  'both': 'both4', 'off': 'off'}
    for i in range(LED_COUNT):
        strip.setPixelColor(i, COLOR_MAP['off'])
    for led, role in ball_states.items():
        strip.setPixelColor(led, COLOR_MAP[role_color[role]])
    strip.show()

def show_frame(frame):
    """
    Generische Schnittstelle der Erweiterung Anzeige-Modi (10.11.2026):
    setzt alle 40 LEDs direkt aus einer Liste von 40 (R, G, B)-Tupeln.
    Index = LED-Index = Spalte × 8 + Zeile. Liefert modes.get_frame().
    """
    if len(frame) != LED_COUNT:
        raise ValueError(
            "show_frame erwartet {} Farben, erhalten: {}".format(
                LED_COUNT, len(frame)))
    for led in range(LED_COUNT):
        r, g, b = frame[led]
        strip.setPixelColor(led, Color(r, g, b))
    strip.show()

def clear_all():
    """Schaltet alle LEDs aus."""
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
