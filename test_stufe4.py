#!/usr/bin/env python3
# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 11.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Stub-Test Stufe 4
"""Stub-Tests der Stufe 4 gegen unabhaengige Referenzlogik.

Referenz: docs/Erweiterungen_Anzeigemodi.md Kap. 5 (Fall-Animation,
Modus 9 Analog, Modus 10 Pong). modes.py und ntp_time.py importieren nur
reines Python bzw. eine gefakte ntplib - der Test laeuft ohne Hardware:
python3 test_stufe4.py

Gruppen:
  G1  ntp_time.get_local_time_precise (Millisekunden, Offset, Fallback)
  G2  EierUhr-Fall-Animation (Modus 7: Phasen C3/C4, Zyklusstart, Invarianten)
  G3  Analog-Uhr (Modus 9: Positionstabelle, Zeiger, Referenzpunkte)
  G4  Pong-Uhr (Modus 10: Ballbahn, Schlaeger, Scoreboard)
  G5  Registry & Konfiguration (frame_sec, ms-Default, Konstanten)
"""
import sys
import types
from datetime import datetime, timedelta, timezone

# --- Fake-ntplib VOR dem Import von ntp_time (E402 bewusst, wie test_helligkeit) ---
_fake_ntplib = types.ModuleType("ntplib")


class _FakeNTPClient:
    def request(self, server, version=3, timeout=2):
        raise OSError("Stub-Test: kein Netzwerk")


_fake_ntplib.NTPClient = _FakeNTPClient
sys.modules["ntplib"] = _fake_ntplib

import modes                              # noqa: E402
import ntp_time                          # noqa: E402
import font5x7                           # noqa: E402
from config import (LED_COUNT, COLOR_OFF, COLOR_HOURS, COLOR_MIN,     # noqa: E402
                    COLOR_BASE4_BOTH, COLOR_FIELD, COLOR_GLAS,
                    COLOR_ANALOG_REF, EIERUHR_FALL_MS, PONG_FRAME_MS,
                    PONG_SCORE_SEC, PONG_SCORE_WECHSEL_MS, FRAME_FAST_SEC)

PASS = 0


def check(bedingung, text):
    global PASS
    assert bedingung, "FEHLER: " + text
    PASS += 1


def frame_ok(frame):
    """Grundcheck: 40 Farben, jede ein (R, G, B)-Tupel."""
    return (len(frame) == 40
            and all(isinstance(f, tuple) and len(f) == 3 for f in frame))


def gelb(frame):
    return {i for i, c in enumerate(frame) if c == COLOR_BASE4_BOTH}


# ============================================================
# G1: ntp_time.get_local_time_precise
# ============================================================
print("G1: ntp_time.get_local_time_precise")

# Zeitzone fuer den Test: Europe/Zurich (November = MEZ, UTC+1);
# ohne zoneinfo/tzdata greift der feste Offset - beide ergeben +1 h.
try:
    from zoneinfo import ZoneInfo
    _TZ = ZoneInfo("Europe/Zurich")
except Exception:
    _TZ = timezone(timedelta(hours=1))       # MEZ im November
ntp_time._tz = _TZ

# NTP-Referenz: 11.11.2026 13:37:30.750 UTC -> Zuerich (MEZ) 14:37:30.750
_EPOCH = datetime(2026, 11, 11, 13, 37, 30, 750000, tzinfo=timezone.utc).timestamp()
ntp_time._ntp_epoch = _EPOCH
ntp_time._last_sync = 510.0
_orig_zeitmodul = ntp_time.time_module


def _uhr(monotonic_wert):
    ntp_time.time_module = types.SimpleNamespace(monotonic=lambda: monotonic_wert)


_uhr(510.0)                                # Sync-Moment selbst (Delta 0)
check(ntp_time.get_local_time_precise() == (14, 37, 30, 750),
      "NTP-Pfad: 13:37:30.750 UTC -> Zuerich 14:37:30, ms 750")
_uhr(510.25)                               # +0.25 s: Sekunden-/ms-Rollover
check(ntp_time.get_local_time_precise() == (14, 37, 31, 0),
      "Sekunden-Rollover: .750 + .25 s -> naechste Sekunde, ms 0")
_uhr(510.999)
check(ntp_time.get_local_time_precise()[3] == 749,
      "ms-Berechnung: .750 + .999 s -> .749 im Folgeschritt")
_uhr(510.0)
check(ntp_time.get_local_time_precise(90) == (14, 39, 0, 750),
      "Handbetrieb-Offset +90 s wirkt (auch auf ms unveraendert)")
