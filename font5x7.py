# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Erweiterung Anzeige-Modi (Stufe 2)
"""5x7-Ziffernfont fuer die Anzeige-Modi der Erweiterung.

Modus 4 (grosse statische Ziffern) nutzt die 5x7-Glyphen (5 Spaltenbytes,
Bit 0 = oberste Zeile; klassischer Standardfont wie beim HD44780 / Arduino,
gemeinfrei). Die Laufschrift (frueher fuer Platz 7 geplant, 10.11.2026 der
EierUhr gewichen) entfiel - die Glyphen blieben fuer Modus 4.

Stufe 4 (11.11.2026): Pong-Uhr (Modus 10) zeigt den Spielstand (Stunden
resp. Minuten) quer im 3x5-Mini-Font (3 Pixel breit, 5 Zeilen hoch):
zwei Ziffern + 1 Pixel Spalt = 7 von 8 Zeilen. mini_glyph(ch) liefert
5 Zeilenwerte (Bit 0 = links), unbekannte Zeichen sind leer.

glyph(ch)   -> 5 Spaltenbytes des 5x7-Fonts (Bit 0 = oben)
mini_glyph(ch) -> 5 Zeilenwerte des 3x5-Fonts (Bit 0 = links)
"""

FONT5x7 = {
    '0': (0x3E, 0x51, 0x49, 0x45, 0x3E),
    '1': (0x00, 0x42, 0x7F, 0x40, 0x00),
    '2': (0x42, 0x61, 0x51, 0x49, 0x46),
    '3': (0x21, 0x41, 0x45, 0x4B, 0x31),
    '4': (0x18, 0x14, 0x12, 0x7F, 0x10),
    '5': (0x27, 0x45, 0x45, 0x45, 0x39),
    '6': (0x3C, 0x4A, 0x49, 0x49, 0x30),
    '7': (0x01, 0x71, 0x09, 0x05, 0x03),
    '8': (0x36, 0x49, 0x49, 0x49, 0x36),
    '9': (0x06, 0x49, 0x49, 0x29, 0x1E),
    ':': (0x00, 0x36, 0x36, 0x00, 0x00),
}

assert all(len(v) == 5 for v in FONT5x7.values()), "Glyphen muessen 5 Spaltenbytes haben!"

# 3x5-Mini-Font (Stufe 4, 11.11.2026): Wert je Zeile = 3 Bit (Bit 0 = links)
# Kreuzgeprueft gegen unabhaengige String-Muster in test_stufe4.py (G4)
FONT3x5 = {
    '0': (0b111, 0b101, 0b101, 0b101, 0b111),
    '1': (0b010, 0b011, 0b010, 0b010, 0b111),
    '2': (0b111, 0b100, 0b111, 0b001, 0b111),
    '3': (0b111, 0b100, 0b111, 0b100, 0b111),
    '4': (0b101, 0b101, 0b111, 0b100, 0b100),
    '5': (0b111, 0b001, 0b111, 0b100, 0b111),
    '6': (0b111, 0b001, 0b111, 0b101, 0b111),
    '7': (0b111, 0b100, 0b100, 0b100, 0b100),
    '8': (0b111, 0b101, 0b111, 0b101, 0b111),
    '9': (0b111, 0b101, 0b111, 0b100, 0b111),
}

assert all(len(v) == 5 and 0 <= z <= 7 for v in FONT3x5.values() for z in v), \
    "Mini-Glyphen muessen 5 Zeilenwerte 0-7 haben!"
assert len(set(FONT3x5.values())) == 10, "Ziffern 0-9 muessen eindeutig sein!"


def glyph(ch):
    """Liefert die 5 Spaltenbytes des Zeichens (leer bei unbekanntem Zeichen)."""
    return FONT5x7.get(ch, (0, 0, 0, 0, 0))


def mini_glyph(ch):
    """Liefert die 5 Zeilenwerte des 3x5-Mini-Fonts (leer bei unbekanntem Zeichen)."""
    return FONT3x5.get(ch, (0, 0, 0, 0, 0))