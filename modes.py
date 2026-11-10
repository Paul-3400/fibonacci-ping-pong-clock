# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Erweiterung Anzeige-Modi (Stufe 1)
"""Modus-Registry: zehn Anzeige-Modi auf dem 5x8-Raster (Erweiterung).

Platz 1-5 = Taster T1-T5, Platz 6-10 = Shift (T6) + T1-T5.
Planung und Modus-Beschreibungen: docs/Erweiterungen_Anzeigemodi.md.

Jeder Registry-Eintrag hat:
  name      - Anzeigename (Log/Doku)
  available - True = implementiert; False = Platz reserviert (Stufe 2-4)
  tick      - Rendertakt: liefert einen Schluessel, bei dessen Aenderung
              neu gezeichnet wird, z. B. (h, m // 5) fuer Fibonacci.
              None-Differenzierung: nur verfuegbare Modi haben tick/render.
  render    - render(h, m, s) -> Liste aus 40 (R, G, B)-Tupeln
              (Index = LED-Index = Spalte * 8 + Zeile).

Stufe 1 (10.11.2026): Platz 1 (Fibonacci) und Platz 2 (Base4) laufen durch
die neue Schnittstelle (Wrapper auf die bestehenden Funktionen, kein
Code-Duplikat); Platz 3-10 sind reserviert.
"""
from config import (LED_COUNT, COLOR_OFF, COLOR_HOURS, COLOR_MIN,
                    COLOR_BOTH, COLOR_BASE4_BOTH)
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


MODES = {
    1:  {"name": "Fibonacci", "available": True,
         "tick": lambda h, m, s: (h, m // 5), "render": _fibonacci_frame},
    2:  {"name": "Base4", "available": True,
         "tick": lambda h, m, s: (h, m), "render": _base4_frame},
    3:  {"name": "Drei Binärzähler h/m/s", "available": False,
         "tick": None, "render": None},
    4:  {"name": "Grosse Ziffern statisch", "available": False,
         "tick": None, "render": None},
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
