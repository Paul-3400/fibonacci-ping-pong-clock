# Erweiterungen: Zehn Zeitdarstellungen auf dem 5×8-Raster

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026
Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
Status: **Planung / Überlegungen** (10.11.2026) – noch kein Code; alle Belegungen sind Vorschläge, bis wir sie einzeln abnicken.

## 1. Ziel

Die Uhr zeigt die Zeit heute über die fünf Fibonacci-Anzeigewerte 1, 1, 2, 3, 5 (Felder A–E, 5-Minuten-Schritte) und – über den Modus-Taster T6 – zusätzlich im Base4-Modus (3×3-Matrix, minutengenau). Die Tafel hat aber 40 einzeln adressierbare LEDs im Raster **5 Spalten × 8 Zeilen** – deutlich mehr Darstellungsfläche, als diese beiden Modi nutzen.

Ziel der Erweiterung:

- Das Raster **5×8 (hochkant)** resp. **8×5 (quer gelesen)** als vollwertige Zeit-Anzeige nutzen – zusätzlich zu den bestehenden Fibonacci-Anzeigewerten.
- **Zehn verschiedene Darstellungen**: Taster T1–T5 wählen fünf Modi direkt, Taster T6 wirkt als **Shift** und T6 + T1–T5 wählen fünf weitere.
- Fibonacci und Base4 **behalten zwei der zehn Plätze**; acht Modi kommen neu dazu.

Anstoss für die neuen Modi (Ideen von Paul, 10.11.2026):

1. **Binärzähler für Sekunden, Minuten, Stunden** – daraus werden zwei Varianten: drei parallele Binärzähler (Modus 3) und eine klassische Binär-BCD-Uhr (Modus 6).
2. **Zeit mit grossen, durchlaufenden Zahlen (5 breit, 8 hoch)** – daraus werden ebenfalls zwei Varianten: statisch wechselnde grosse Ziffern (Modus 4) und eine Laufschrift, die durchs Fenster zieht (Modus 7).

## 2. Ausgangslage und Konventionen

**Tafel (massgeblich, siehe Bauanleitung):** 5 Spalten (A–E) × 8 Zeilen (0–7), hochkant, öffnende Schnecke. LED-Index = Spalte × 8 + Zeile, Datenkette spaltenweise (IN an A0). Zeile 0 oben, Zeile 7 unten.

- **Hochkant (5×8):** 5 Positionen nebeneinander (Spalten A–E), 8 übereinander (Zeilen 0–7).
- **Quer gedacht (8×5):** Breite = 8 (Zeilen 0–7), Höhe = 5 (Spalten A–E) – für Modi, die «liegend» gelesen werden (Laufschrift, Pong).

**Bestehende Modi:** Fibonacci (Werte 1, 1, 2, 3, 5 auf den Feldern A–E; rot = Stunde, grün = Minute ×5, blau = beides, aus = nichts; Zufallszerlegung; 5-Minuten-Genauigkeit) und Base4 (3×3 in Zeilen 0–2, Spalten B–D; minutengenau; gelb statt blau für «beides»).

**Heutige Taster-Belegung** (wird durch die Erweiterung ersetzt bzw. erweitert, siehe Kap. 4):

| Taster | GPIO | Heutige Funktion |
|---|---|---|
| T1 | 5 | Felder A–E durchschalten (weiss) |
| T2 | 6 | Handbetrieb +1 Minute |
| T3 | 12 | Handbetrieb +5 Minuten |
| T4 | 13 | Handbetrieb +1 Stunde |
| T5 | 16 | Normalbetrieb (Offset auf 0) |
| T6 | 26 | Moduswechsel Fibonacci ↔ Base4 |

**Software-Stand (10.11.2026):** Module config, mapping, buttons, fibonacci, base4, display, tm1637_display, ntp_time, main; systemd-Regelbetrieb mit Soft-Start-Rampe; TM1637 zeigt HH:MM:SS.

## 3. Bedienkonzept

### 3.1 Die zehn Plätze

**Direkt (T1–T5) = Alltags-Modi. Shift (T6) + T1–T5 = Show- und Experimentier-Modi.**