check(ntp_time.get_local_time(90) == ntp_time.get_local_time_precise(90)[:3],
      "get_local_time deckt sich mit get_local_time_precise (delegiert)")
_uhr(510.0)
f = ntp_time.get_local_time_precise()
check(len(f) == 4 and all(isinstance(x, int) for x in f) and 0 <= f[3] <= 999,
      "Rueckgabe: 4 ints, ms 0-999")

# Fallback vor dem ersten Sync: Systemzeit (mit Toleranz +-3 s)
ntp_time._ntp_epoch = None
ntp_time._last_sync = None
ntp_time.time_module = _orig_zeitmodul
t_a = datetime.now()
erg = ntp_time.get_local_time_precise()
t_b = datetime.now()
check(len(erg) == 4 and 0 <= erg[3] <= 999, "Fallback: 4 Werte, ms 0-999")
sek_lo = t_a.hour * 3600 + t_a.minute * 60 + t_a.second - 3
sek_hi = t_b.hour * 3600 + t_b.minute * 60 + t_b.second + 3
sek_erg = erg[0] * 3600 + erg[1] * 60 + erg[2]
check(sek_lo <= sek_erg <= sek_hi, "Fallback: Systemzeit innerhalb Toleranz")
ntp_time._ntp_epoch = _EPOCH               # fuer spaetere Gruppen restaurieren
ntp_time._last_sync = 510.0

# ============================================================
# G2: EierUhr-Fall-Animation (Modus 7)
# ============================================================
print("G2: EierUhr-Fall-Animation (Modus 7)")

_phase = modes._eieruhr_phase
check(_phase(36, 0, 0) == 0, "Zyklusstart x:36:00.000: kein Korn (kein Fall)")
check(_phase(36, 0, 299) == 0, "Zyklusstart +299 ms: immer noch kein Korn")
check(_phase(36, 29, 999) == 0, "kurz vor dem ersten Fall: keine Animation")
check(_phase(37, 30, 0) == 1, "Fallssekunde 90 s, ms 0: Korn auf C3 (Phase 1)")
check(_phase(37, 30, 149) == 1, "ms 149: noch Phase 1 (C3)")
check(_phase(37, 30, 150) == 2, "ms 150: Phase 2 (C4)")
check(_phase(37, 30, 299) == 2, "ms 299: noch Phase 2 (C4)")
check(_phase(37, 30, 300) == 0, "ms 300: gelandet (Phase 0)")
check(_phase(38, 30, 0) == 1, "fuenfte Fallssekunde (150 s): Korn faellt auch hier")
check(_phase(39, 0, 150) == 0, "neuer Zyklusstart x:39:00: kein Korn trotz ms 150")

f7 = modes.get_frame(7, 14, 37, 30, 0)     # elapsed 90 s, Kugel 3 faellt
check(frame_ok(f7), "Modus 7 Animations-Frame: Form")
check(gelb(f7) == set(modes._EIERUHR_OBEN[3:]) | {14, 22} | {19},
      "ms 0 (Phase 1): oben 3 Kugeln, unten erst 2, Korn auf C3 (LED 19)")
check(f7[19] == COLOR_BASE4_BOTH and f7[20] == COLOR_GLAS,
      "Phase 1: C3 gelb ueber dimmem Umriss, C4 bleibt Glas")
f7b = modes.get_frame(7, 14, 37, 30, 150)
check(gelb(f7b) == set(modes._EIERUHR_OBEN[3:]) | {14, 22} | {20},
      "ms 150 (Phase 2): Korn auf C4 (LED 20)")
check(f7b[19] == COLOR_GLAS and f7b[20] == COLOR_BASE4_BOTH,
      "Phase 2: nur C4 gelb, C3 wieder Glas")
check(modes.get_frame(7, 14, 37, 30, 299) == f7b,
      "ms 299: noch Phase 2 (gleicher Frame)")
f7c = modes.get_frame(7, 14, 37, 30, 300)
check(gelb(f7c) == set(modes._EIERUHR_OBEN[3:]) | {14, 22, 30},
      "ms 300 (Phase 0): Kugel unten gelandet (LED 30 dazu)")
check(f7c[19] == COLOR_GLAS and f7c[20] == COLOR_GLAS,
      "gelandet: Taille wieder reiner Umriss")
check(sum(c == COLOR_GLAS for c in f7c) == 25, "gelandet: 25 Umriss-LEDs")

