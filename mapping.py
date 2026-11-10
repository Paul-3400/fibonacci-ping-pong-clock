# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Mapping: 40 physische LEDs → 5 logische Fibonacci-Felder (Schnecke)."""

# Spaltenweise Kette, LOGISCH: LED-Index = Spalte × 8 + Zeile (Spalte A = links)
# Logische Reihenfolge: A0–A7 → B0–B7 → C0–C7 → D0–D7 → E0–E7
# Raster hochkant: 5 Spalten (A–E) × 8 Zeilen (0–7)
# Achtung Fallstrick 33 (10.11.2026, am Gerät gemessen): Die physische
# Datenkette beginnt REAL bei Spalte E (rechts), nicht bei A – display.py
# spiegelt die Spalte beim Schreiben zentral (_PHYS_LED-Tabelle).
# Schnecke: D/E (Zeile 5, Spalten A/B) -> C (darunter) -> B (rechts) -> A (oben)

FELDER = [
    # (Wert, [LED-Indizes])
    (5, [s * 8 + z for s in range(5) for z in range(5)]),          # A: 25 LEDs (Spalten A–E, Zeilen 0–4)
    (3, [s * 8 + z for s in range(2, 5) for z in range(5, 8)]),    # B:  9 LEDs (Spalten C–E, Zeilen 5–7)
    (2, [s * 8 + z for s in range(0, 2) for z in range(6, 8)]),   # C:  4 LEDs (Spalten A–B, Zeilen 6–7)
    (1, [0 * 8 + 5]),                                              # D:  1 LED (A5 = LED 5)
    (1, [1 * 8 + 5]),                                              # E:  1 LED (B5 = LED 13)
]

# Verifikation beim Import
assert sum(len(f[1]) for f in FELDER) == 40, "LED-Anzahl stimmt nicht!"
assert sum(f[0] for f in FELDER) == 12, "Fibonacci-Summe stimmt nicht!"

# Base4-Matrix (2. Anzeige-Modus): 3x3-Block in Zeilen 0-2, Spalten B-D
# (Positionsindex 1-3, innerhalb von Feld A). Werte identisch zur
# 9-Baelle-Ping-Pong-Uhr. LED-Index = Spalte*8 + Zeile
BASE4_MATRIX = [
    # (Wert, LED-Index)
    (48, 1 * 8 + 0), (12, 2 * 8 + 0), ( 3, 3 * 8 + 0),
    (32, 1 * 8 + 1), ( 8, 2 * 8 + 1), ( 2, 3 * 8 + 1),
    (16, 1 * 8 + 2), ( 4, 2 * 8 + 2), ( 1, 3 * 8 + 2),
]
assert len(BASE4_MATRIX) == 9, "Base4-Matrix muss 9 Baelle haben!"
assert [w for w, _ in BASE4_MATRIX] == [48, 12, 3, 32, 8, 2, 16, 4, 1], \
    "Base4-Werte stimmen nicht mit der 9-Baelle-Uhr ueberein!"