#!/usr/bin/env python3
# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 11.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Stub-Test Helligkeits-Justage
"""Stub-Tests der Helligkeits-Justage (Phase 1, manuell) - ohne Hardware.

helligkeit.py ist reines Python und wird direkt getestet; buttons.py
laeuft mit einer Fake-gpiozero-Button-Klasse (Handler werden direkt
aufgerufen, wie es gpiozero tun wuerde). Aufruf: python3 test_helligkeit.py
"""
import io
import os
import re
import sys
import types

# --- Fake-gpiozero VOR dem Import von buttons bereitstellen ---
class FakeButton:
    def __init__(self, pin, bounce_time=None, hold_time=None,
                 hold_repeat=False):
        self.pin = pin
        self.hold_time = hold_time
        self.hold_repeat = hold_repeat
        self.when_pressed = None
        self.when_held = None
        self.when_released = None

_fake = types.ModuleType("gpiozero")
_fake.Button = FakeButton
sys.modules["gpiozero"] = _fake

import buttons                       # noqa: E402 (Absicht: nach Fake-Modul)
import helligkeit                   # noqa: E402
from config import (HELL_SCHRITT_PCT, HELL_MIN_PCT, HELL_MAX_PCT,  # noqa
                    HELL_DEFAULT_PCT, HELL_TIMEOUT_SEC)

PASS = 0


def check(bedingung, text):
    global PASS
    assert bedingung, "FEHLER: " + text
    PASS += 1
    print("  ok -", text)


# Test-Datei ins /tmp (nicht ins Projektverzeichnis)
TEST_DATEI = "/tmp/test_helligkeit_wert.txt"
helligkeit._DATEI = TEST_DATEI
if os.path.exists(TEST_DATEI):
    os.remove(TEST_DATEI)

print("G1: helligkeit.py")
check(helligkeit.prozent_raw(40) == 102, "40 % -> 102 (wie bisher LED_BRIGHTNESS)")
check(helligkeit.prozent_raw(5) == 12, "5 % -> 12")
check(helligkeit.prozent_raw(100) == 255, "100 % -> 255")
check(helligkeit.prozent_raw(50) == 127, "50 % -> 127")
check(helligkeit.prozent_raw(0) == 0, "0 % -> 0")
check(isinstance(helligkeit.prozent_raw(40), int), "Rohwert int (Fallstrick 27)")
check(helligkeit.lese_prozent() == HELL_DEFAULT_PCT, "ohne Datei: Default 40 %")
helligkeit.schreibe_prozent(60)
check(helligkeit.lese_prozent() == 60, "schreiben/lesen Roundtrip")
check(helligkeit.ziel_raw() == helligkeit.prozent_raw(60), "ziel_raw konsistent")
check(helligkeit.anpassen(-HELL_SCHRITT_PCT) == 55, "anpassen -5 -> 55")
check(helligkeit.anpassen(HELL_SCHRITT_PCT * 100) == 100, "anpassen klemmt bei 100")
helligkeit.schreibe_prozent(7)
check(helligkeit.anpassen(-HELL_SCHRITT_PCT) == HELL_MIN_PCT, "anpassen klemmt bei 5")
with io.open(TEST_DATEI, "w", encoding="utf-8") as f:
    f.write("abc")
check(helligkeit.lese_prozent() == HELL_DEFAULT_PCT, "Muell-Datei -> Default 40")
with io.open(TEST_DATEI, "w", encoding="utf-8") as f:
    f.write("150")
check(helligkeit.lese_prozent() == HELL_DEFAULT_PCT, "Wert 150 ausserhalb -> Default 40")

print("G2: buttons.py (Fake-gpiozero)")
EREIGNISSE = []


def on_event(mode_id, shift, offset_sec, feedback):
    EREIGNISSE.append((mode_id, shift, offset_sec, feedback))


helligkeit.schreibe_prozent(40)
ctrl = buttons.ButtonController(on_event)
check(ctrl._taster[1].hold_time is not None, "T1 hat hold_time (Langdruck)")
check(ctrl._taster[1].hold_repeat is False, "T1 ohne hold_repeat (kein Toggle-Flattern)")


def taste(slot, aktion):
    btn = ctrl._taster[slot]
    if aktion == "kurz":
        btn.when_released()
    elif aktion == "lang":
        btn.when_held()


def letzte():
    return EREIGNISSE[-1] if EREIGNISSE else None


taste(1, "kurz")
check(letzte() == (1, False, 0, "M 1"), "T1 kurz ohne Justage: Modus 1, 'M 1'")
taste(1, "lang")
check(ctrl._hell is True, "T1 lang: Justage aktiv")
check(letzte()[3] == "br40", "Justage-Start zeigt 'br40'")
taste(2, "kurz")
check(letzte()[3] == "br35" and helligkeit.lese_prozent() == 35,
      "T2 kurz: -5 %, sofort gespeichert")