f7s = modes.get_frame(7, 14, 36, 0, 0)     # Zyklusstart: Sprung zurueck nach oben
check(gelb(f7s) == set(modes._EIERUHR_OBEN), "Zyklusstart: alle 6 Kugeln oben")
check(f7s[19] == COLOR_GLAS and f7s[20] == COLOR_GLAS,
      "Zyklusstart: kein Korn in der Taille")

check(modes.get_tick(7, 14, 37, 30, 0) == (14, 37, 30, 1) and
      modes.get_tick(7, 14, 37, 30, 150) == (14, 37, 30, 2) and
      modes.get_tick(7, 14, 37, 30, 300) == (14, 37, 30, 0),
      "Tick enthaelt die Phase: main.py zeichnet alle 3 Phasen neu")
check(modes.get_tick(7, 14, 36, 0, 0) == (14, 36, 0, 0) and
      modes.get_tick(7, 14, 36, 0, 150) == (14, 36, 0, 0),
      "Zyklusstart: Phase bleibt 0 (kein unnuetzes Neuzeichnen)")

_max_gelb = 0
for m in range(60):
    for s in range(60):
        for ms in (0, 150, 300):
            f = modes.get_frame(7, 14, m, s, ms)
            g = gelb(f)
            assert len(g) == 6, \
                f"Modus 7: {len(g)} gelbe Kugeln/Koerner bei m={m} s={s} ms={ms}"
            assert not (19 in g and 20 in g), \
                f"Modus 7: Korn auf beiden Taille-LEDs bei m={m} s={s} ms={ms}"
            assert any(led in g for led in modes._EIERUHR_OBEN), \
                f"Modus 7: oberer Raum komplett leer bei m={m} s={s} ms={ms}"
            assert sum(c == COLOR_GLAS for c in f) in (24, 25), \
                f"Modus 7: Umriss-Zaehler kaputt bei m={m} s={s} ms={ms}"
            _max_gelb = max(_max_gelb, len(g))
check(True, "Invarianten ueber 60 min x 3 ms-Stichproben (10 800 Frames): "
            "immer genau 6 gelbe, nie beide Korn-LEDs, oben nie leer")

# ============================================================
# G3: Analog-Uhr (Modus 9)
# ============================================================
print("G3: Analog-Uhr (Modus 9)")

# Unabhaengige Positionstabelle (Notation Spalte+Zeile -> selbst gerechnet)
_REF_POS = {"12": "C0", "1": "D0", "2": "E1", "3": "E4", "4": "E5",
            "5": "D7", "6": "C7", "7": "B7", "8": "A5", "9": "A3",
            "10": "A1", "11": "B0"}


def _ref_led(notation):
    return "ABCDE".index(notation[0]) * 8 + int(notation[1:])


def _ref_analog_leds(h, m):
    """(LED Stunden, LED Minuten) unabhaengig aus der Notationstabelle."""
    stunde = h % 12 or 12
    minute = m // 5 or 12
    return _ref_led(_REF_POS[str(stunde)]), _ref_led(_REF_POS[str(minute)])


check(len(set(_ref_led(v) for v in _REF_POS.values())) == 12,
      "Referenz: 12 eindeutige LED-Positionen (Selbsttest der Tabelle)")

f9 = modes.get_frame(9, 14, 35, 49)        # Doku-Beispiel
check(frame_ok(f9), "Modus 9: Frame-Form")
led_h, led_m = _ref_analog_leds(14, 35)
check(led_h == 33 and led_m == 15,
      "Referenz 14:35: Stunde 2 -> E1 (33), Minute 7 -> B7 (15)")
check(f9[33] == COLOR_HOURS and f9[15] == COLOR_MIN,
      "14:35: Stundenzeiger rot auf E1, Minutenzeiger gruen auf B7")
check(f9[16] == COLOR_ANALOG_REF and f9[36] == COLOR_ANALOG_REF and
      f9[23] == COLOR_ANALOG_REF and f9[3] == COLOR_ANALOG_REF,
      "14:35: 12/3/6/9 schwach weiss als Referenz")
check(sum(c != COLOR_OFF for c in f9) == 6,
      "14:35: 4 Referenzpunkte + 2 Zeiger = 6 LEDs")

f9x = modes.get_frame(9, 12, 0, 0)         # beide Zeiger auf 12 -> gelb
check(f9x[16] == COLOR_BASE4_BOTH,
      "12:00: beide Zeiger auf C0 -> gelb (wie 'beide' in Base4)")
