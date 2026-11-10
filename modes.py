# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Erweiterung Anzeige-Modi
"""Modus-Registry: zehn Anzeige-Modi auf dem 5x8-Raster (Erweiterung).

Platz 1-5 = Taster T1-T5, Platz 6-10 = Shift (T6) + T1-T5.
Planung und Modus-Beschreibungen: docs/Erweiterungen_Anzeigemodi.md.

Jeder Registry-Eintrag hat:
  name      - Anzeigename (Log/Doku)
  available - True = implementiert; False = Platz reserviert (Stufe 3-4)
  tick      - Rendertakt: liefert einen Schluessel, bei dessen Aenderung
              neu gezeichnet wird, z. B. (h, m // 5) fuer Fibonacci.
  render    - render(h, m, s) -> Liste aus 40 (R, G, B)-Tupeln
              (Index = LED-Index = Spalte * 8 + Zeile).

Stufe 1 (10.11.2026): Platz 1 (Fibonacci) und 2 (Base4) als Wrapper auf
die bestehenden Funktionen - kein Code-Duplikat.
Stufe 2 (10.11.2026): Platz 3 (drei Binaerzaehler h/m/s) und Platz 4
(grosse statische Ziffern mit font5x7.py) dazugebaut.
Platz 5-10: reserviert (Stufe 3-4).
"""
from config import (LED_COUNT, COLOR_OFF, COLOR_HOURS, COLOR_MIN,
                    COLOR_BOTH, COLOR_BASE4_BOTH, COLOR_FIELD,
                    ZIFFERN_WECHSEL_SEC)
import font5x7
from mapping import FELDER
from fibonacci import get_field_assignment
from base4 import get_ball_states

# Rollen -> Farben, je Modus ('both' ist blau bei Fibonacci, gelb bei Base4)
_FIB_COLORS = {'hours': COLOR_HOURS, 'minutes': COLOR_MIN,
                'both': COLOR_BOTH, 'off': COLOR_OFF}
_BASE4_COLORS = {'hours': COLOR_HOURS, 'minutes': COLOR_MIN,
                 'both': COLOR_BASE4_BOTH, 'off': COLOR_OFF}


def _fibonacci_frame(h, m, s):
    """Platz 1: Fibonacci-Schnecke - Felder A-E gemaess get_field_assignment."""
    assignment = get_field_assignment(h, m)
    frame = [COLOR_OFF] * LED_COUNT
    for feld_idx, (wert, leds) in enumerate(FELDER):
        farbe = _FIB_COLORS[assignment.get(feld_idx, 'off')]
        for led in leds:
            frame[led] = farbe
    return frame


def _base4_frame(h, m, s):
    """Platz 2: Base4-Matrix - 9 Baelle gemaess get_ball_states, Rest dunkel."""
    states = get_ball_states(h, m)
    frame = [COLOR_OFF] * LED_COUNT
    for led, role in states.items():
        frame[led] = _BASE4_COLORS[role]
    return frame


def _binary_frame(h, m, s):
    """
    Platz 3 (Stufe 2, Idee Paul): drei senkrechte Binaerzaehler -
    Stunden (Spalte A, rot, 5 Bit), Minuten (Spalte C, gruen, 6 Bit),
    Sekunden (Spalte E, gelb, 6 Bit). LSB unten (Zeile 7), MSB oben.
    Spalten B und D bleiben dunkel (Trenner). 24-h-Zaehlung.
    LED-Index = Spalte * 8 + Zeile.
    """
    frame = [COLOR_OFF] * LED_COUNT
    for bit in range(5):                 # Stunden 0-23: Bit 0..4
        if (h >> bit) & 1:
            frame[0 * 8 + (7 - bit)] = COLOR_HOURS
    for bit in range(6):                 # Minuten 0-59: Bit 0..5
        if (m >> bit) & 1:
            frame[2 * 8 + (7 - bit)] = COLOR_MIN
    for bit in range(6):                 # Sekunden 0-59: Bit 0..5
        if (s >> bit) & 1:
            frame[4 * 8 + (7 - bit)] = COLOR_BASE4_BOTH
    return frame