| Platz | Tasten | Modus | Quelle | Auflösung |
|---|---|---|---|---|
| 1 | T1 | Fibonacci-Schnecke (bestehend) | Original (pchretien) | 5 min |
| 2 | T2 | Base4-Matrix (bestehend) | Schwesterprojekt | 1 min |
| 3 | T3 | Drei Binärzähler h/m/s | Idee «Binärzähler», Originalform | 1 s |
| 4 | T4 | Grosse Ziffern, statisch | Idee «grosse Zahlen», Variante A | 1 min |
| 5 | T5 | Tagesfortschritt-Balken | Vibe-Vorschlag | 36 min |
| 6 | Shift+T1 | Binär-BCD-Uhr | Idee «Binärzähler», Variante A | 1 min (1 s optional) |
| 7 | Shift+T2 | Durchlaufende grosse Zahlen (Laufschrift) | Idee «grosse Zahlen», Variante B | 1 min |
| 8 | Shift+T3 | Sekunden-Serpentine | Vibe-Vorschlag | 1 s |
| 9 | Shift+T4 | Grobe Analog-Uhr | Vibe-Vorschlag (Experiment) | 5 min |
| 10 | Shift+T5 | Pong-Uhr | Vibe-Vorschlag (Hommage) | 1 min + Animation |

Die Zuordnung der acht Neuen auf die Tasten ist ein Vorschlag – nach den ersten Demos kann sie frei getauscht werden, ohne dass sich an der Struktur etwas ändert (Modus-Nummer = fest, Taste = nur Auswahl).

### 3.2 Shift-Variante (T6)

| Kriterium | Variante «Toggle» (T6 drücken = Shift an/aus) | Variante «Halten» (T6 gedrückt halten + T1–T5) |
|---|---|---|
| Einhandbedienung | ja | nein (zwei Finger, kleiner Tastenabstand auf der Steuerbox) |
| Vergessener Zustand | möglich – Gegenmittel: Shift-Timeout (z. B. 10 s) + TM1637-Feedback | ausgeschlossen |
| gpiozero-Umsetzung | trivial (Software-Flag wie heute bei is_base4) | machbar (when_held + Zustandsabfrage), etwas mehr Logik |
| Nähe zum heutigen Verhalten | T6 ist heute ein Toggle (Fibonacci ↔ Base4) | neuartig |

**Empfehlung (Konfidenz mittel):** Toggle mit 10-s-Timeout und TM1637-Feedback. Begründung: Einhandbedienung, Konsistenz mit dem heutigen T6-Verhalten, und der Timeout schliesst den einzigen Nachteil (vergessener Shift) weitgehend.

**Boot-Verhalten (Vorschlag):** Shift aus, Modus = Fibonacci (Platz 1) – die Uhr startet also künftig genau wie heute. Alternativ könnte der letzte Modus in einer Datei gemerkt werden (offene Frage 6 in Kap. 8).

### 3.3 TM1637-Feedback beim Umschalten

Beim Moduswechsel zeigt das TM1637 für 1–2 s die Modus-Nummer (1–10, bei aktivem Shift mit «S» davor, z. B. «S 3»), danach wieder HH:MM:SS. Text-Kürzel (z. B. «FIB», «BCD») nur, wenn encode_string sie sauber darstellt – Zeichensatz der Library vorher prüfen. Die halbe Spiegelung des 6-stelligen Moduls bleibt unverändert durch _modul_segments() abgedeckt (Fallstrick 31).

## 4. Konflikt mit den heutigen Taster-Funktionen

T1–T5 haben heute Bedienfunktionen (Feld-Durchschaltung, Handbetrieb, Normalbetrieb), die durch die Moduswahl belegt werden. Varianten:

| Variante | Beschreibung | Beurteilung |
|---|---|---|
| A: Wegfallen | Zeitverstellung entfällt komplett | Einfachste Lösung; NTP + Fallstrick-30-Fix machen den Handbetrieb selten nötig. Nachteil: ohne Netz (Basteltisch, Demo) keine Korrektur möglich. |
| B: Langdruck | T2/T3/T4 kurz = Modus, lang gedrückt (über 1 s) = +1/+5 min/+1 h; T5 lang = Normalbetrieb | Alles bleibt erhalten; gpiozero kann das (hold_time, when_held, hold_repeat für schnelles Verstellen). Nachteil: Doppelbelegung, versehentliche Auslösung möglich. |
| C: Setup-Modus | z. B. T6 beim Boot gedrückt halten = Setup-Modus mit alter Belegung | Sauber getrennt; Nachteil: nur beim Boot erreichbar, versteckt. |

**Empfehlung (Konfidenz mittel):** Variante B für die Zeitverstellung – der Handbetrieb ist seit dem NTP-Fix nur noch Reserve, aber genau in Reservesituationen (kein Netz) braucht man ihn. Die **Feld-Durchschaltung (T1)** entfällt als Betriebsmodus: ihre Erklär- und Prüffunktion deckt anzeige_test.py bereits ab.