check(f9x[36] == COLOR_ANALOG_REF and f9x[23] == COLOR_ANALOG_REF and
      f9x[3] == COLOR_ANALOG_REF,
      "12:00: uebrige Referenzpunkte schwach weiss (C0 ist Zeiger)")
check(sum(c != COLOR_OFF for c in f9x) == 4,
      "12:00: 3 Referenzpunkte + 1 Doppelzeiger = 4 LEDs")
f9y = modes.get_frame(9, 0, 0, 0)
check(f9y == f9x, "00:00 zeigt wie 12:00 (12-h-Zaehlung)")
f9z = modes.get_frame(9, 6, 30, 0)         # beide auf 6 -> gelb
check(f9z[23] == COLOR_BASE4_BOTH, "06:30: beide Zeiger auf C7 -> gelb")

check(modes.get_tick(9, 14, 38, 49) == (14, 7),
      "Modus 9: 5-Minuten-Takt (14, 38 -> (14, 7))")
check(modes.get_tick(9, 14, 38, 49, 999) == (14, 7),
      "Modus 9: Takt ignoriert ms")

_alle_led = set(_ref_led(v) for v in _REF_POS.values())
for h in range(24):
    for m in range(0, 60, 5):
        f = modes.get_frame(9, h, m, 0)
        led_h, led_m = _ref_analog_leds(h, m)
        erwartet = {16, 36, 23, 3}          # Referenzpunkte
        if led_h == led_m:
            farben = {led_h: COLOR_BASE4_BOTH}
        else:
            farben = {led_h: COLOR_HOURS, led_m: COLOR_MIN}
        assert {i for i, c in enumerate(f) if c != COLOR_OFF} \
            == (erwartet | set(farben)), \
            f"Modus 9 weicht ab bei {h:02d}:{m:02d}"
        for led, farbe in farben.items():
            assert f[led] == farbe, \
                f"Modus 9: Zeigerfarbe falsch bei {h:02d}:{m:02d}"
        assert set(i for i, c in enumerate(f) if c == COLOR_ANALOG_REF) \
            <= _alle_led, \
            f"Modus 9: Referenz ausserhalb des Zifferblatts bei {h:02d}:{m:02d}"
check(True, "Modus 9: komplette Referenz ueber 24 h x 12 Positionen (288 Faelle)")

# ============================================================
# G4: Pong-Uhr (Modus 10)
# ============================================================
print("G4: Pong-Uhr (Modus 10)")


def _ref_welle(i, n):
    """Dreieckwelle 0..n, anders formuliert (Spiegelung um n)."""
    p = i % (2 * n)
    return p if p <= n else n - (p - n)


def _ref_bahn(frames):
    """Ballbahn per Simulation mit Richtungsumkehr (unabhaengig)."""
    x, y, dx, dy = 0, 0, 1, 1
    bahn = []
    for _ in range(frames):
        bahn.append((x, y))
        if not 0 <= x + dx <= 7:
            dx = -dx
        if not 0 <= y + dy <= 4:
            dy = -dy
        x, y = x + dx, y + dy
    return bahn


bahn = _ref_bahn(112)
check(all(modes._pong_ball(i) == bahn[i] for i in range(112)),
      "Ballbahn = unabhängige Simulation ueber 2 volle Zyklen (112 Frames)")
check(all(abs(bahn[i + 1][0] - bahn[i][0]) == 1 and
          abs(bahn[i + 1][1] - bahn[i][1]) == 1 for i in range(111)),
      "Ball fliegt strikt diagonal (je Frame 1 Schritt in x und y)")
check(any(p[1] == 0 for p in bahn) and any(p[1] == 4 for p in bahn),
      "Ball erreicht beide Banden (Spalte A und E: Abprallen oben/unten)")
check(bahn[56] == bahn[0], "Ballzyklus = 56 Frames (Doku: LCM 14/8)")

for idx in (0, 7, 13, 28, 42, 55):
    h, m, s, ms = 10, 4, 30, idx * PONG_FRAME_MS % 1000
    gesamt_ms = ((h * 60 + m) * 60 + s) * 1000 + ms
    fr = gesamt_ms // PONG_FRAME_MS
    f = modes.get_frame(10, h, m, s, ms)
    zeile, spalte = modes._pong_ball(fr)
    check(f[spalte * 8 + zeile] == COLOR_FIELD,
          f"Pong: Ball weiss an der berechneten Position (Frame {fr})")
    rot = {i for i, c in enumerate(f) if c == COLOR_HOURS}
    pk = max(0, min(3, spalte - 1))
    check(rot == {pk * 8, (pk + 1) * 8, pk * 8 + 7, (pk + 1) * 8 + 7},
          f"Pong: beide Schlaeger rot, 2 LEDs, folgen dem Ball (Frame {fr})")
    check(spalte in (pk, pk + 1), "Pong: Schlaeger erreicht den Ball immer")

