# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Taster-Steuerung: Feld-Modus, Handbetrieb (Offset), Normalbetrieb,
Moduswechsel Fibonacci <-> Base4 (Modus-Taster T6, Toggle pro Druck)."""
from gpiozero import Button
from config import (BTN_FIELD_PIN, BTN_MIN_PIN, BTN_MIN5_PIN,
                    BTN_HOUR_PIN, BTN_NORM_PIN, BTN_MODE_PIN, BTN_BOUNCE_SEC)

MODE_NORMAL = "normal"   # NTP-Zeit, Fibonacci-Anzeige
MODE_MANUAL = "manual"   # Zeitversatz (Offset), Uhr läuft weiter
MODE_FIELD  = "field"    # Feld-Durchschaltung A-E

class ButtonController:
    """
    Fragt die Bedien-Taster T1–T5 und den Modus-Taster T6 ab (gpiozero,
    interne Pull-Ups, softwareseitig entprellt).

    Handbetrieb = Offset in Sekunden zur Systemzeit; Taster 5 setzt ihn auf 0.
    on_event(mode, field_idx, offset_sec) wird bei jedem Tasterdruck aufgerufen
    ( gpiozero ruft when_pressed in einem Hintergrund-Thread auf ).

    Der Modus-Taster T6 (GPIO 26, gegen GND) wechselt bei jedem Druck die
    Anzeige zwischen Fibonacci und Base4 (Software-Toggle, entprellt).
    Der Zustand steht in der Software – nach dem Boot startet die Uhr im
    Fibonacci-Modus. Abfrage im Hauptprogramm per is_base4().
    """

    def __init__(self, on_event):
        self._notify = on_event
        self._mode = MODE_NORMAL
        self._field = -1
        self._offset_sec = 0

        taster = {
            "field": Button(BTN_FIELD_PIN, bounce_time=BTN_BOUNCE_SEC),
            "min":   Button(BTN_MIN_PIN,   bounce_time=BTN_BOUNCE_SEC),
            "min5":  Button(BTN_MIN5_PIN,  bounce_time=BTN_BOUNCE_SEC),
            "hour":  Button(BTN_HOUR_PIN,  bounce_time=BTN_BOUNCE_SEC),
            "norm":  Button(BTN_NORM_PIN,  bounce_time=BTN_BOUNCE_SEC),
        }
        taster["field"].when_pressed = self._field_pressed
        taster["min"].when_pressed   = lambda: self._manual_pressed(60)
        taster["min5"].when_pressed  = lambda: self._manual_pressed(300)
        taster["hour"].when_pressed  = lambda: self._manual_pressed(3600)
        taster["norm"].when_pressed  = self._normal_pressed

        # Modus-Taster T6: jeder Druck wechselt Fibonacci <-> Base4;
        # Prellen über bounce_time abfangen (genau 1 Ereignis pro Druck)
        self._base4 = False   # Start nach Boot: Fibonacci-Modus
        self._mode_btn = Button(BTN_MODE_PIN, bounce_time=BTN_BOUNCE_SEC)
        self._mode_btn.when_pressed = self._mode_pressed

    def is_base4(self):
        """True = Base4-Anzeige aktiv (Software-Toggle via T6)."""
        return self._base4

    def _mode_pressed(self):
        """T6: Anzeige-Modus umschalten (Fibonacci <-> Base4)."""
        self._base4 = not self._base4
        self._emit()   # Haupt-Loop rendert im neuen Modus

    def _emit(self):
        self._notify(self._mode, self._field, self._offset_sec)

    def _field_pressed(self):
        """Taster 1: Felder A-E durchschalten (Fibonacci-Funktion)."""
        self._mode = MODE_FIELD
        self._field = (self._field + 1) % 5
        self._emit()

    def _manual_pressed(self, delta):
        """Taster 2/3/4: +1 Minute / +5 Minuten / +1 Stunde."""
        self._mode = MODE_MANUAL
        self._offset_sec += delta
        self._emit()

    def _normal_pressed(self):
        """Taster 5: Normalbetrieb – Offset auf 0."""
        self._mode = MODE_NORMAL
        self._offset_sec = 0
        self._emit()
