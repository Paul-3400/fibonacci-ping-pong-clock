# 🎛️ Wokwi-Demo – Fibonacci Ping-Pong-Ball-Uhr mit 5 Tastern

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 18.10.2026

Demo-Variante des [Wokwi-Prototyps](../wokwi/) für Demonstrationen: gleiche Uhr
(40 NeoPixel im 8×5-Raster, TM1637, NTP), zusätzlich **5 Taster** zum Erklären
und Ausprobieren der Fibonacci-Codierung.

## Die fünf Taster

| Taster | Pin (XIAO) | Funktion |
|---|---|---|
| **T1** | D0 = GPIO1 | **Feld-Durchschaltung:** wieder drücken → A → B → C → D → E → A … Das gewählte Feld leuchtet weiss, TM1637 zeigt Buchstabe + Wert (z. B. `C 2`) |
| **T2** | D1 = GPIO2 | **Handbetrieb: +1 Minute** |
| **T3** | D6 = GPIO43 | **Handbetrieb: +5 Minuten** |
| **T4** | D7 = GPIO44 | **Handbetrieb: +1 Stunde** |
| **T5** | D8 = GPIO7 | **Normalbetrieb:** Offset auf 0, NTP-Zeit, Fibonacci-Anzeige |

## Betriebsarten

- **Normalbetrieb** (Start): NTP-Zeit, Raster zeigt die Zufallszerlegung, TM1637 zeigt HH:MM.
- **Handbetrieb** (T2–T4): verschiebt die Uhrzeit als **Offset** zur NTP-Zeit – die Uhr
  läuft dabei ganz normal weiter. Ideal, um beliebige Zeiten einzustellen und die
  Fibonacci-Zerlegung zu erklären. T5 setzt den Offset zurück.
- **Feld-Modus** (T1): zeigt die Feldgeometrie – jedes Feld einzeln mit Wert und Ball-Anzahl.
- Ohne NTP-Sync läuft eine virtuelle Uhr ab 12:00:00 (Handbetrieb funktioniert trotzdem).

## Demo-Szenarien

1. **Feld-Geometrie zeigen:** T1 fünfmal drücken – Felder A–E mit Wert auf dem TM1637.
2. **Ablesen üben (Beispiel 08:10):** mit T4 von der Startzeit auf 8 Uhr stellen, mit T3
   auf 10 Minuten – leuchten muss: A+B rot, C grün (Stunde 5+3, Minute 2×5).
3. **Zufallszerlegung zeigen:** mit T3 fünf Minuten weiter – das Muster wechselt,
   obwohl dieselbe Uhrzeit-Klasse (gleiches 5-Minuten-Fenster) kaum variiert;
   bei jedem neuen 5-Minuten-Fenster wird neu gewürfelt.
4. **Zurück zum Echtbetrieb:** T5.

## Verdrahtung

- LED-Kette, TM1637 und Farbschema identisch zum [Prototyp](../wokwi/) (siehe dort).
- **Taster:** Signal auf `1.l`, GND als Daisy-Chain `2.r → 2.l` von Taste zu Taste;
  im Sketch `INPUT_PULLUP`, gedrückt = LOW. Taster-Drähte **violett**.

## Dateien

| Datei | Inhalt |
|---|---|
| `sketch.ino` | Demo-Firmware: 3 Betriebsarten, Taster-Entprellung, Offset-basierter Handbetrieb |
| `diagram.json` | Prototyp-Aufbau + 5 Taster mit Beschriftung |
| `libraries.txt` | `Adafruit NeoPixel`, `TM1637` |

*Hinweis: Auch hier gilt – TM1637 im Sim nur 4-stellig (HH:MM); Ziel-Hardware bleibt 6-stellig.*
