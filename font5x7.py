# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Erweiterung Anzeige-Modi (Stufe 2)
"""5x7-Ziffernfont fuer die Anzeige-Modi der Erweiterung.

Modus 4 (grosse statische Ziffern) und spaeter Modus 7 (Laufschrift,
Stufe 4) nutzen diese Glyphen. Jedes Zeichen besteht aus 5 Spaltenbytes,
Bit 0 = oberste Zeile (klassischer 5x7-Standardfont wie beim HD44780 /
Arduino; die Glyphenmuster sind gemeinfrei und seit Jahrzehnten in
unzaehligen Open-Source-Projekten ueblich).

glyph(ch) liefert das 5-Byte-Tupel eines Zeichens;
unbekannte Zeichen sind leer (alles 0).
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


def glyph(ch):
    """Liefert die 5 Spaltenbytes des Zeichens (leer bei unbekanntem Zeichen)."""
    return FONT5x7.get(ch, (0, 0, 0, 0, 0))