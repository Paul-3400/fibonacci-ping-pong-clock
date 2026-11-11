#!/usr/bin/env python3
# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Fibonacci Ping-Pong-Ball-Uhr – Hauptprogramm
(5×8 Schnecke, 6 Taster).

Erweiterung Anzeige-Modi (10.11.2026, Stufe 1 –
docs/Erweiterungen_Anzeigemodi.md):
- Moduswahl über T1–T5 (Shift T6 = Platz 6–10); Registry in modes.py.
  Platz 1 (Fibonacci) und 2 (Base4) laufen durch die neue Schnittstelle
  (modes.get_frame -> display.show_frame); Platz 3–10 folgen in Stufe 2–4.
- Langdruck T2–T5 = Zeitverstellung (buttons.py, gpiozero hold_time).
- TM1637: kurzes Feedback bei Modus/Shift/Zeitverstellung
  ("M n", "- n", "SHIFT", "1MIN", "5MIN", "1STD", "NORM"), sonst HH:MM:SS.
- Shift (T6) endet automatisch nach SHIFT_TIMEOUT_SEC (buttons.poll()).
- Helligkeit (11.11.2026, docs/Helligkeit.md): Zielwert kommt aus
  helligkeit.py (persistente Datei, Justage ueber Langdruck T1 + T2/T3);
  die Boot-Rampe (Fallstrick 29) faehrt weiterhin stufenweise hoch,
  spaetere Aenderungen (manuelle Justage) setzen sofort um.
- Stufe 4 (11.11.2026, docs/Erweiterungen_Anzeigemodi.md): Millisekunden-
  genaue Zeit (ntp_time.get_local_time_precise) fuer die EierUhr-Fall-
  Animation (Modus 7) und die Pong-Uhr (Modus 10). Modi mit Untersekunden-
  Takt setzen ihr Loop-Intervall selbst ("frame_sec" in der Registry,
  FRAME_FAST_SEC), alle anderen bleiben beim 1-s-Raster.
"""
import time
import signal
import sys

from config import *
from modes import MODES, get_frame, get_tick
from buttons import ButtonController
from display import strip, show_frame, clear_all
from tm1637_display import show_clock, show_text, clear_display
from ntp_time import sync_ntp, get_local_time_precise, needs_resync
import helligkeit

running = True
state = {"mode": 1, "shift": False, "offset": 0, "feedback": None}

def on_event(mode_id, shift, offset_sec, feedback):
    """Callback des ButtonControllers – aktualisiert den Zustand."""
    state["mode"] = mode_id
    state["shift"] = shift
    state["offset"] = offset_sec
    if feedback is not None:
        state["feedback"] = feedback

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
    print("Anzeige-Modus 1: " + MODES[1]["name"] + " (Start nach Boot)")

    # Taster: Moduswahl T1-T5, Shift T6, Langdruck-Zeitverstellung
    buttons = ButtonController(on_event)

    # Erste NTP-Synchronisation
    print("Synchronisiere NTP...")
    if not sync_ntp():
        print("WARNUNG: NTP-Sync fehlgeschlagen – laufe mit Systemzeit.")

    last_display_time = ""
    last_raster = None    # was zuletzt auf der Tafel stand: (modus, tick)
    last_log = None       # (modus, h, m) - Log max. 1 Zeile pro Minute
    feedback_until = 0.0  # bis dahin steht Feedback auf dem TM1637

    # Soft-Start: Helligkeit langsam hochfahren - bei Minuten 0-4 gehen
    # sofort alle 40 LEDs an; mit Rampe kein Last-Schlag beim Start
    # (wichtig, wenn Pi und Tafel am selben Netzteil haengen - Fallstrick 29)
    brightness = SOFTSTART_BRIGHTNESS
    strip.setBrightness(brightness)
    hell_rampe_fertig = False   # Boot-Rampe laeuft bis zum Zielwert aus helligkeit.py

    while running:
        # Shift-Timeout pruefen (T6 schaltet nach SHIFT_TIMEOUT_SEC aus)
        buttons.poll()

        # Helligkeit: Boot-Rampe (Fallstrick 29) bis zum Zielwert aus
        # helligkeit.py; danach folgen manuelle Justage-Aenderungen sofort
        soll_hell = helligkeit.ziel_raw()
        if brightness != soll_hell:
            manuelle_aenderung = hell_rampe_fertig
            if not hell_rampe_fertig:
                brightness = min(soll_hell, brightness + SOFTSTART_STEP)
            else:
                brightness = soll_hell          # Justage: sofort umsetzen
            strip.setBrightness(brightness)
            strip.show()
            if brightness == soll_hell:
                hell_rampe_fertig = True
            if manuelle_aenderung:
                print(f"Helligkeit: {helligkeit.lese_prozent()} % "
                      f"(Rohwert {brightness} von 255)")

        # NTP gelegentlich resynchronisieren
        if needs_resync(NTP_SYNC_INTERVAL_MIN):
            sync_ntp()

        h, m, s, ms = get_local_time_precise(state["offset"])

        # --- TM1637: Feedback (Modus/Shift/Zeit) hat kurz Vorrang ---
        if state["feedback"] is not None:
            show_text(state["feedback"])
            feedback_until = time.monotonic() + TM1637_FEEDBACK_SEC
            state["feedback"] = None
        current_display = f"{h:02d}{m:02d}{s:02d}"
        if time.monotonic() < feedback_until:
            last_display_time = ""   # nach Feedback sofort wieder Uhrzeit zeigen
        elif current_display != last_display_time:
            show_clock(h, m, s)
            last_display_time = current_display

        # --- Tafel: nur neu zeichnen, wenn sich Modus oder Takt aendert ---
        # Stufe 4: ms-Genauigkeit - der Takt der EierUhr enthaelt die
        # Animationsphase (Korn C3 -> C4), der des Pong den Ballframe.
        tick = get_tick(state["mode"], h, m, s, ms)
        if tick is not None and last_raster != (state["mode"], tick):
            frame = get_frame(state["mode"], h, m, s, ms)
            if frame is not None:
                show_frame(frame)
                last_raster = (state["mode"], tick)
                log_key = (state["mode"], h, m)
                if log_key != last_log:   # Modus 3/4 rendern sekündlich, Log nur je Minute
                    print(f"Modus {state['mode']} ({MODES[state['mode']]['name']}): "
                          f"{h:02d}:{m:02d}:{s:02d}")
                    last_log = log_key

        # Kurze Pause: Modi mit Untersekunden-Takt (EierUhr-Fall-Animation,
        # Pong) holen sich ihr Loop-Intervall aus der Registry (frame_sec),
        # alle anderen laufen im 1-s-Raster weiter
        sleep_sec = MODES.get(state["mode"], {}).get("frame_sec") \
            or UPDATE_INTERVAL_SEC
        time.sleep(sleep_sec)

if __name__ == "__main__":
    main()
