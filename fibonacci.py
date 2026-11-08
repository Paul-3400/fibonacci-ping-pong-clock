# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Fibonacci-Zerlegung mit Zufallsauswahl (portiert von Arduino setBits)."""
import random

FIB_VALUES = [1, 1, 2, 3, 5]  # Die fünf Fibonacci-Feldwerte

# Alle gültigen Kombinationen für Werte 1–12
# Jede Kombination ist eine Liste von Feld-Indizes (0–4)
# Feld 0 = Wert 1, Feld 1 = Wert 1, Feld 2 = Wert 2, Feld 3 = Wert 3, Feld 4 = Wert 5
COMBINATIONS = {
    1:  [[0], [1]],
    2:  [[2], [0, 1]],
    3:  [[3], [0, 2], [1, 2]],
    4:  [[0, 3], [1, 3], [0, 1, 2]],
    5:  [[4], [2, 3], [0, 1, 3]],
    6:  [[0, 4], [1, 4], [0, 2, 3], [1, 2, 3]],
    7:  [[2, 4], [0, 1, 4], [0, 1, 2, 3]],
    8:  [[3, 4], [0, 2, 4], [1, 2, 4]],
    9:  [[0, 3, 4], [1, 3, 4]],
    10: [[2, 3, 4], [0, 1, 3, 4]],
    11: [[0, 2, 3, 4], [1, 2, 3, 4]],
    12: [[0, 1, 2, 3, 4]],
}

def set_bits(value, offset):
    """
    Wählt per Zufall eine gültige Fibonacci-Kombination für value (1–12).
    Setzt das offset-Bit (0x01=Stunde, 0x02=Minute) in bits[].
    Gibt die Liste der gesetzten Feld-Indizes zurück.
    """
    value = max(1, min(12, value))
    combo = random.choice(COMBINATIONS[value])
    return combo

def get_field_assignment(hours, minutes):
    """
    Bestimmt für Stunde (1–12) und Minute (0–59) welche Felder
    leuchten und mit welcher Bedeutung.
    Gibt ein Dict zurück: {feld_index: 'hours'|'minutes'|'both'|'off'}
    """
    hours_12 = hours % 12
    if hours_12 == 0:
        hours_12 = 12
    min_units = minutes // 5  # 0–12 (5-Minuten-Schritte)
    if min_units == 0:
        min_units = 12  # 0 Minuten = 12 in Fibonacci-Darstellung

    field_bits = [0] * 5  # 0=off, 1=hours, 2=minutes, 3=both

    hour_fields = set_bits(hours_12, 0x01)
    min_fields  = set_bits(min_units, 0x02)

    for f in hour_fields:
        field_bits[f] |= 0x01
    for f in min_fields:
        field_bits[f] |= 0x02

    assignment = {}
    for i in range(5):
        if field_bits[i] == 0x01:
            assignment[i] = 'hours'
        elif field_bits[i] == 0x02:
            assignment[i] = 'minutes'
        elif field_bits[i] == 0x03:
            assignment[i] = 'both'
        else:
            assignment[i] = 'off'

    return assignment