## 5. Die zehn Modi im Detail

Alle Beispiele zeigen **14:35:49**. Positionsnotation: Spalte A–E + Zeile 0–7 (z. B. «E7» = LED 39).

### Modus 1 (T1) – Fibonacci-Schnecke [bestehend]

Unverändert: fünf Felder A–E mit den Werten 1, 1, 2, 3, 5, Zufallszerlegung, 5-Minuten-Schritte. Beispiel 14:35: Stunden 2, Minuten 35 = 7 Fünfer-Einheiten; jede Zerlegung wird per Zufall gewählt, Farben rot/grün/blau. Kein Änderungsaufwand (Wrapper auf get_field_assignment).

### Modus 2 (T2) – Base4-Matrix [bestehend]

Unverändert: 3×3-Matrix in Zeilen 0–2, Spalten B–D, minutengenau, rot/grün/gelb. Kein Änderungsaufwand (Wrapper auf get_ball_states).

### Modus 3 (T3) – Drei Binärzähler h/m/s [Idee «Binärzähler», Originalform]

**Prinzip:** Drei senkrechte Binär-Säulen – je ein Zähler für Stunden, Minuten, Sekunden. LSB unten (Zeile 7), MSB oben. 24-h-Zählung (wie Base4).

| Spalte | Inhalt | Bits (Zeile) |
|---|---|---|
| A | Stunden 0–23 | 5 Bit: 1 (Z7), 2 (Z6), 4 (Z5), 8 (Z4), 16 (Z3) |
| B | dunkel (Trenner) | – |
| C | Minuten 0–59 | 6 Bit: 1 (Z7) … 32 (Z2) |
| D | dunkel (Trenner) | – |
| E | Sekunden 0–59 | 6 Bit: 1 (Z7) … 32 (Z2) |

**Farben:** A rot, C grün, E gelb (Sekunden, wie Base4-«beides»). **Update:** jede Sekunde.

**Beispiel 14:35:49:**

| Zeile | A (Stunde) | B | C (Minute) | D | E (Sekunde) |
|---|---|---|---|---|---|
| 0 | . | . | . | . | . |
| 1 | . | . | . | . | . |
| 2 | . | . | ● 32 | . | ● 32 |
| 3 | . | . | . | . | ● 16 |
| 4 | ● 8 | . | . | . | . |
| 5 | ● 4 | . | . | . | . |
| 6 | ● 2 | . | ● 2 | . | . |
| 7 | . | . | ● 1 | . | ● 1 |

(rot: A4, A5, A6 → 14; grün: C2, C6, C7 → 35; gelb: E2, E3, E7 → 49)

**Bewertung:** Auflösung 1 s – die lebendigste Alltags-Anzeige (Sekunden laufen sichtbar). Aufwand klein. LED-Last gering (maximal 17 von 40). Lesbarkeit nach kurzer Übung gut.

### Modus 4 (T4) – Grosse Ziffern, statisch [Idee «grosse Zahlen», Variante A]

**Prinzip:** Je eine Ziffer füllt die ganze Tafel (5 Spalten breit × 7 Zeilen hoch, Standard-5×7-Font wie beim HD44780/Arduino). Gezeigt wird zyklisch: H-Zehner → H-Einer → M-Zehner → M-Einer, Wechsel alle ca. 2 s (konfigurierbar). Zeile 7 bleibt frei – Vorschlag: ein Sekundenpunkt in Zeile 7, Mitte (Spalte C), im Sekundentakt an/aus.

**Farben:** Stunden-Ziffern rot, Minuten-Ziffern grün (konsistent mit dem Farbschema der Uhr). **Update:** alle 2 s, Sekundenpunkt jede Sekunde.

**Beispiel 14:35:** erst grosse «1», dann «4», dann «3», dann «5» – voller Zyklus 8 s.

**Bewertung:** Beste Lesbarkeit für Besucher – keine Übungszeit nötig. Aufwand klein (Font-Tabelle für 0–9). LED-Last gering (ca. 10–20 LEDs je Ziffer).

### Modus 5 (T5) – Tagesfortschritt-Balken [Vibe-Vorschlag]

**Prinzip:** «Wie viel vom Tag ist schon?» – die Tafel als Fortschrittsbalken: 40 LEDs = 1440 min, also 36 min je LED. In Kettenreihenfolge (LED 0 = A0 oben links … LED 39 = E7 unten rechts) leuchten alle LEDs bis zum aktuellen Stand: LED i leuchtet, wenn floor(Minuten_seit_Mitternacht / 36) mindestens i ist.

