#!/usr/bin/env python3
# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Fibonacci Ping-Pong-Ball-Uhr – Hauptprogramm
(5×8 Schnecke, 6 Taster, Modus-Taster T6: Fibonacci <-> Base4)."""
import time
import signal
import sys

from config import *
from mapping import FELDER
from fibonacci import get_field_assignment
from base4 import get_ball_states
from buttons import ButtonController, MODE_NORMAL, MODE_MANUAL, MODE_FIELD
from display import strip, show_time, show_field, show_base4, clear_all
from tm1637_display import show_clock, show_field_text, clear_display
from ntp_time import sync_ntp, get_local_time, needs_resync

running = True
state = {"mode": MODE_NORMAL, "field": 0, "offset": 0}

def on_event(mode, field_idx, offset_sec):
    """Callback des ButtonControllers – aktualisiert den Zustand."""
    state["mode"] = mode
    state["field"] = field_idx
    state["offset"] = offset_sec

def signal_handler(sig, frame):
    global running
    running = False
    clear_all()
    clear_display()
    print("Uhr gestoppt.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    print("Fibonacci Ping-Pong-Ball-Uhr startet...")

    # Taster + Modus-Schalter
    buttons = ButtonController(on_event)

    # Erste NTP-Synchronisation
    print("Synchronisiere NTP...")
    if not sync_ntp():
        print("WARNUNG: NTP-Sync fehlgeschlagen – laufe mit Systemzeit.")

    last_display_time = ""
    last_raster = None  # was zuletzt im Raster stand

    while running:
        # NTP gelegentlich resynchronisieren
        if needs_resync(NTP_SYNC_INTERVAL_MIN):
            sync_ntp()

        # Feld-Modus ist eine Fibonacci-Funktion: bei Base4-Anzeige
        # (T6 umgeschaltet) automatisch verlassen
        if state["mode"] == MODE_FIELD and buttons.is_base4():
            state["mode"] = MODE_NORMAL

        if state["mode"] == MODE_FIELD:
            # --- Feld-Durchschaltung (Taster 1): Feld weiss zeigen ---
            if last_raster != ("field", state["field"]):
                wert, leds = FELDER[state["field"]]
                show_field(state["field"])
                show_field_text(state["field"], wert)
                last_raster = ("field", state["field"])
                print(f"Feldmodus: {'ABCDE'[state['field']]} (Wert {wert})")
        else:
            h, m, s = get_local_time(state["offset"])

            # --- TM1637: jede Sekunde aktualisieren ---
            current_display = f"{h:02d}{m:02d}{s:02d}"
            if current_display != last_display_time:
                show_clock(h, m, s)
                last_display_time = current_display

            if buttons.is_base4():
                # --- Base4-Modus: Update jede Minute ---
                if last_raster != ("base4", (h, m)):
                    show_base4(get_ball_states(h, m))
                    last_raster = ("base4", (h, m))
                    print(f"Base4: {h:02d}:{m:02d}")
            else:
                # --- Fibonacci-Modus: Update alle 5 Minuten ---
                slot = (h, m // 5)
                if last_raster != ("fib", slot):
                    assignment = get_field_assignment(h, m)
                    show_time(assignment)
                    last_raster = ("fib", slot)
                    print(f"Zeit: {h:02d}:{m:02d} – Felder: {assignment}")

        # Kurze Pause
        time.sleep(UPDATE_INTERVAL_SEC)

if __name__ == "__main__":
    main()
