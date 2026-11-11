# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 11.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Helligkeit der Tafel
"""Ziel-Helligkeit der 40 NeoPixel - der eine Ort, der sie definiert.

Phase 1 (11.11.2026, manuell): Prozent-Wert in HELL_DATEI (Projektordner),
Justage ueber Langdruck T1 + T2/T3 (siehe buttons.py); ueberlebt den
Reboot. Ohne/defekte Datei: HELL_DEFAULT_PCT (40 % = Rohwert 102, wie
bisher LED_BRIGHTNESS). Design: docs/Helligkeit.md.

Phase 2 (geplant): LDR/Lux-Sensor (Empfehlung BH1750, I2C) als Quelle -
AUTOMATIK mit Log-Kurve Lux->Prozent, Hysterese +-5 %, sanften
Uebergaengen; manuelle Justage schaltet auf MANUELL zurueck. Die
Schnittstelle bleibt gleich: ziel_raw() liefert die Ziel-Helligkeit.
"""
import io
import os

from config import (HELL_MIN_PCT, HELL_MAX_PCT, HELL_DEFAULT_PCT,
                    HELL_DATEI)

# Datei liegt neben diesem Modul im Projektordner - egal von wo der
# systemd-Dienst startet (WorkingDirectory ist nicht garantiert).
_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), HELL_DATEI)


def prozent_raw(prozent):
    """Prozent -> rpi_ws281x-Rohwert 0-255 (int, KEIN Float - Fallstrick 27).

    int(255 * pct / 100): 40 % -> 102, identisch mit dem frueheren
    festen LED_BRIGHTNESS - die Justage aendert also nichts am Startwert.
    """
    return max(0, min(255, int(255 * prozent / 100)))


def lese_prozent():
    """Aktuellen Prozent-Wert lesen; fehlt/defekt ist die Datei: Default.

    Ungueltige Werte (ausserhalb 5-100) fallen ebenfalls zurueck - eine
    kaputte Datei darf die Uhr nie ohne Anzeige starten lassen.
    """
    try:
        roh = io.open(_DATEI, encoding="utf-8").read().strip()
        wert = int(roh)
        if HELL_MIN_PCT <= wert <= HELL_MAX_PCT:
            return wert
    except (OSError, ValueError):
        pass
    return HELL_DEFAULT_PCT


def schreibe_prozent(prozent):
    """Prozent-Wert speichern (persistente Datei, eine ganze Zahl)."""
    assert HELL_MIN_PCT <= prozent <= HELL_MAX_PCT, "Prozent ausserhalb 5-100"
    with io.open(_DATEI, "w", encoding="utf-8") as f:
        f.write(str(prozent))


def anpassen(delta_prozent):
    """Wert um +/- delta aendern, auf 5-100 klemmen, speichern, zurueckgeben."""
    neu = max(HELL_MIN_PCT, min(HELL_MAX_PCT, lese_prozent() + delta_prozent))
    schreibe_prozent(neu)
    return neu


def ziel_raw():
    """Ziel-Helligkeit als rpi_ws281x-Rohwert (0-255) - fuer den Haupt-Loop.

    Phase 2: Hier springt spaeter die LDR-Automatik ein.
    """
    return prozent_raw(lese_prozent())
