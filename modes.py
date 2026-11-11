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
Stufe 3 (11.11.2026): Platz 5 (Tagesfortschritt), Platz 6 (Binär-BCD),
Platz 7 (EierUhr) und Platz 8 (Sekunden-Serpentine) dazugebaut.
Platz 9-10: reserviert (Stufe 4).
"""
from config import (LED_COUNT, COLOR_OFF, COLOR_HOURS, COLOR_MIN,
                    COLOR_BOTH, COLOR_BASE4_BOTH, COLOR_FIELD,
                    ZIFFERN_WECHSEL_SEC, COLOR_GLAS, COLOR_ORANGE,
                    SERPENTINE_DIM_FAKTOR, DAY_PHASES)
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



def _day_progress_frame(h, m, s):
    """
    Platz 5 (Stufe 3, Vibe-Vorschlag): Tagesfortschritt-Balken -
    40 LEDs = 1440 min, also 36 min je LED, in Kettenreihenfolge
    (LED 0 = A0 oben links ... LED 39 = E7 unten rechts). LED i leuchtet,
    wenn floor(Minuten_seit_Mitternacht / 36) mindestens i ist.
    Farbe tageszeitabhaengig (Entscheid 11.11.2026): die ganze Leiste in
    der Farbe der aktuellen Tagesphase - Nacht blau, Morgen orange,
    Mittag gelb, Abend rot (config.DAY_PHASES, Stimmungsanzeige).
    Minutentakt genuegt: tick = (h, m).
    """
    frame = [COLOR_OFF] * LED_COUNT
    stand = (h * 60 + m) // 36                     # 0-39
    farbe = DAY_PHASES[0][1]
    for beginn, phase_farbe in DAY_PHASES:
        if h >= beginn:
            farbe = phase_farbe
    for led in range(min(stand, LED_COUNT - 1) + 1):
        frame[led] = farbe
    return frame


def _bcd_frame(h, m, s):
    """
    Platz 6 (Stufe 3, Idee Paul, Variante A): klassische Binär-BCD-Uhr -
    jede Dezimalziffer einzeln im Binaercode, eine Spalte je Ziffer,
    LSB unten (Zeile 7), 24-h-Zaehlung. Spalten: A = H-Zehner (2 bit),
    B = H-Einer (4 bit), C = M-Zehner (3 bit), D = M-Einer (4 bit),
    E = S-Einer (4 bit; Entscheid 11.11.2026: mit Sekunden).
    Farben: A/B rot, C/D gruen, E gelb. Rendertakt 1 s.
    """
    frame = [COLOR_OFF] * LED_COUNT

    def _setze_bcd(spalte, wert, nbits, farbe):
        for bit in range(nbits):
            if (wert >> bit) & 1:
                frame[spalte * 8 + (7 - bit)] = farbe

    _setze_bcd(0, h // 10, 2, COLOR_HOURS)
    _setze_bcd(1, h % 10, 4, COLOR_HOURS)
    _setze_bcd(2, m // 10, 3, COLOR_MIN)
    _setze_bcd(3, m % 10, 4, COLOR_MIN)
    _setze_bcd(4, s % 10, 4, COLOR_BASE4_BOTH)
    return frame


# Platz 7 (Stufe 3, Idee Paul 10.11.2026): EierUhr - Sanduhr-Glas auf der
# Tafel. Logische LEDs (Index = Spalte * 8 + Zeile, Zeile 0 oben), Design
# nach Pauls Skizze, siehe docs/Erweiterungen_Anzeigemodi.md Kap. 5.
_EIERUHR_UMRISS = (0, 8, 16, 24, 32,     # Zeile 0 komplett (Glas oben)
                   1, 33, 2, 34,         # Waende A/E, Zeilen 1-2
                   3, 11, 19, 27,        # Taille Zeile 3 (Spalten A-D)
                   12, 20, 28,           # Taille Zeile 4 (Spalten B-D)
                   5, 37, 6, 38,         # Waende A/E, Zeilen 5-6
                   7, 15, 23, 31, 39)    # Zeile 7 komplett (Glas unten)
_EIERUHR_OBEN = (10, 18, 26,             # Kugelplaetze Zeile 2 (B, C, D)
                 9, 17, 25)              # Kugelplaetze Zeile 1 (B, C, D)
_EIERUHR_UNTEN = (14, 22, 30,            # Kugelplaetze Zeile 6 (B, C, D)
                  13, 21, 29)            # Kugelplaetze Zeile 5 (B, C, D)
assert len(_EIERUHR_UMRISS) == 25, "EierUhr: Umriss muss 25 LEDs haben!"
assert len(_EIERUHR_OBEN) == len(_EIERUHR_UNTEN) == 6,     "EierUhr: je 6 Kugelplaetze oben und unten!"
assert len(set(_EIERUHR_UMRISS) | set(_EIERUHR_OBEN) | set(_EIERUHR_UNTEN)) == 37,     "EierUhr: Umriss + 12 Kugelplaetze muessen 37 verschiedene LEDs sein!"


def _egg_timer_frame(h, m, s):
    """
    Platz 7 (Stufe 3, Idee Paul, Entscheid 10.11.2026): EierUhr (Sanduhr) -
    6 gelbe Kugeln (30 s je Kugel) fallen vom oberen in den unteren Teil
    eines gedimmten Sanduhr-Glases. Zyklus 3 min, an volle Minuten gebunden:
    elapsed = (m mod 3) * 60 + s, Neustart bei x:00/x:03/x:06 ...
    Falllogik Variante 1: gefallen = elapsed // 30 (0-5), Kugel k faellt
    bei k * 30 s. Der obere Raum leert sich von unten nach oben (erst
    Zeile 2, dann Zeile 1, je B-C-D), der untere fuellt sich von unten
    nach oben (erst Zeile 6, dann Zeile 5). "Alle 6 Kugeln unten" ist
    bewusst nie sichtbar - der Sprung zurueck auf 6 Kugeln oben markiert
    die 3-Minuten-Grenze. Umriss gedimmt (COLOR_GLAS), Kugeln gelb
    (COLOR_BASE4_BOTH, Sand-Optik). Rendertakt 1 s.
    """
    frame = [COLOR_OFF] * LED_COUNT
    for led in _EIERUHR_UMRISS:
        frame[led] = COLOR_GLAS
    elapsed = (m % 3) * 60 + s
    gefallen = elapsed // 30                      # Variante 1: 0-5
    for led in _EIERUHR_OBEN[gefallen:]:         # oben leert sich von unten
        frame[led] = COLOR_BASE4_BOTH
    for led in _EIERUHR_UNTEN[:gefallen]:        # unten fuellt sich von unten
        frame[led] = COLOR_BASE4_BOTH
    return frame


def _serpentine_frame(h, m, s):
    """
    Platz 8 (Stufe 3, Vibe-Vorschlag): Sekunden-Serpentine - die laufende
    Minute fuellt die Tafel in Kettenreihenfolge (A0 -> E7):
    LED = s mod 40. Runde 1 (0-39 s) gruen, Runde 2 (40-59 s) orange.
    Erweiterte Variante (Entscheid 11.11.2026): Nach Sekunde 39 bleiben
    die 40 LEDs der Runde 1 gedimmt stehen (SERPENTINE_DIM_FAKTOR),
    Runde 2 uebermalt sie mit voller Helligkeit orange - der
    Minutenfortschritt wird doppelt genau sichtbar. Rendertakt 1 s.
    """
    frame = [COLOR_OFF] * LED_COUNT
    gedimmt = tuple(int(wert * SERPENTINE_DIM_FAKTOR) for wert in COLOR_MIN)
    if s < 40:
        for led in range(s + 1):
            frame[led] = COLOR_MIN
    else:
        for led in range(LED_COUNT):
            frame[led] = gedimmt
        for led in range(s - 39):
            frame[led] = COLOR_ORANGE
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
    5:  {"name": "Tagesfortschritt", "available": True,
         "tick": lambda h, m, s: (h, m), "render": _day_progress_frame},
    6:  {"name": "Binär-BCD-Uhr", "available": True,
         "tick": lambda h, m, s: (h, m, s), "render": _bcd_frame},
    7:  {"name": "EierUhr (Sanduhr)", "available": True,
         "tick": lambda h, m, s: (h, m, s), "render": _egg_timer_frame},
    8:  {"name": "Sekunden-Serpentine", "available": True,
         "tick": lambda h, m, s: (h, m, s), "render": _serpentine_frame},
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