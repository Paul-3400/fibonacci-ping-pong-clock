# 🎛️ Wokwi-Demo – Fibonacci-Uhr im Schnecken-Layout (5 Taster)

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 20.10.2026

Demo-Variante der Uhr für Demonstrationszwecke: Das Raster steht **hochkant
(5 Spalten × 8 Zeilen)** als **sich öffnende Fibonacci-Schnecke** – die Anordnung
der [Nerdiy-Fibonacci-Uhr](https://www.nerdiy.de/fibonacciClock) bzw. des Originals.
Das grosse Feld oben dominiert wie ein Zifferblatt, und die Quadrate wachsen vom
Zentrum aus spiralförmig nach aussen – das Ablesen ist intuitiver, weil das Auge
der öffnenden Schnecke folgt. **Dieses Layout wird auch für die echte Uhr gebaut.**

> *Hinweis:* Dieser Ordner hiess bis zum 20.10.2026 `wokwidemo2` (mit einer
> älteren 8×5-Demo als `wokwidemo`). Nach der Entscheidung für das Schnecken-Layout
> wurde die alte 8×5-Demo gelöscht und diese Demo in `wokwidemo` umbenannt.

## Feld-Anordnung (Schnecke, vom Zentrum nach aussen öffnend: D → E → C → B → A)

| Feld | Wert | Bälle | Lage (5 Spalten × 8 Zeilen) | np-Indizes |
|---|---|---|---|---|
| **A** | 5 | 25 | Zeilen 0–4, Spalten 0–4 – **oben, volle Breite** (5×5-Quadrat) | np0–np24 |
| **B** | 3 | 9 | Zeilen 5–7, Spalten 0–2 – **unten links** (3×3-Quadrat) | np25–np27, np30–np32, np35–np37 |
| **C** | 2 | 4 | Zeilen 6–7, Spalten 3–4 – **unten rechts** (2×2-Quadrat) | np33, np34, np38, np39 |
| **D** | 1 | 1 | Zeile 5, Spalte 3 | np28 |
| **E** | 1 | 1 | Zeile 5, Spalte 4 | np29 |

```
A A A A A
A A A A A
A A A A A
A A A A A
A A A A A
B B B D E     ← D und E nebeneinander (Zentrum der Schnecke)
B B B C C     ← C direkt darunter
B B B C C
```

Mapping: `LED-Index = Zeile*5 + Spalte` – alle 40 Bälle, Summe der Werte 12.

**Zur Schnecke:** Die Quadrate wachsen vom Zentrum nach aussen in echter
Fibonacci-Manier: D (1) und E (1) liegen nebeneinander, C (2) schliesst direkt
darunter an, B (3) links daneben, A (5) schliesslich oben über die volle Breite.
Jedes Quadrat umschliesst damit die kleineren – klassische Fibonacci-Spirale.

## Die fünf Taster

| Taster | Pin (XIAO) | Funktion |
|---|---|---|
| **T1** | D0 = GPIO1 | **Feld-Durchschaltung:** A → B → C → D → E → A … (weiss, TM1637 zeigt Buchstabe + Wert) |
| **T2** | D1 = GPIO2 | **Handbetrieb: +1 Minute** |
| **T3** | D6 = GPIO43 | **Handbetrieb: +5 Minuten** |
| **T4** | D7 = GPIO44 | **Handbetrieb: +1 Stunde** |
| **T5** | D8 = GPIO7 | **Normalbetrieb:** Offset auf 0, NTP-Zeit, Fibonacci-Anzeige |

## Betriebsarten

- **Normalbetrieb** (Start): NTP-Zeit, Raster zeigt die Zufallszerlegung, TM1637 zeigt HH:MM.
- **Handbetrieb** (T2–T4): verschiebt die Uhrzeit als **Offset** zur NTP-Zeit – die Uhr
  läuft dabei weiter. T5 setzt den Offset zurück.
- **Feld-Modus** (T1): zeigt jedes Feld einzeln mit Wert und Ball-Anzahl – hier sieht
  man die Schnecken-Struktur besonders gut.
- Ohne NTP-Sync läuft eine virtuelle Uhr ab 12:00:00.

## Demo-Szenarien

1. **Schnecke zeigen:** T1 fünfmal drücken – vom Zentrum (D, E) über C und B zum
   grossen Feld A oben. TM1637 zeigt Buchstabe + Wert.
2. **Ablesen üben (Beispiel 08:10):** mit T4/T3 einstellen – A+B rot (Stunde 5+3), C grün (Minute 2×5).
3. **Zurück zum Echtbetrieb:** T5.

## Verdrahtung

- Farbschema wie im [Prototyp](../wokwi/): Daten grün, 5 V rot, GND schwarz,
  CLK orange, DIO blau, Taster violett.
- LED-Daisy-Chain: Zeile für Zeile (5er-Gruppen), `LED-Index = Zeile*5+Spalte`;
  Zeilenwechsel mit festem Versatz im Kanal zwischen den Zeilen (Kollisionscheck: 0).
- **Taster:** Signal auf `1.l`, GND als Daisy-Chain `2.r → 2.l`; `INPUT_PULLUP`, gedrückt = LOW.

## Dateien

| Datei | Inhalt |
|---|---|
| `sketch.ino` | Demo-Firmware: Schnecken-Mapping (C unter D/E), 5 Taster, Handbetrieb-Offset, Feld-Modus |
| `diagram.json` | Hochkantes 5×8-Raster mit 5 Tastern und Beschriftung |
| `libraries.txt` | `Adafruit NeoPixel`, `TM1637` |

*Hinweis: TM1637 im Sim nur 4-stellig (HH:MM); Ziel-Hardware bleibt 6-stellig (HH:MM:SS).*
