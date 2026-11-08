# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Base4-Zerlegung – portiert aus der 9-Baelle-Ping-Pong-Uhr (Schwesterprojekt).
Wertemengen seit 14.10.2026 vollstaendig (alle 24 h / 60 min darstellbar)."""
from mapping import BASE4_MATRIX

# Werte je Ball (feste Position, siehe mapping.BASE4_MATRIX)
HOUR_VALUES   = [16, 12, 8, 4, 3, 2, 1]        # 48/32 nur fuer Minuten
MINUTE_VALUES = [48, 32, 16, 8, 4, 3, 2, 1]

def _decompose(value, values):
    """Zerlegt value gierig in Summanden aus values (jeder Wert max. 1x)."""
    parts = []
    for v in values:
        if v <= value:
            parts.append(v)
            value -= v
    return parts

def get_ball_states(h, m):
    """
    Liefert {led_index: 'hours'|'minutes'|'both'|'off'} fuer die 9 Matrix-Baelle.
    Im Base4-Modus bedeutet 'both' GELB (Stunde + Minute), nicht blau.
    Aufloesung: 1 Minute (Update jede Minute).
    """
    h = h % 24
    hparts = set(_decompose(h, HOUR_VALUES))
    mparts = set(_decompose(m, MINUTE_VALUES))

    states = {}
    for wert, led in BASE4_MATRIX:
        role = 'off'
        if wert in hparts and wert in mparts:
            role = 'both'          # gelb
        elif wert in hparts:
            role = 'hours'         # rot
        elif wert in mparts:
            role = 'minutes'       # gruen
        states[led] = role
    return states
