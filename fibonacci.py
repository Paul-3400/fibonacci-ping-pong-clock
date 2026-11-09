# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Fibonacci-Zerlegung mit Zufallsauswahl (portiert von Arduino setBits)."""
import random

FIB_VALUES = [1, 1, 2, 3, 5]  # die fünf Fibonacci-Werte (reine Doku)

# Alle gültigen Kombinationen für Werte 1–12
# Jede Kombination ist eine Liste von Feld-Indizes (0–4)
# WICHTIG (08.11.2026, Bugfix Fallstrick 28): Feld-Index = mapping.FELDER-Index
#   0 = A (Wert 5), 1 = B (Wert 3), 2 = C (Wert 2), 3 = D (Wert 1), 4 = E (Wert 1)
# Vorher nummerierte diese Tabelle 0–4 = [1,1,2,3,5] - das passte nicht zu
# mapping.FELDER, deshalb leuchteten die falschen Felder (Fallstrick 28).
COMBINATIONS = {
    1:  [[3], [4]],
    2:  [[2], [3, 4]],
    3:  [[1], [3, 2], [4, 2]],
    4:  [[3, 1], [4, 1], [3, 4, 2]],
    5:  [[0], [2, 1], [3, 4, 1]],
    6:  [[3, 0], [4, 0], [3, 2, 1], [4, 2, 1]],
    7:  [[2, 0], [3, 4, 0], [3, 4, 2, 1]],
    8:  [[1, 0], [3, 2, 0], [4, 2, 0]],
    9:  [[3, 1, 0], [4, 1, 0]],
    10: [[2, 1, 0], [3, 4, 1, 0]],
    11: [[3, 2, 1, 0], [4, 2, 1, 0]],
    12: [[3, 4, 2, 1, 0]],
}

def set_bits(value, offset):
    """
    Wählt per Zufall eine gültige Fibonacci-Kombination für value (1–12).
    (offset ist historisch aus dem Arduino-Port und wird nicht benutzt.)
    Gibt die Liste der gesetzten Feld-Indizes zurück (0–4 = A–E).
    """
    value = max(1, min(12, value))
    combo = random.choice(COMBINATIONS[value])
    return combo

def get_field_assignment(hours, minutes):
    """
    Bestimmt für Stunde (1–12) und Minute (0–59) welche Felder
    leuchten und mit welcher Bedeutung.
    Gibt ein Dict zurück: {feld_index: 'hours'|'minutes'|'both'|'off'}
    feld_index = mapping.FELDER-Index (0–4 = A–E), konsistent mit
    display.show_time()/show_field() und dem Konsole-Log.
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
