#!/usr/bin/env python3
# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 11.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Stub-Test Stufe 3 (Modi 5-8)
"""Stub-Tests der Stufe-3-Modi gegen unabhaengige Referenzlogik.

Referenz: docs/Erweiterungen_Anzeigemodi.md Kap. 5 (Modi 5-8) und die
Festlegungen vom 11.11.2026 (Farbverlauf, BCD mit Sekunden, Serpentine
erweitert). modes.py importiert nur reines Python (kein rpi_ws281x) -
der Test laeuft ohne Hardware: python3 test_stufe3.py
"""
from config import (LED_COUNT, COLOR_OFF, COLOR_HOURS, COLOR_MIN,
                    COLOR_BOTH, COLOR_BASE4_BOTH, COLOR_GLAS,
                    COLOR_ORANGE, SERPENTINE_DIM_FAKTOR, COLOR_FIELD)
import modes

PASS = 0


def check(bedingung, text):
    global PASS
    assert bedingung, "FEHLER: " + text
    PASS += 1


def frame_ok(frame):
    """Grundcheck: 40 Farben, jede ein (R, G, B)-Tupel."""
    return (len(frame) == 40
            and all(isinstance(f, tuple) and len(f) == 3 for f in frame))


# ---------- unabhaengige Referenzlogik (bewusst anders formuliert) ----------

def ref_tag_farbe(h):
    if h < 6 or h >= 21:
        return COLOR_BOTH          # Nacht blau
    if h < 9:
        return COLOR_ORANGE        # Morgen orange
    if h < 17:
        return COLOR_BASE4_BOTH    # Mittag gelb
    return COLOR_HOURS             # Abend rot


def ref_modus5(h, m):
    """Doku-Formel: LED i leuchtet, wenn floor(min/36) >= i."""
    frame = [COLOR_OFF] * 40
    for i in range(40):
        if (h * 60 + m) // 36 >= i:
            frame[i] = ref_tag_farbe(h)
    return frame