**Farben:** Vorschlag: tageszeitabhängiger Verlauf – Nacht blau, Morgen orange, Mittag gelb, Abend rot (Stimmungsanzeige); alternativ einfarbig weiss. **Update:** minütlich genügt.

**Beispiel 14:35** = 875 min → 875 / 36 = 24,3 → LEDs 0–24 leuchten (25 LEDs).

**Bewertung:** Intuitiv und philosophisch reizvoll («der Tag füllt sich»). Als alleinige Uhr zu grob (36 min) – deshalb bewusst mit der TM1637-Klartextanzeige kombiniert, die ja ohnehin läuft. LED-Last am Tagesende bis 40 LEDs (Volllast, siehe 6.3). Aufwand klein.

### Modus 6 (Shift+T1) – Binär-BCD-Uhr [Idee «Binärzähler», Variante A]

**Prinzip:** Klassische Binäruhr im BCD-Stil: jede Dezimalziffer einzeln im Binärcode, eine Spalte je Ziffer, LSB unten. 24-h-Zählung.

| Spalte | Inhalt | Bits (Zeile) |
|---|---|---|
| A | Stunden-Zehner 0–2 | 1 (Z7), 2 (Z6) |
| B | Stunden-Einer 0–9 | 1 (Z7), 2 (Z6), 4 (Z5), 8 (Z4) |
| C | Minuten-Zehner 0–5 | 1 (Z7), 2 (Z6), 4 (Z5) |
| D | Minuten-Einer 0–9 | 1 (Z7) … 8 (Z4) |
| E | Sekunden-Einer 0–9 (optional; ohne Sekunden dunkel) | 1 (Z7) … 8 (Z4) |

**Farben:** A/B rot, C/D grün, E gelb. **Update:** mit Spalte E jede Sekunde, sonst jede Minute.

**Beispiel 14:35:49:** rot A7 (Zehner 1) und B5 (Einer 4); grün C7 + C6 (3 = 2+1) und D7 + D5 (5 = 4+1); gelb E7 + E4 (9 = 8+1).

**Bewertung:** Für Binär-Kenner die «ehrlichste» Uhr; leichter lesbar als Modus 3, weil ziffernweise statt als grosse Zahl. Aufwand klein. LED-Last gering.

### Modus 7 (Shift+T2) – Durchlaufende grosse Zahlen (Laufschrift) [Idee «grosse Zahlen», Variante B]

**Prinzip:** Die Zeit als Laufschrift, die durchs 5er-Fenster zieht: «HH:MM» im 5×7-Font (Doppelpunkt als schmale Glyphe) schiebt sich spaltenweise von rechts nach links durch die Tafel. Ziffernbreite 5 + Lücke 1, Doppelpunkt ca. 2 → «14:35» ist rund 24 Spalten breit; bei 0,3–0,5 s pro Spalte dauert ein Durchlauf etwa 10 s, plus kurze Pause.

**Farben:** Ziffern weiss (Show-Modus) oder Stunden rot / Minuten grün. **Update:** kontinuierlich (alle 0,3–0,5 s ein Frame).

**Beispiel 14:35:** «1» wandert ein, dann «4», Doppelpunkt, «3», «5» – nach einer Pause wiederholt sich der Vorgang mit der dann aktuellen Zeit.

**Bewertung:** Show-Modus mit hohem Wiedererkennungswert; nutzt denselben Font wie Modus 4. Aufwand mittel (Schiebe-Logik, ca. 30–50 Zeilen). LED-Last gering (je Frame nur ein Glyphenausschnitt).

### Modus 8 (Shift+T3) – Sekunden-Serpentine [Vibe-Vorschlag]

**Prinzip:** Die laufende Minute sichtbar machen: Sekunde 0–59 als Zähler, der die Tafel in Kettenreihenfolge (A0 → E7) füllt. 60 Sekunden auf 40 LEDs: LED = Sekunde mod 40, die Farbe zeigt die Runde – Runde 1 (0–39 s) grün, Runde 2 (40–59 s) orange.

**Variante erweitert:** Die LEDs der Runde 1 bleiben gedimmt (z. B. 30 % Helligkeit) stehen, Runde 2 übermalt mit voller Helligkeit – der Fortschritt der Minute wird doppelt genau sichtbar.

