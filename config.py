# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""Konfiguration der Fibonacci Ping-Pong-Ball-Uhr (5×8 Schnecken-Raster)."""

# --- NeoPixel ---
LED_PIN        = 18          # GPIO 18 (PWM0)
LED_COUNT      = 40          # 5×8 Bälle
LED_FREQ_HZ    = 800000      # WS2812-Standard
LED_DMA        = 10          # DMA-Kanal
LED_BRIGHTNESS = 0.4         # 0.0–1.0 (40 Bälle: nicht zu hell!)
LED_INVERT     = False
LED_CHANNEL    = 0
LED_STRIP_TYPE = 0x00081008  # NEO_GRB + NEO_KHZ800 (PRÜFEN!)

# --- TM1637 ---
TM1637_CLK     = 23          # GPIO 23
TM1637_DIO     = 24          # GPIO 24
TM1637_BRIGHTNESS = 4        # 0–7

# --- Taster (gpiozero, gegen GND, interner Pull-Up) ---
BTN_FIELD_PIN = 5            # T1: Felder A–E durchschalten
BTN_MIN_PIN   = 6            # T2: Handbetrieb +1 Minute
BTN_MIN5_PIN  = 12           # T3: Handbetrieb +5 Minuten
BTN_HOUR_PIN  = 13           # T4: Handbetrieb +1 Stunde
BTN_NORM_PIN  = 16           # T5: Normalbetrieb (Offset zurücksetzen)
BTN_BOUNCE_SEC = 0.05        # Prellen abfangen

# --- Modus-Taster (T6: Fibonacci <-> Base4, Toggle pro Druck) ---
BTN_MODE_PIN = 26          # GPIO 26 (Pin 37), gegen GND; jeder Druck = umschalten

# --- Farben (R, G, B) ---
COLOR_OFF    = (0,   0,   0)
COLOR_HOURS  = (255, 0,   0)   # rot
COLOR_MIN    = (0,   255, 0)   # grün
COLOR_BOTH   = (0,   0,   255) # blau (Fibonacci: Stunde + Minute)
COLOR_FIELD  = (255, 255, 255) # weiss (Feld-Durchschaltung)
COLOR_BASE4_BOTH = (255, 255, 0) # gelb (Base4: Stunde + Minute)

# --- NTP ---
NTP_SERVER   = "ch.pool.ntp.org"
TIMEZONE     = "Europe/Zurich"

# --- Update ---
UPDATE_INTERVAL_SEC = 1       # Haupt-Loop 1 s: TM1637 zeigt Sekunden (Raster nur bei Änderung neu)
NTP_SYNC_INTERVAL_MIN = 30    # alle 30 min NTP neu synchronisieren
