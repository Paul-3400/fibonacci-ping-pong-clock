# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Konfiguration der Fibonacci Ping-Pong-Ball-Uhr (5×8 Schnecken-Raster)."""

# --- NeoPixel ---
LED_PIN        = 18          # GPIO 18 (PWM0)
LED_COUNT      = 40          # 5×8 Bälle
LED_FREQ_HZ    = 800000      # WS2812-Standard
LED_DMA        = 10          # DMA-Kanal
LED_BRIGHTNESS = 102         # int 0-255 (rpi_ws281x: uint8_t, KEIN Float!); 102 entspricht ca. 40 % Helligkeit
LED_INVERT     = False
LED_CHANNEL    = 0
LED_STRIP_TYPE = 0x00081000  # ws.WS2811_STRIP_GRB (WS2812-Standard, GRB) - NICHT der Arduino-Wert!
SOFTSTART_BRIGHTNESS = 20    # Soft-Start: Start-Helligkeit (Schutz vor Last-Spitzen, Fallstrick 29)
SOFTSTART_STEP = 2           # Soft-Start: +2 pro Sekunde bis LED_BRIGHTNESS

# --- TM1637 ---
TM1637_CLK     = 23          # GPIO 23
TM1637_DIO     = 24          # GPIO 24
TM1637_BRIGHTNESS = 4        # 0–7

# --- Taster (gpiozero, gegen GND, interner Pull-Up) ---
# Erweiterung Anzeige-Modi (10.11.2026, docs/Erweiterungen_Anzeigemodi.md):
# T1-T5 KURZ = Anzeige-Modus 1-5 waehlen (mit Shift T6: Platz 6-10);
# T2-T5 LANGDRUCK = Zeitverstellung. Die alte Belegung (Feld-Durchschaltung,
# Handbetrieb kurz, Normalbetrieb kurz) ist damit abgeloest.
BTN_FIELD_PIN = 5            # T1: Modus 1 (Fibonacci) waehlen; Langdruck ohne Funktion
BTN_MIN_PIN   = 6            # T2: Modus 2 (Base4) waehlen; Langdruck +1 Minute
BTN_MIN5_PIN  = 12           # T3: Modus 3 (reserviert); Langdruck +5 Minuten
BTN_HOUR_PIN  = 13           # T4: Modus 4 (reserviert); Langdruck +1 Stunde
BTN_NORM_PIN  = 16           # T5: Modus 5 (reserviert); Langdruck = Normalbetrieb (Offset 0)
BTN_BOUNCE_SEC = 0.05        # Prellen abfangen
BTN_HOLD_SEC  = 1.0          # Langdruck-Schwelle (gpiozero hold_time); gehaltene Taste wiederholt
SHIFT_TIMEOUT_SEC = 10       # Shift (T6) schaltet nach 10 s automatisch aus
TM1637_FEEDBACK_SEC = 2      # so lange steht Modus-/Shift-Feedback auf dem TM1637

# --- Shift-Taster (T6: Shift an/aus, Toggle pro Druck) ---
# Erweiterung 10.11.2026: T6 war der Moduswechsel Fibonacci <-> Base4 -
# diese Auswahl laeuft jetzt ueber T2 (Modus 2); T6 ist der Shift fuer
# die Plaetze 6-10 (Erweiterung docs/Erweiterungen_Anzeigemodi.md, Kap. 3.2).
BTN_MODE_PIN = 26          # GPIO 26 (Pin 37), gegen GND; Shift-Toggle mit Timeout

# --- Farben (R, G, B) ---
COLOR_OFF    = (0,   0,   0)
COLOR_HOURS  = (255, 0,   0)   # rot
COLOR_MIN    = (0,   255, 0)   # grün
COLOR_BOTH   = (0,   0, 255)   # blau (Fibonacci: Stunde + Minute)
COLOR_FIELD  = (255, 255, 255) # weiss (Feld-Durchschaltung)
COLOR_BASE4_BOTH = (255, 255, 0) # gelb (Base4: Stunde + Minute)

# --- NTP ---
NTP_SERVER   = "ch.pool.ntp.org"
TIMEZONE     = "Europe/Zurich"

# --- Update ---
UPDATE_INTERVAL_SEC = 1       # Haupt-Loop 1 s: TM1637 zeigt Sekunden (Raster nur bei Änderung neu)
NTP_SYNC_INTERVAL_MIN = 30    # alle 30 min NTP neu synchronisieren