**Update:** jede Sekunde. **Beispiel 23:57:47:** 47 mod 40 = 7 → LEDs 0–7 orange, Rest dunkel (bzw. in der erweiterten Variante orange über gedimmtem grünem Rest).

**Bewertung:** Sehr lebendig – die Uhr «atmet» im Sekundentakt; ideal für Demo und Besucher. Auflösung 1 s. Aufwand klein. LED-Last: bei Sekunde 39 kurz alle 40 LEDs, aber nur einfarbig (Strom unkritisch).

### Modus 9 (Shift+T4) – Grobe Analog-Uhr [Vibe-Vorschlag, Experiment]

**Prinzip:** Das Raster als Zifferblatt: Stundenzeiger (rot) und Minutenzeiger im 5-min-Raster (grün) – je 1 LED an der Zeigerposition. Die vier Hauptpositionen (12 / 3 / 6 / 9) leuchten zusätzlich schwach weiss als Referenz. 12-h-Zählung (wie Fibonacci).

**Positionstabelle (Spalte × Zeile):**

| Stunde | Pos | Stunde | Pos | Stunde | Pos | Stunde | Pos |
|---|---|---|---|---|---|---|---|
| 12 | C0 | 3 | E4 | 6 | C7 | 9 | A3 |
| 1 | D0 | 4 | E5 | 7 | B7 | 10 | A1 |
| 2 | E1 | 5 | D7 | 8 | A5 | 11 | B0 |

(Minutenzeiger: gleiche Tabelle, Index = Minute / 5.)

**Beispiel 14:35:** Stundenzeiger (14 h = 2) → E1 rot; Minutenzeiger (35 min = Position 7) → B7 grün; dazu schwach weiss C0, E4, C7, A3.

**Bewertung (Konfidenz niedrig):** Charmant, aber auf 5×8 grob – nur 12 statt 60 Minutenpositionen, Auflösung 5 min. Die Lesbarkeit ist am Gerät zu testen; wenn er sich nicht bewährt, bekommt der Platz eine Reserve-Idee (Kap. 7). Aufwand mittel.

### Modus 10 (Shift+T5) – Pong-Uhr [Vibe-Vorschlag, Hommage]

**Prinzip:** Hommage an die Ping-Pong-Bälle: quer gespielt (8 Breitenpositionen = Zeilen 0–7, 5 hoch = Spalten A–E) läuft ein Endlos-Pong: der Ball (weiss) fliegt diagonal, oben und unten (Spalten A und E) prallt er ab, die Schläger (rot, je 2 LEDs hoch) an Zeile 0 und 7 bewegen sich so, dass sie ihn immer erreichen. Das Spiel ist Dekoration – die Zeit steht auf dem «Scoreboard»: Das TM1637 zeigt ja ohnehin HH:MM:SS; zusätzlich blendet die Tafel periodisch (z. B. alle 60 s für 5 s) den Spielstand quer im 3×5-Font ein: abwechselnd «14» und «35» (Breite 3 + 1 + 3 = 7, passt ins 8er-Fenster).

**Beispiel 14:35:** Ball fliegt und prallt; alle 60 s kurz «14» / «35» als Spielstand.

**Bewertung:** Der aufwendigste Modus (Spiellogik + Animation, geschätzt 100–150 Zeilen) und rein dekorativ – bewusst als letzter geplant. Thematisch passt er perfekt zur Ping-Pong-Uhr; das Konzept ist von Matrix-Uhren bekannt («Pong Clock»). LED-Last gering (max. ca. 6 LEDs).

## 6. Software-Skizze

### 6.1 Architektur

| Modul | Aufgabe |
|---|---|
| modes.py (neu) | Modus-Registry: id, Name, render(h, m, s) → Liste aus 40 (R, G, B)-Werten; Fibonacci und Base4 als Wrapper auf die bestehenden Funktionen (kein Code-Duplikat) |
| font5x7.py (neu) | Font-Tabelle 0–9 und Doppelpunkt als 5 Bitmasken à 7 Zeilen (gemeinfreier 5×7-Standardfont, z. B. HD44780/Arduino); Modus 7/10 nutzen zusätzlich einen 3×5-Mini-Font |
| display.py | Neue generische Funktion show_frame(colors40) neben den bestehenden show_time / show_base4 / show_field |
| buttons.py | Moduswahl (T1–T5, Shift-Zustand mit Timeout) + Langdruck (gpiozero: hold_time, when_held, hold_repeat) für die Zeitverstellung |
| main.py | Zustandsmaschine: aktueller Modus + Shift; Rendering nur bei Änderung (last_raster wie bisher); Laufschrift/Pong mit eigenem Frametiming |
| config.py | Modus-Konstanten, Ziffern-Wechselzeit, Scrollgeschwindigkeit, Shift-Timeout |

