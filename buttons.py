# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Taster-Steuerung: Moduswahl T1-T5, Shift (T6), Langdruck-Zeitverstellung.

Erweiterung Anzeige-Modi (10.11.2026, Stufe 1 - docs/Erweiterungen_Anzeigemodi.md):
- T1-T5 kurz: Anzeige-Modus 1-5 waehlen; mit aktivem Shift (T6) die
  Plaetze 6-10. Nicht implementierte Plaetze zeigen '- n' auf dem TM1637.
- T6 kurz: Shift an/aus (Toggle); Shift endet automatisch nach
  SHIFT_TIMEOUT_SEC (poll() im Haupt-Loop prueft das).
- T2-T5 lang (laenger als BTN_HOLD_SEC): +1 Minute / +5 Minuten /
  +1 Stunde / Normalbetrieb (Offset 0); gehaltene Taste wiederholt
  (gpiozero hold_time + hold_repeat).
- Die Feld-Durchschaltung (frueher T1) entfaellt als Betriebsmodus -
  anzeige_test.py deckt diese Funktion ab.

on_event(mode_id, shift, offset_sec, feedback) wird bei jeder Aenderung
aufgerufen (gpiozero ruft die Callbacks in einem Hintergrund-Thread).
feedback = kurzer Text fuer das TM1637 (None = nichts Neues). Zeichensatz
der TM1637-Library (Quellcode geprueft 10.11.2026): 0-9, a-z, A-Z,
Leerzeichen, '-' und '*'; alles andere wirft ValueError.
"""
from time import monotonic
from gpiozero import Button
from config import (BTN_FIELD_PIN, BTN_MIN_PIN, BTN_MIN5_PIN, BTN_HOUR_PIN,
                    BTN_NORM_PIN, BTN_MODE_PIN, BTN_BOUNCE_SEC, BTN_HOLD_SEC,
                    SHIFT_TIMEOUT_SEC)
from modes import is_available

class ButtonController:
    """
    Fragt T1-T6 ab und verwaltet Anzeige-Modus (1-10), Shift und Zeit-Offset.
    Nach dem Boot: Modus 1 (Fibonacci), Shift aus, Offset 0.
    """

    def __init__(self, on_event):
        self._notify = on_event
        self._mode = 1            # Modus 1 = Fibonacci (Start nach Boot)
        self._shift = False
        self._shift_since = None  # monotonic()-Zeit des Shift-Einschaltens
        self._offset_sec = 0
        self._held = {}           # Taster-Nummer -> True (Langdruck aktiv)

        # T1-T5: kurzer Druck = Moduswahl (im Loslosen ohne Langdruck),
        # langer Druck T2-T5 = Zeitverstellung (when_held, wiederholend)
        self._taster = {
            1: Button(BTN_FIELD_PIN, bounce_time=BTN_BOUNCE_SEC),
            2: Button(BTN_MIN_PIN,  bounce_time=BTN_BOUNCE_SEC,
                      hold_time=BTN_HOLD_SEC, hold_repeat=True),
            3: Button(BTN_MIN5_PIN, bounce_time=BTN_BOUNCE_SEC,
                      hold_time=BTN_HOLD_SEC, hold_repeat=True),
            4: Button(BTN_HOUR_PIN, bounce_time=BTN_BOUNCE_SEC,
                      hold_time=BTN_HOLD_SEC, hold_repeat=True),
            5: Button(BTN_NORM_PIN, bounce_time=BTN_BOUNCE_SEC,
                      hold_time=BTN_HOLD_SEC, hold_repeat=True),
        }
        self._taster[1].when_released = self._released(1)
        for slot, delta, text in ((2, 60, "1MIN"), (3, 300, "5MIN"),
                                  (4, 3600, "1STD")):
            self._taster[slot].when_held = self._long_adjust(slot, delta, text)
            self._taster[slot].when_released = self._released(slot)
        self._taster[5].when_held = self._long_normal
        self._taster[5].when_released = self._released(5)

        # Shift-Taster T6: Toggle an/aus; Timeout prueft poll()
        self._shift_btn = Button(BTN_MODE_PIN, bounce_time=BTN_BOUNCE_SEC)
        self._shift_btn.when_pressed = self._shift_pressed

    # --- Abfragen fuer den Haupt-Loop ---
    def poll(self):
        """Im Haupt-Loop aufrufen: beendet Shift nach SHIFT_TIMEOUT_SEC."""
        if self._shift and self._shift_since is not None:
            if monotonic() - self._shift_since >= SHIFT_TIMEOUT_SEC:
                self._shift = False
                self._shift_since = None
                self._emit("M " + str(self._mode))

    def _emit(self, feedback):
        self._notify(self._mode, self._shift, self._offset_sec, feedback)

    # --- Kurzer Druck: Moduswahl ---
    def _released(self, slot):
        def handler():
            if self._held.pop(slot, False):
                return   # war ein Langdruck - Zeitverstellung lief ueber when_held
            mode_id = slot + (5 if self._shift else 0)
            if is_available(mode_id):
                self._mode = mode_id
                self._emit("M " + str(mode_id))
            else:
                self._emit("- " + str(mode_id))   # Platz reserviert (Stufe 2-4)
        return handler

    # --- Langer Druck: Zeitverstellung ---
    def _long_adjust(self, slot, delta, text):
        def handler():
            self._held[slot] = True
            self._offset_sec += delta
            self._emit(text)
        return handler

    def _long_normal(self):
        """T5 lang: Normalbetrieb - Offset auf 0."""
        self._held[5] = True
        self._offset_sec = 0
        self._emit("NORM")

    # --- Shift (T6) ---
    def _shift_pressed(self):
        self._shift = not self._shift
        if self._shift:
            self._shift_since = monotonic()
            self._emit("SHIFT")
        else:
            self._shift_since = None
            self._emit("M " + str(self._mode))