taste(3, "kurz")
check(letzte()[3] == "br40" and helligkeit.lese_prozent() == 40, "T3 kurz: +5 %")
taste(3, "lang"); taste(3, "lang"); taste(3, "lang")
check(letzte()[3] == "br55", "T3 lang x3 (wiederholend): 55 %")
check(all(e[2] == 0 for e in EREIGNISSE), "Justage: kein Zeit-Offset")
for _ in range(10):
    taste(2, "lang")
check(letzte()[3] == "br 5" and helligkeit.lese_prozent() == 5,
      "T2 lang x10: klemmt bei 5 %")
taste(2, "kurz")   # Loslassen nach dem Halten: _held[2] wird nur gepoppt
check(helligkeit.lese_prozent() == 5, "Loslassen nach Halten: kein Doppel-Schritt")
taste(3, "kurz")   # Loslassen des vorher gehaltenen T3: auch nur poppen
check(helligkeit.lese_prozent() == 5, "Loslassen T3 nach Halten: kein Doppel-Schritt")
n_vor = len(EREIGNISSE)
taste(4, "kurz"); taste(5, "kurz"); taste(4, "lang"); taste(5, "lang")
check(len(EREIGNISSE) == n_vor, "T4/T5 kurz und lang in der Justage: ignoriert")
check(letzte() == (1, False, 0, "br 5"), "kein Moduswechsel waehrend der Justage")
# --- Uhr VOR dem Shift-Druck patchen (korrigiert 11.11.2026): vorher stand
#     der Patch unter "Timeout" - _shift_since bekam dann die ECHTE monotonic-
#     Uhr, und ob poll() den Shift beendet, haengt von der Uptime der Test-
#     Maschine ab (>= 1000 s => Shift ueberlebt => am Ende "M 6" statt "M 1"). ---
jetzt = [1000.0]
buttons.monotonic = lambda: jetzt[0]
ctrl._shift_btn.when_pressed()
check(letzte()[1] is True, "Shift (T6) in der Justage moeglich")
taste(3, "kurz")
check(letzte()[3] == "br10", "T3 in der Justage trotz Shift: +5 %")

# --- Timeout mit gepatchter Uhr ---
taste(1, "lang")
check(ctrl._hell is False, "T1 lang (Toggle): Justage beendet")
taste(1, "lang")
check(letzte()[3] == "br10", "Justage-Neustart zeigt 'br10'")
jetzt[0] = 1000.0 + HELL_TIMEOUT_SEC + 0.1
ctrl.poll()
check(ctrl._hell is False, "Justage endet nach HELL_TIMEOUT_SEC automatisch")
taste(1, "lang")
jetzt[0] = 1000.0 + HELL_TIMEOUT_SEC - 1.0
taste(3, "kurz")            # Aktivitaet verlaengert das Timeout
jetzt[0] += HELL_TIMEOUT_SEC - 2.0    # 8 s spaeter: Justage muss noch leben
ctrl.poll()
check(ctrl._hell is True, "Aktivitaet haelt die Justage am Leben")

# --- Ende ueber T1 kurz: erstes Kurz poppt nur das _held des Langdrucks ---
taste(1, "kurz")
check(ctrl._hell is True, "Loslassen nach Start-Langdruck: Justage laeuft weiter")
taste(1, "kurz")
check(ctrl._hell is False, "T1 kurz: Justage beendet")

# --- Regression: normale Funktion wieder da ---
# (Shift wurde vorher berechtig vom Shift-Timeout beendet - nur Offset/Feedback pruefen)
taste(2, "lang")
check(letzte()[2] == 60 and letzte()[3] == "1MIN", "T2 lang nach Justage: wieder +1 min")
taste(5, "lang")
check(letzte()[2] == 0 and letzte()[3] == "NORM", "T5 lang: Normalbetrieb")
taste(1, "kurz")
check(letzte()[3] == "M 1", "T1 kurz ohne Justage: Moduswahl")

print("G3: Konfiguration & TM1637-Zeichensatz")
check(HELL_MIN_PCT < HELL_DEFAULT_PCT <= HELL_MAX_PCT, "5 < 40 <= 100")
check(HELL_TIMEOUT_SEC == 10, "Justage-Timeout 10 s wie Shift")
zeilen = {e[3] for e in EREIGNISSE if e[3]}
for text in zeilen:
    check(bool(re.match(r"^[A-Za-z0-9 \-*]{1,6}$", text)),
          "TM1637-darstellbar: %r" % text)

print("\nALLE %d CHECKS BESTANDEN" % PASS)