def ref_modus6(h, m, s):
    frame = [COLOR_OFF] * 40
    for spalte, ziffer, nbits, farbe in (
            (0, h // 10, 2, COLOR_HOURS), (1, h % 10, 4, COLOR_HOURS),
            (2, m // 10, 3, COLOR_MIN), (3, m % 10, 4, COLOR_MIN),
            (4, s % 10, 4, COLOR_BASE4_BOTH)):
        for b in range(nbits):
            if ziffer >> b & 1:
                frame[spalte * 8 + (7 - b)] = farbe
    return frame


def ref_modus7(m, s):
    umriss = {0, 8, 16, 24, 32, 1, 33, 2, 34, 3, 11, 19, 27, 12, 20, 28,
              5, 37, 6, 38, 7, 15, 23, 31, 39}
    oben = [10, 18, 26, 9, 17, 25]     # leer: erst Zeile 2, dann Zeile 1
    unten = [14, 22, 30, 13, 21, 29]    # fuell: erst Zeile 6, dann Zeile 5
    elapsed = (m % 3) * 60 + s
    gefallen = elapsed // 30           # Variante 1
    frame = [COLOR_GLAS if i in umriss else COLOR_OFF for i in range(40)]
    for led in oben[gefallen:] + unten[:gefallen]:
        frame[led] = COLOR_BASE4_BOTH
    return frame


def ref_modus8(s):
    frame = [COLOR_OFF] * 40
    gedimmt = (0, int(255 * SERPENTINE_DIM_FAKTOR), 0)
    if s < 40:
        for i in range(s + 1):
            frame[i] = COLOR_MIN
    else:
        frame = [gedimmt] * 40
        for i in range(s - 39):
            frame[i] = COLOR_ORANGE
    return frame


# ---------- G1: Registry ----------
# Stufe-4-Update (11.11.2026): Plaetze 9-10 sind seither implementiert
# (Modus 9 Analog-Uhr, Modus 10 Pong-Uhr) - geprueft in test_stufe4.py.

check(all(modes.is_available(i) for i in range(1, 9)),
      "Plaetze 1-8 muessen verfuegbar sein")
check(all(modes.is_available(i) for i in (9, 10)),
      "Plaetze 9-10 verfuegbar (Stufe 4, 11.11.2026)")
check(modes.get_frame(11, 14, 35, 49) is None and
      modes.get_tick(0, 14, 35, 49) is None,
      "unbekannte Plaetze liefern None")
check(modes.MODES[7]["name"] == "EierUhr (Sanduhr)",
      "Platz 7 heisst EierUhr (Laufschrift ersetzt)")
check(modes.get_tick(5, 14, 35, 49) == (14, 35),
      "Modus 5: Minutentakt (h, m)")
check(all(modes.get_tick(i, 14, 35, 49) == (14, 35, 49) for i in (6, 8)),
      "Modi 6+8: Sekundentakt (h, m, s)")
check(modes.get_tick(7, 14, 35, 49) == (14, 35, 49, 0),
      "Modus 7: Sekundentakt + Animationsphase 0 (kein Fall um 35:49, Stufe 4)")

# ---------- G2: Modus 5 (Tagesfortschritt) ----------

f5 = modes.get_frame(5, 14, 35, 49)
check(frame_ok(f5), "Modus 5: Frame-Form")
check([i for i, c in enumerate(f5) if c != COLOR_OFF] == list(range(25)),
      "14:35 = 875 min -> floor 24 -> LEDs 0-24 (25 LEDs, Doku-Beispiel)")
check(f5[0] == COLOR_BASE4_BOTH and f5[24] == COLOR_BASE4_BOTH,
      "14:35 Mittagsphase: Leiste gelb")
f5n = modes.get_frame(5, 3, 0, 0)
check(f5n[0] == COLOR_BOTH, "03:00 Nachtphase: blau")
f5o = modes.get_frame(5, 7, 0, 0)
check(f5o[0] == COLOR_ORANGE, "07:00 Morgenphase: orange")
f5a = modes.get_frame(5, 18, 0, 0)
check(f5a[0] == COLOR_HOURS, "18:00 Abendphase: rot")
f5s = modes.get_frame(5, 23, 0, 0)
check(f5s[0] == COLOR_BOTH, "23:00 Nachtphase: blau")
check(sum(c != COLOR_OFF for c in modes.get_frame(5, 0, 0, 0)) == 1,
      "00:00: LED 0 leuchtet (Doku-Formel floor 0 >= 0)")
check(all(c != COLOR_OFF for c in modes.get_frame(5, 23, 59, 0)),
      "23:59: alle 40 LEDs (Volllast am Tagesende)")
for h in range(0, 24, 1):
    for m in (0, 17, 35, 59):
        assert modes.get_frame(5, h, m, 0) == ref_modus5(h, m), \
            f"Modus 5 weicht ab bei {h:02d}:{m:02d}"
check(True, "Modus 5: komplette Referenz ueber 24 h x 4 Minuten (96 Faelle)")

# ---------- G3: Modus 6 (Binär-BCD) ----------

f6 = modes.get_frame(6, 14, 35, 49)
check(frame_ok(f6), "Modus 6: Frame-Form")
check({i for i, c in enumerate(f6) if c == COLOR_HOURS} == {7, 13},
      "14:35:49 rot = A7 (H-Zehner 1), B5 (H-Einer 4) - Doku-Beispiel")
check({i for i, c in enumerate(f6) if c == COLOR_MIN} == {23, 22, 31, 29},
      "14:35:49 gruen = C7+C6 (3), D7+D5 (5)")
check({i for i, c in enumerate(f6) if c == COLOR_BASE4_BOTH} == {39, 36},
      "14:35:49 gelb = E7+E4 (9)")
check(all(c == COLOR_OFF for c in modes.get_frame(6, 0, 0, 0)),
      "00:00:00: alles dunkel")
f6x = modes.get_frame(6, 23, 59, 59)
check({i for i, c in enumerate(f6x) if c == COLOR_HOURS} == {6, 14, 15},
      "23:59:59 rot = A6 (Zehner 2 = b10), B7+B6 (Einer 3 = b11)")
check({i for i, c in enumerate(f6x) if c == COLOR_MIN} == {23, 21, 31, 28},
      "23:59:59 gruen = C7+C5 (Zehner 5 = b101), D7+D4 (Einer 9 = b1001)")
check({i for i, c in enumerate(f6x) if c == COLOR_BASE4_BOTH} == {39, 36},
      "23:59:59 gelb = E7+E4 (9)")
for h in range(24):
    for m in range(0, 60, 7):
        for s in range(0, 60, 11):
            assert modes.get_frame(6, h, m, s) == ref_modus6(h, m, s), \
                f"Modus 6 weicht ab bei {h:02d}:{m:02d}:{s:02d}"
check(True, "Modus 6: komplette Referenz ueber 24 h (14976 Faelle)")

# ---------- G4: Modus 7 (EierUhr) ----------
# Stufe-4-Update (11.11.2026): Seit der Fall-Animation (docs/Erweiterungen_
# Anzeigemodi.md Kap. 5) ist die erste halbe Sekunde jeder Fallssekunde das
# durch die Taille wandernde Korn. Diese Stufe-3-Regression prueft darum den
# GELANDETEN Zustand (ms=400 >= 2 x EIERUHR_FALL_MS); die Animation selbst
# und der Zyklusstart-Ausschluss testet test_stufe4.py.

f7 = modes.get_frame(7, 14, 37, 30, 400)
check(frame_ok(f7), "Modus 7: Frame-Form")
check(sum(c == COLOR_GLAS for c in f7) == 25, "Umriss: 25 gedimmte LEDs")
check({i for i, c in enumerate(f7) if c == COLOR_BASE4_BOTH} ==
      {9, 17, 25, 14, 22, 30},
      "14:37:30 (elapsed 90 s): oben nur Zeile 1 (9,17,25), unten Zeile 6 "
      "(14,22,30) - Doku-Beispiel")
f7a = modes.get_frame(7, 14, 36, 0)
check({i for i, c in enumerate(f7a) if c == COLOR_BASE4_BOTH} ==
      {9, 17, 25, 10, 18, 26},
      "x:36:00 (elapsed 0): alle 6 Kugeln oben")
f7b = modes.get_frame(7, 14, 38, 30, 400)
check({i for i, c in enumerate(f7b) if c == COLOR_BASE4_BOTH} ==
      {25, 14, 22, 30, 13, 21},
      "x:38:30 (elapsed 150 s): 1 oben (25), 5 unten")
for m in range(60):
    for s in range(60):
        f = modes.get_frame(7, 14, m, s, 400)
        assert f == ref_modus7(m, s), f"Modus 7 weicht ab bei m={m} s={s}"
        assert sum(c == COLOR_BASE4_BOTH for c in f) <= 6, \
            f"Modus 7: mehr als 6 Kugeln bei m={m} s={s}"
        assert not (f[9] == COLOR_OFF and f[10] == COLOR_OFF
                    and f[17] == COLOR_OFF and f[18] == COLOR_OFF
                    and f[25] == COLOR_OFF and f[26] == COLOR_OFF), \
            f"Modus 7: 'alle 6 Kugeln unten' sichtbar bei m={m} s={s}"
check(True, "Modus 7: komplette Referenz ueber 60 min (3600 Faelle), "
            "max. 6 Kugeln, 'alle unten' nie sichtbar")
check(set(modes._EIERUHR_UMRISS) | set(modes._EIERUHR_OBEN)
      | set(modes._EIERUHR_UNTEN) | {4, 35, 36} == set(range(40)),
      "Umriss + 12 Kugelplaetze + A4/E3/E4 fuellen die Tafel lueckenlos")
dunkel = {i for i in range(40) if modes.get_frame(7, 14, 36, 0)[i] == COLOR_OFF}
check(dunkel == {4, 35, 36} | set(modes._EIERUHR_UNTEN),
      "x:36:00: unterer Raum leuchtet nicht (leer) + A4/E3/E4 dunkel")

# ---------- G5: Modus 8 (Sekunden-Serpentine, erweitert) ----------

f8 = modes.get_frame(8, 23, 57, 47)
check(frame_ok(f8), "Modus 8: Frame-Form")
check([i for i, c in enumerate(f8) if c == COLOR_ORANGE] == list(range(8)),
      "23:57:47: LEDs 0-7 orange (47 mod 40 = 7) - Doku-Beispiel")
check(all(f8[i] == (0, int(255 * SERPENTINE_DIM_FAKTOR), 0)
          for i in range(8, 40)),
      "23:57:47: LEDs 8-39 gedimmt gruen stehen")
f8a = modes.get_frame(8, 10, 0, 0)
check([i for i, c in enumerate(f8a) if c == COLOR_MIN] == [0]
      and sum(c != COLOR_OFF for c in f8a) == 1,
      "Sekunde 0: nur LED 0 gruen")
f8b = modes.get_frame(8, 10, 0, 39)
check(all(c == COLOR_MIN for c in f8b), "Sekunde 39: alle 40 gruen")
f8c = modes.get_frame(8, 10, 2, 40)
check(f8c[0] == COLOR_ORANGE and
      all(f8c[i] == (0, int(255 * SERPENTINE_DIM_FAKTOR), 0)
          for i in range(1, 40)),
      "Sekunde 40: Runde 1 gedimmt, LED 0 orange uebermalt")
f8d = modes.get_frame(8, 10, 1, 59)
check([i for i, c in enumerate(f8d) if c == COLOR_ORANGE] ==
      list(range(20)), "Sekunde 59: LEDs 0-19 orange")
for s in range(60):
    assert modes.get_frame(8, 12, 34, s) == ref_modus8(s), \
        f"Modus 8 weicht ab bei s={s}"
check(True, "Modus 8: komplette Referenz ueber 60 s")

# ---------- G6: Regression Stufe 1+2 ----------

for modus in (1, 2, 3, 4):
    for (h, m, s) in ((0, 0, 0), (12, 0, 0), (13, 32, 5), (14, 35, 49),
                      (23, 59, 59)):
        check(frame_ok(modes.get_frame(modus, h, m, s)),
              f"Regression Modus {modus} bei {h}:{m}:{s}")
f3 = modes.get_frame(3, 14, 35, 49)
check({i for i, c in enumerate(f3) if c == COLOR_HOURS} == {4, 5, 6},
      "Regression Modus 3: 14 h rot = A4+A5+A6")
check({i for i, c in enumerate(f3) if c == COLOR_MIN} == {18, 22, 23},
      "Regression Modus 3: 35 min gruen = C2+C6+C7")
check({i for i, c in enumerate(f3) if c == COLOR_BASE4_BOTH} == {34, 35, 39},
      "Regression Modus 3: 49 s gelb = E2+E3+E7")
f4 = modes.get_frame(4, 14, 35, 0)
check(f4[2 * 8 + 7] == COLOR_FIELD, "Regression Modus 4: Sekundenpunkt C7")

print(f"Alle {PASS} Checks bestanden (Stufe 3).")