f10 = modes.get_frame(10, 14, 35, 54, 0)   # Spiel, keine Score-Anzeige
check(frame_ok(f10), "Modus 10 Spiel-Frame: Form")
check(sum(c != COLOR_OFF for c in f10) == 5,
      "Spiel: genau 5 LEDs an (Ball + 2 Schlaeger mit je 2 LEDs)")
check(modes.get_frame(10, 14, 35, 54, 0) == modes.get_frame(10, 14, 35, 54, 0),
      "Pong: Bahn ist reine Funktion der Zeit (deterministisch, kein Zustand)")

# Scoreboard: unabhaengiger Mini-Font als Pixelmuster (Strings)
_MINI_STR = {
    '0': ("###", "#.#", "#.#", "#.#", "###"),
    '1': (" #.", "##.", " #.", " #.", "###"),
    '2': ("###", "..#", "###", "#..", "###"),
    '3': ("###", "..#", "###", "..#", "###"),
    '4': ("#.#", "#.#", "###", "..#", "..#"),
    '5': ("###", "#..", "###", "..#", "###"),
    '6': ("###", "#..", "###", "#.#", "###"),
    '7': ("###", "..#", "..#", "..#", "..#"),
    '8': ("###", "#.#", "###", "#.#", "###"),
    '9': ("###", "#.#", "###", "..#", "###"),
}
check(all(font5x7.mini_glyph(z)[dy] ==
          sum(1 << dx for dx, c in enumerate(_MINI_STR[z][dy]) if c == "#")
          for z in "0123456789" for dy in range(5)),
      "Mini-Font: Glyphen decken sich mit dem String-Muster (Kreuzcheck)")


def _ref_score_leds(zahl):
    """Erwartete Score-LEDs quer: Zeile 7 = links, Spalte A = oben."""
    leds = set()
    for pos, ch in enumerate(f"{zahl:02d}"):
        for dy in range(5):
            for dx in range(3):
                if _MINI_STR[ch][dy][dx] == "#":
                    leds.add(dy * 8 + (7 - (pos * 4 + dx)))
    return leds


fsc = modes.get_frame(10, 14, 35, 55, 0)   # Score-Fenster: erste 2500 ms = HH
check({i for i, c in enumerate(fsc) if c == COLOR_HOURS} == _ref_score_leds(14),
      "14:35:55.0: Score '14' rot quer (3x5-Font, Stunden)")
check(all(c != COLOR_FIELD for c in fsc) and
      all(c != COLOR_MIN for c in fsc),
      "Score-Fenster: kein Ball, keine Minuten-Anzeige")
fsc2 = modes.get_frame(10, 14, 35, 57, 500)   # zweite Haelfte = MM
check({i for i, c in enumerate(fsc2) if c == COLOR_MIN} == _ref_score_leds(35),
      "14:35:57.5: Score '35' gruen (Minuten)")
check(all(i % 8 != 0 for i, c in enumerate(fsc) if c != COLOR_OFF) and
      all(i % 8 != 0 for i, c in enumerate(fsc2) if c != COLOR_OFF),
      "Score: Zeile 0 bleibt frei (Breite 3+1+3 = 7 von 8)")

check(not modes._pong_score_fenster(54) and
      all(modes._pong_score_fenster(s) for s in (55, 57, 59)),
      f"Score-Fenster: letzte {PONG_SCORE_SEC} s jeder Minute")
f_none = modes.get_frame(10, 14, 35, 54, 999)
check(sum(c != COLOR_OFF for c in f_none) == 5,
      "54,999 s: noch Spiel (Fenster beginnt erst bei Sekunde 55)")