### 6.2 TM1637

Beim Moduswechsel kurz die Modus-Nummer (1–10, bei Shift mit «S»), danach wieder HH:MM:SS. Die halbe Spiegelung des 6-stelligen Moduls bleibt durch _modul_segments() abgedeckt (Fallstrick 31 unverändert wirksam).

### 6.3 LED-Last und Strom

Worst Case ist der Tagesfortschritt am Tagesende: 40 LEDs; bei weiss und Helligkeit 102 von 255 rund 1 A (überschlägig, Konfidenz mittel). Am 4-A-Netzteil der Tafel unkritisch. Die Soft-Start-Rampe (Fallstrick 29) bleibt für alle Modi wirksam. Laufschrift, Pong und Binär-Modi liegen weit darunter.

### 6.4 Verifikation

Wie bisher automatisiert je Modus: Randwerte (0:00:00, 12:00:00, 23:59:59) und Stichproben über den Tag, asserts zu Tabellenlängen und LED-Indizes (0–39, jede LED höchstens 1× pro Frame, alle 40 lückenlos). Plus Funktionstest am Gerät (Dienst stoppen, wie in docs/Betriebsbefehle.md beschrieben).

### 6.5 Keine Wokwi-Simulation

Der Entscheid vom 21.10./07.11.2026 bleibt: keine neuen Wokwi-Demos. Neue Modi werden direkt am Gerät geprüft.

## 7. Reserve-Ideen (falls ein Platz frei wird)

- **Stimmungsmodus:** Tageszeit als Farbe (Mitternacht blau → Sonnenaufgang orange → Mittag gelb → Abend rot), Tafel sonst dunkel – die «Zen-Uhr»: Zeit als Atmosphäre statt als Zahl.
- **Regenbogen-/Demo-Modus** für Präsentationen (Farb- und Funktionsshow).
- **Mini-Wortuhr:** deutsche Zeitwörter («FÜNF», «ZEHN», «VIERTEL», «VOR», «NACH», «HALB») nacheinander im 3×5-Font – statisch passt immer nur ein Wort ins 5er-Fenster, also höchstens als Laufschrift sinnvoll.
- **12h/24h-Umschaltung** für die Binär-Modi (Modus 3/6 zählen standardmässig 24 h).

## 8. Offene Fragen (Entscheidliste)

1. **Shift-Mechanik:** Toggle mit Timeout (Empfehlung, Kap. 3.2) oder Halten? – zu entscheiden.
2. **Zeitverstellung:** Langdruck (Empfehlung, Kap. 4), Wegfallen oder Setup-Modus beim Boot? – zu entscheiden.
3. **Modus 9 (Analog):** erst am Gerät testen; bei ungenügender Lesbarkeit Platz an eine Reserve-Idee vergeben.
4. **Tasten-Zuordnung** der acht Neuen: Vorschlag in Kap. 3.1 – nach den ersten Demos festzurren.
5. **Grosse Ziffern:** 5×7-Standardfont (Zeile 7 frei für Sekundenpunkt, Empfehlung) oder eigener 5×8-Font?
6. **Boot-Verhalten:** immer Fibonacci-Modus und Shift aus (Empfehlung), oder letzten Modus in einer Datei merken?
7. **Tagesfortschritt:** tageszeitabhängiger Farbverlauf (Empfehlung) oder einfarbig?

## 9. Fahrplan

| Stufe | Inhalt |
|---|---|
| 0 | Entscheidungen zu Kap. 8.1 und 8.2 (Shift + Zeitverstellung) |
| 1 | Schnittstelle: modes.py, display.show_frame, Shift-/Moduswahl und Langdruck in buttons.py – die zwei bestehenden Modi laufen unverändert durch die neue Schnittstelle |
| 2 | Modus 3 (Binärzähler) + Modus 4 (grosse Ziffern) mit font5x7.py – erster Mehrwert-Stand |
| 3 | Modus 5 (Tagesfortschritt), Modus 6 (BCD), Modus 8 (Sekunden-Serpentine) |
| 4 | Modus 7 (Laufschrift), Modus 9 (Analog, Test), Modus 10 (Pong, zuletzt) |

Jede Stufe: Verifikation, Funktionstest am Gerät, README/Bauanleitung nachziehen.