def _big_digit_frame(h, m, s):
    """
    Platz 4 (Stufe 2, Idee Paul, Variante A): eine grosse Ziffer fuellt
    die ganze Tafel (5 Spalten x 7 Zeilen, font5x7). Zyklus minutenorientiert:
    H-Zehner -> H-Einer -> M-Zehner -> M-Einer, jede Ziffer steht
    ZIFFERN_WECHSEL_SEC Sekunden (H-Zehner startet bei Sekunde 0).
    Stunden-Ziffern rot, Minuten-Ziffern gruen. Zeile 7 bleibt frei bis
    auf den weissen Sekundenpunkt (Spalte C), der im Sekundentakt blinkt.
    """
    frame = [COLOR_OFF] * LED_COUNT
    idx = (s // ZIFFERN_WECHSEL_SEC) % 4
    ziffer = f"{h // 10}{h % 10}{m // 10}{m % 10}"[idx]
    farbe = COLOR_HOURS if idx < 2 else COLOR_MIN
    for spalte in range(5):
        spaltenbyte = font5x7.glyph(ziffer)[spalte]
        for zeile in range(7):           # Zeilen 0-6, Bit 0 = oben
            if spaltenbyte & (1 << zeile):
                frame[spalte * 8 + zeile] = farbe
    if s % 2 == 0:                       # Sekundenpunkt: Spalte C, Zeile 7
        frame[2 * 8 + 7] = COLOR_FIELD  # weiss, blinkt im Sekundentakt
    return frame


MODES = {
    1:  {"name": "Fibonacci", "available": True,
         "tick": lambda h, m, s: (h, m // 5), "render": _fibonacci_frame},
    2:  {"name": "Base4", "available": True,
         "tick": lambda h, m, s: (h, m), "render": _base4_frame},
    3:  {"name": "Drei Binärzähler h/m/s", "available": True,
         "tick": lambda h, m, s: (h, m, s), "render": _binary_frame},
    4:  {"name": "Grosse Ziffern statisch", "available": True,
         "tick": lambda h, m, s: (h, m, s), "render": _big_digit_frame},
    5:  {"name": "Tagesfortschritt", "available": False,
         "tick": None, "render": None},
    6:  {"name": "Binär-BCD-Uhr", "available": False,
         "tick": None, "render": None},
    7:  {"name": "Laufschrift (durchlaufende Zahlen)", "available": False,
         "tick": None, "render": None},
    8:  {"name": "Sekunden-Serpentine", "available": False,
         "tick": None, "render": None},
    9:  {"name": "Analog-Uhr (Experiment)", "available": False,
         "tick": None, "render": None},
    10: {"name": "Pong-Uhr", "available": False,
         "tick": None, "render": None},
}

assert set(MODES) == set(range(1, 11)), "Modus-Registry muss Plaetze 1-10 haben!"


def is_available(mode_id):
    """True, wenn der Modus implementiert ist (verfuegbarer Platz)."""
    return bool(MODES.get(mode_id, {}).get("available"))


def get_tick(mode_id, h, m, s):
    """Rendertakt-Schluessel des Modus (None, wenn Modus nicht verfuegbar)."""
    modus = MODES.get(mode_id)
    if not modus or not modus["available"]:
        return None
    return modus["tick"](h, m, s)


def get_frame(mode_id, h, m, s):
    """40er-Farb-Frame des Modus (None, wenn Modus nicht verfuegbar)."""
    modus = MODES.get(mode_id)
    if not modus or not modus["available"]:
        return None
    frame = modus["render"](h, m, s)
    assert len(frame) == LED_COUNT, "render() muss 40 Farben liefern!"
    return frame