t1 = modes.get_tick(10, 14, 35, 54, 0)
gesamt_ms = ((14 * 60 + 35) * 60 + 54) * 1000
check(t1 == (14, 35, 54, "ball", (gesamt_ms // PONG_FRAME_MS) % 56),
      "Spiel-Tick: Ballframe im Schluessel (main.py zeichnet je Bahn Schritt)")
t2 = modes.get_tick(10, 14, 35, 54, 200)
check(t2 == (14, 35, 54, "ball", (gesamt_ms // PONG_FRAME_MS + 1) % 56) and
      t2 != t1, "naechster Ballframe +200 ms: Tick aendert sich")
check(modes.get_tick(10, 14, 35, 55, 0) == (14, 35, 55, "score", 0) and
      modes.get_tick(10, 14, 35, 57, 500) == (14, 35, 57, "score", 1),
      "Score-Tick: Phase 0 = Stunden, 1 = Minuten")

_pong_leds = 0
for s in range(60):
    for ms in (0, 100, 350):
        f = modes.get_frame(10, 14, 35, s, ms)
        an = [i for i, c in enumerate(f) if c != COLOR_OFF]
        assert all(0 <= i < 40 for i in an), f"Pong: LED ausserhalb 0-39 bei s={s}"
        if s < 55:
            weiss = sum(1 for c in f if c == COLOR_FIELD)
            rot = sum(1 for c in f if c == COLOR_HOURS)
            assert weiss == 1 and rot in (3, 4) and len(an) == rot + 1, \
                f"Pong: {len(an)} LEDs im Spiel bei s={s} (Ball auf/nahe Schlaeger moeglich)"
        else:
            assert len(an) == len(_ref_score_leds(14 if (s * 1000 + ms - 55000) < PONG_SCORE_WECHSEL_MS else 35)), \
                f"Pong: Score-LED-Anzahl falsch bei s={s} ms={ms}"
        _pong_leds += 1
check(True, "Pong: Invarianten ueber 60 s x 3 ms-Stichproben (180 Frames)")

# ============================================================
# G5: Registry & Konfiguration
# ============================================================
print("G5: Registry & Konfiguration")

check(all(modes.is_available(i) for i in range(1, 11)),
      "Alle Plaetze 1-10 verfuegbar (Stufe 4 abgeschlossen)")
check(modes.MODES[9]["name"] == "Analog-Uhr (Experiment)" and
      modes.MODES[10]["name"] == "Pong-Uhr", "Platz 9/10 heissen wie geplant")
check(modes.MODES[7]["frame_sec"] == FRAME_FAST_SEC and
      modes.MODES[10]["frame_sec"] == FRAME_FAST_SEC,
      "Modus 7 + 10: Loop-Intervall FRAME_FAST_SEC aus der Registry")
check(all("frame_sec" not in modes.MODES[i] for i in (1, 2, 3, 4, 5, 6, 8, 9)),
      "Alle anderen Modi: kein frame_sec (1-s-Raster bleibt)")
check(FRAME_FAST_SEC <= EIERUHR_FALL_MS / 1000,
      "Loop 0.1 s faengt beide Korn-Phasen (je 150 ms)")
check(FRAME_FAST_SEC <= PONG_FRAME_MS / 1000,
      "Loop 0.1 s faengt jeden Ball-Schritt (200 ms)")
check(EIERUHR_FALL_MS == 150 and PONG_FRAME_MS == 200 and
      PONG_SCORE_SEC == 5 and PONG_SCORE_WECHSEL_MS == 2500,
      "Konstanten wie dokumentiert (Doku Kap. 5 + config.py)")
check(modes.get_frame(7, 14, 37, 30) == modes.get_frame(7, 14, 37, 30, 0) and
      modes.get_frame(6, 14, 35, 49) == modes.get_frame(6, 14, 35, 49, 0),
      "ms-Default 0: alte 4-stellige Aufrufe aendern nichts (Modus 6 statt 1: "
      "Fibonacci waehlt zufaellig eine Darstellung, ist nie frame-deterministisch)")
check(modes.get_frame(11, 1, 2, 3, 4) is None and
      modes.get_tick(0, 1, 2, 3, 4) is None,
      "unbekannte Modus-IDs: None (mit ms-Signatur)")

# Regression: Modi 1-8 unveraendert (Stichproben, volle Regression: test_stufe3)
for modus in range(1, 9):
    for (h, m, s) in ((0, 0, 0), (13, 32, 5), (14, 37, 30), (23, 59, 59)):
        if modus == 7 and s == 30:
            continue                       # Fallsekunde: Animation ab ms 0 (Stufe 4)
        check(frame_ok(modes.get_frame(modus, h, m, s)),
              f"Regression Modus {modus} bei {h}:{m}:{s}")
check(modes.get_frame(6, 13, 32, 5) == modes.get_frame(6, 13, 32, 5, 0),
      "Regression: BCD-Frame ms-unabhaengig")

print(f"\nALLE {PASS} CHECKS BESTANDEN (Stufe 4).")
