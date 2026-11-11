# Erweiterungen: Zehn Zeitdarstellungen auf dem 5×8-Raster

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026
Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
Status: **Stufe 1–3 abgeschlossen und am Gerät bestätigt** (Stufe 3: 11.11.2026). Entscheidungen: Shift = Toggle mit 10-s-Timeout; Zeitverstellung = Langdruck T2–T5. Platz 1–8 laufen durch modes.py (Fallstrick-33-Spiegelfix in display.py live verifiziert); Platz 7 = EierUhr – die Laufschrift entfiel (Entscheid Paul 10.11.2026); Platz 9–10 folgen in Stufe 4 (zurückgestellt bis Pauls Go, 11.11.2026). Details: Kap. 10.

## 1. Ziel

Die Uhr zeigt die Zeit heute über die fünf Fibonacci-Anzeigewerte 1, 1, 2, 3, 5 (Felder A–E, 5-Minuten-Schritte) und – über den Modus-Taster T6 – zusätzlich im Base4-Modus (3×3-Matrix, minutengenau). Die Tafel hat aber 40 einzeln adressierbare LEDs im Raster **5 Spalten × 8 Zeilen** – deutlich mehr Darstellungsfläche, als diese beiden Modi nutzen.

Ziel der Erweiterung:

- Das Raster **5×8 (hochkant)** resp. **8×5 (quer gelesen)** als vollwertige Zeit-Anzeige nutzen – zusätzlich zu den bestehenden Fibonacci-Anzeigewerten.
- **Zehn verschiedene Darstellungen**: Taster T1–T5 wählen fünf Modi direkt, Taster T6 wirkt als **Shift** und T6 + T1–T5 wählen fünf weitere.
- Fibonacci und Base4 **behalten zwei der zehn Plätze**; acht Modi kommen neu dazu.

Anstoss für die neuen Modi (Ideen von Paul, 10.11.2026):

1. **Binärzähler für Sekunden, Minuten, Stunden** – daraus werden zwei Varianten: drei parallele Binärzähler (Modus 3) und eine klassische Binär-BCD-Uhr (Modus 6).
2. **Zeit mit grossen, durchlaufenden Zahlen (5 breit, 8 hoch)** – daraus wurden zwei Varianten: statisch wechselnde grosse Ziffern (Modus 4, umgesetzt in Stufe 2) und eine Laufschrift, die durchs Fenster zieht (ursprünglich Modus 7 – am 10.11.2026 zugunsten der EierUhr verworfen, siehe Punkt 3).
3. **EierUhr (Pauls Skizze, 10.11.2026):** ein Sanduhr-Glas auf der Tafel, 6 Kugeln à 30 s fallen vom oberen in den unteren Teil – übernimmt Platz 7 (statt Laufschrift); Umsetzung in Stufe 3.

## 2. Ausgangslage und Konventionen

**Tafel (massgeblich, siehe Bauanleitung):** 5 Spalten (A–E) × 8 Zeilen (0–7), hochkant, öffnende Schnecke. LED-Index = Spalte × 8 + Zeile, Datenkette spaltenweise (IN an A0). Zeile 0 oben, Zeile 7 unten.

- **Hochkant (5×8):** 5 Positionen nebeneinander (Spalten A–E), 8 übereinander (Zeilen 0–7).
- **Quer gedacht (8×5):** Breite = 8 (Zeilen 0–7), Höhe = 5 (Spalten A–E) – für Modi, die «liegend» gelesen werden (Pong; die geplante Laufschrift ist am 10.11.2026 der EierUhr gewichen).

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
| 6 | Shift+T1 | Binär-BCD-Uhr | Idee «Binärzähler», Variante A | 1 s |
| 7 | Shift+T2 | EierUhr (Sanduhr: 6 Kugeln à 30 s) | Idee «EierUhr» (Paul), 10.11.2026 | 30 s |
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

**Entschieden (10.11.2026):** Toggle mit 10-s-Timeout (SHIFT_TIMEOUT_SEC) und TM1637-Feedback («SHIFT», nach dem Timeout Modusnummer). Begründung: Einhandbedienung, Konsistenz mit dem bisherigen T6-Verhalten, und der Timeout schliesst den einzigen Nachteil (vergessener Shift) weitgehend.

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

**Entschieden (10.11.2026):** Variante B (Langdruck) für die Zeitverstellung – gpiozero hold_time 1 s, wiederholend (hold_repeat): T2 lang = +1 min, T3 lang = +5 min, T4 lang = +1 h, T5 lang = Normalbetrieb. Der Handbetrieb ist seit dem NTP-Fix nur noch Reserve, aber genau in Reservesituationen (kein Netz) braucht man ihn. Die **Feld-Durchschaltung (früher T1)** entfällt als Betriebsmodus: ihre Erklär- und Prüffunktion deckt anzeige_test.py bereits ab.

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

**Bewertung:** Auflösung 1 s – die lebendigste Alltags-Anzeige (Sekunden laufen sichtbar). Aufwand klein. LED-Last gering (maximal 17 von 40). Lesbarkeit nach kurzer Übung gut. **Status:** ✅ umgesetzt (Stufe 2, 10.11.2026), am Gerät bestätigt.

### Modus 4 (T4) – Grosse Ziffern, statisch [Idee «grosse Zahlen», Variante A]

**Prinzip:** Je eine Ziffer füllt die ganze Tafel (5 Spalten breit × 7 Zeilen hoch, Standard-5×7-Font wie beim HD44780/Arduino). Gezeigt wird zyklisch: H-Zehner → H-Einer → M-Zehner → M-Einer, Wechsel alle ca. 2 s (konfigurierbar). Zeile 7 bleibt frei – Vorschlag: ein Sekundenpunkt in Zeile 7, Mitte (Spalte C), im Sekundentakt an/aus.

**Farben:** Stunden-Ziffern rot, Minuten-Ziffern grün (konsistent mit dem Farbschema der Uhr). **Update:** alle 2 s, Sekundenpunkt jede Sekunde.

**Beispiel 14:35:** erst grosse «1», dann «4», dann «3», dann «5» – voller Zyklus 8 s.

**Bewertung:** Beste Lesbarkeit für Besucher – keine Übungszeit nötig. Aufwand klein (Font-Tabelle für 0–9). LED-Last gering (ca. 10–20 LEDs je Ziffer). **Status:** ✅ umgesetzt (Stufe 2, 10.11.2026), am Gerät bestätigt.

### Modus 5 (T5) – Tagesfortschritt-Balken [Vibe-Vorschlag]

**Prinzip:** «Wie viel vom Tag ist schon?» – die Tafel als Fortschrittsbalken: 40 LEDs = 1440 min, also 36 min je LED. In Kettenreihenfolge (LED 0 = A0 oben links … LED 39 = E7 unten rechts) leuchten alle LEDs bis zum aktuellen Stand: LED i leuchtet, wenn floor(Minuten_seit_Mitternacht / 36) mindestens i ist.

**Farben:** ✅ entschieden (11.11.2026): tageszeitabhängiger Verlauf (Stimmungsanzeige) – die ganze Leiste leuchtet in der Farbe der aktuellen Tagesphase (config.DAY_PHASES): Nacht (0–6, 21–24 h) blau, Morgen (6–9 h) orange, Mittag (9–17 h) gelb, Abend (17–21 h) rot. **Update:** minütlich genügt.

**Beispiel 14:35** = 875 min → 875 / 36 = 24,3 → LEDs 0–24 leuchten (25 LEDs).

**Bewertung:** Intuitiv und philosophisch reizvoll («der Tag füllt sich»). Als alleinige Uhr zu grob (36 min) – deshalb bewusst mit der TM1637-Klartextanzeige kombiniert, die ja ohnehin läuft. LED-Last am Tagesende bis 40 LEDs (Volllast, siehe 6.3). Aufwand klein. **Status:** ✅ umgesetzt und am Gerät bestätigt (Stufe 3, 11.11.2026; 65 Stub-Checks, test_stufe3.py).

### Modus 6 (Shift+T1) – Binär-BCD-Uhr [Idee «Binärzähler», Variante A]

**Prinzip:** Klassische Binäruhr im BCD-Stil: jede Dezimalziffer einzeln im Binärcode, eine Spalte je Ziffer, LSB unten. 24-h-Zählung.

| Spalte | Inhalt | Bits (Zeile) |
|---|---|---|
| A | Stunden-Zehner 0–2 | 1 (Z7), 2 (Z6) |
| B | Stunden-Einer 0–9 | 1 (Z7), 2 (Z6), 4 (Z5), 8 (Z4) |
| C | Minuten-Zehner 0–5 | 1 (Z7), 2 (Z6), 4 (Z5) |
| D | Minuten-Einer 0–9 | 1 (Z7) … 8 (Z4) |
| E | Sekunden-Einer 0–9 (optional; ohne Sekunden dunkel) | 1 (Z7) … 8 (Z4) |

**Farben:** A/B rot, C/D grün, E gelb. **Update:** ✅ entschieden (11.11.2026): mit Spalte E (Sekunden-Einer, gelb) – Rendertakt jede Sekunde.

**Beispiel 14:35:49:** rot A7 (Zehner 1) und B5 (Einer 4); grün C7 + C6 (3 = 2+1) und D7 + D5 (5 = 4+1); gelb E7 + E4 (9 = 8+1).

**Bewertung:** Für Binär-Kenner die «ehrlichste» Uhr; leichter lesbar als Modus 3, weil ziffernweise statt als grosse Zahl. Aufwand klein. LED-Last gering. **Status:** ✅ umgesetzt und am Gerät bestätigt (Stufe 3, 11.11.2026; 65 Stub-Checks, test_stufe3.py).

### Modus 7 (Shift+T2) – EierUhr (Sanduhr) [Idee «EierUhr» von Paul, 10.11.2026 – ersetzt die Laufschrift]

**Entscheid (10.11.2026, Paul):** Die geplante Laufschrift (durchlaufende grosse Zahlen) entfällt ganz – Platz 7 bekommt stattdessen die EierUhr. Sie hat einen echten Nutzen (Ei-Koch-Timer), passt zur Ping-Pong-Ball-Idee und braucht weder Schiebe-Logik noch einen 3×5-Mini-Font. font5x7.py bleibt unverändert für Modus 4 erhalten.

**Prinzip:** Ein Sanduhr-Glas füllt die ganze Tafel: gedimmter Umriss, sechs gelbe Kugeln à 30 Sekunden fallen einzeln vom oberen in den unteren Teil. Der 3-Minuten-Zyklus ist an die vollen Minuten gebunden – eine Runde startet immer bei x:00, x:03, x:06 …: elapsed = (Minuten mod 3) × 60 + Sekunden. Rendertakt 1 s (tick = (h, m, s)).

**Layout (logische Konvention LED = Spalte × 8 + Zeile, Zeile 0 oben):**

```
      A  B  C  D  E
Z0    #  #  #  #  #      Umriss: 0, 8, 16, 24, 32
Z1    #  o  o  o  #      oben: Kugeln 9, 17, 25 / Wand 1, 33
Z2    #  o  o  o  #      oben: Kugeln 10, 18, 26 / Wand 2, 34
Z3    #  #  #  #  .      Taille: 3, 11, 19, 27
Z4    .  #  #  #  .      Taille: 12, 20, 28
Z5    #  o  o  o  #      unten: Kugeln 13, 21, 29 / Wand 5, 37
Z6    #  o  o  o  #      unten: Kugeln 14, 22, 30 / Wand 6, 38
Z7    #  #  #  #  #      Umriss: 7, 15, 23, 31, 39
```

(# = gedimmter Glas-Umriss, o = Kugelplatz, . = dunkel.) Der Umriss umfasst 25 LEDs; dunkel bleiben nur A4, E3 und E4. Kugelplätze: oben Zeilen 1–2 (LEDs 9, 17, 25 / 10, 18, 26), unten Zeilen 5–6 (LEDs 13, 21, 29 / 14, 22, 30), jeweils Spalten B–D.

**Falllogik (Variante 1 – revidierte Empfehlung):** gefallen = elapsed // 30 (0–5) – Kugel k ist gefallen, sobald elapsed ≥ k × 30 s. Der obere Raum leert sich von unten nach oben (erst Zeile 2, dann Zeile 1; je B → C → D), der untere füllt sich von unten nach oben (erst Zeile 6, dann Zeile 5). «Alle 6 Kugeln unten» ist bewusst nie zu sehen: Der Zustand dauert exakt 0 s – der Sprung zurück auf 6 Kugeln oben (bei x:00/x:03/…) markiert die 3-Minuten-Grenze. **Warum die Revision:** Bei der zuerst erwogenen Variante 2 (erste Kugel fällt zum Zyklusstart, gefallen = min(6, elapsed // 30 + 1)) läge «alle 6 unten» bereits ab 2:30 – der scheinbare «Fertig»-Zustand käme 30 s zu früh. Variante 1 zeigt die verstrichene Zeit korrekt an (gefallene Kugeln × 30 s). Falls Variante 2 am Gerät doch besser gefällt: Ein-Zeilen-Änderung in modes.py.

**Optik (Entscheid 10.11.2026):** Umriss gedimmt – neue Konstante COLOR_GLAS in config.py (z. B. (40, 40, 40)); Kugeln gelb = COLOR_BASE4_BOTH (Sand-Optik). LED-Last unkritisch: maximal 31 von 40 LEDs (elapsed = 150–179 s), davon 25 nur gedimmt.

**Beispiel 14:37:30:** 37 mod 3 = 1 → elapsed = 90 s → 3 Kugeln gefallen: unten gelb die LEDs 14, 22, 30 (Zeile 6), oben gelb nur noch Zeile 1 (LEDs 9, 17, 25), Umriss gedimmt. Ei-Koch-Praxis: Ei rein bei x:00/x:03/…, der Sprung «alles wieder oben» zeigt die nächste 3-Minuten-Grenze an.

**Bewertung:** Nutzmodus mit Charme – Sanduhr-Prinzip auf 40 LEDs, Auflösung 30 s, Augenzwinkern zur Ping-Pong-Idee. Aufwand klein (kein Font nötig, ca. 20–30 Zeilen in modes.py plus Konstante in config.py). **Status:** ✅ umgesetzt und am Gerät bestätigt (Stufe 3, 11.11.2026; 65 Stub-Checks, test_stufe3.py).

**Geplant: Fall-Animation des Sandkorns (Idee Paul, 11.11.2026 – Umsetzung mit Stufe 4):** Statt des Sprungs von «oben» nach «unten» wandert das Korn in der Fallssekunde (elapsed = k × 30 s) sichtbar durch die Taille: Es leuchtet nacheinander auf den Taille-LEDs C3 (LED 19) und C4 (LED 20) – je ca. 150 ms (geplante Konstante EIERUHR_FALL_MS), gelb wie die Kugeln – und erst danach erscheint die Kugel auf ihrem unteren Platz; die Fallzeit zählt trotzdem schon ab k × 30 s. Dafür braucht main.py ein Frame-Timing (Rendertakt unter 1 s während der Animation; geplante Funktion get_local_time_precise() mit Millisekunden in ntp_time.py) – derselbe Mechanismus, den die Pong-Uhr (Modus 10) ohnehin braucht; die EierUhr ist der erste Nutzniesser. Einfache Alternative (3 Zeilen, kein Umbau): Nur die Taille-LEDs C3+C4 leuchten in der Fallssekunde 1 s gelb auf. Entscheid (11.11.2026, Paul): fliessende Variante eingeplant, Umsetzung mit Stufe 4.

### Modus 8 (Shift+T3) – Sekunden-Serpentine [Vibe-Vorschlag]

**Prinzip:** Die laufende Minute sichtbar machen: Sekunde 0–59 als Zähler, der die Tafel in Kettenreihenfolge (A0 → E7) füllt. 60 Sekunden auf 40 LEDs: LED = Sekunde mod 40, die Farbe zeigt die Runde – Runde 1 (0–39 s) grün, Runde 2 (40–59 s) orange.

**Variante erweitert:** ✅ entschieden (11.11.2026): Die LEDs der Runde 1 bleiben nach Sekunde 39 gedimmt stehen (30 % Helligkeit, SERPENTINE_DIM_FAKTOR in config.py), Runde 2 übermalt mit voller Helligkeit orange – der Fortschritt der Minute wird doppelt genau sichtbar.

**Update:** jede Sekunde. **Beispiel 23:57:47:** 47 mod 40 = 7 → LEDs 0–7 orange, Rest dunkel (bzw. in der erweiterten Variante orange über gedimmtem grünem Rest).

**Bewertung:** Sehr lebendig – die Uhr «atmet» im Sekundentakt; ideal für Demo und Besucher. Auflösung 1 s. Aufwand klein. LED-Last: bei Sekunde 39 kurz alle 40 LEDs, aber nur einfarbig (Strom unkritisch). **Status:** ✅ umgesetzt und am Gerät bestätigt (Stufe 3, 11.11.2026; 65 Stub-Checks, test_stufe3.py).

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
| font5x7.py (neu) | Font-Tabelle 0–9 und Doppelpunkt als 5 Bitmasken à 7 Zeilen (gemeinfreier 5×7-Standardfont, z. B. HD44780/Arduino); Modus 10 nutzt zusätzlich einen 3×5-Mini-Font |
| display.py | Neue generische Funktion show_frame(colors40) neben den bestehenden show_time / show_base4 / show_field |
| buttons.py | Moduswahl (T1–T5, Shift-Zustand mit Timeout) + Langdruck (gpiozero: hold_time, when_held, hold_repeat) für die Zeitverstellung |
| main.py | Zustandsmaschine: aktueller Modus + Shift; Rendering nur bei Änderung (last_raster wie bisher); Pong mit eigenem Frametiming |
| config.py | Modus-Konstanten, Ziffern-Wechselzeit, EierUhr-Konstanten (COLOR_GLAS, Kugelfarbe), Shift-Timeout |

### 6.2 TM1637

Beim Moduswechsel kurz die Modus-Nummer (1–10, bei Shift mit «S»), danach wieder HH:MM:SS. Die halbe Spiegelung des 6-stelligen Moduls bleibt durch _modul_segments() abgedeckt (Fallstrick 31 unverändert wirksam).

### 6.3 LED-Last und Strom

Worst Case ist der Tagesfortschritt am Tagesende: 40 LEDs; bei weiss und Helligkeit 102 von 255 rund 1 A (überschlägig, Konfidenz mittel). Am 4-A-Netzteil der Tafel unkritisch. Die Soft-Start-Rampe (Fallstrick 29) bleibt für alle Modi wirksam. Pong, EierUhr (maximal 31 LEDs, Umriss nur gedimmt) und Binär-Modi liegen weit darunter.

### 6.4 Verifikation

Wie bisher automatisiert je Modus: Randwerte (0:00:00, 12:00:00, 23:59:59) und Stichproben über den Tag, asserts zu Tabellenlängen und LED-Indizes (0–39, jede LED höchstens 1× pro Frame, alle 40 lückenlos). Plus Funktionstest am Gerät (Dienst stoppen, wie in docs/Betriebsbefehle.md beschrieben).

### 6.5 Keine Wokwi-Simulation

Der Entscheid vom 21.10./07.11.2026 bleibt: keine neuen Wokwi-Demos. Neue Modi werden direkt am Gerät geprüft.

## 7. Reserve-Ideen (falls ein Platz frei wird)

- **Stimmungsmodus:** Tageszeit als Farbe (Mitternacht blau → Sonnenaufgang orange → Mittag gelb → Abend rot), Tafel sonst dunkel – die «Zen-Uhr»: Zeit als Atmosphäre statt als Zahl.
- **Regenbogen-/Demo-Modus** für Präsentationen (Farb- und Funktionsshow).
- **Mini-Wortuhr:** deutsche Zeitwörter («FÜNF», «ZEHN», «VIERTEL», «VOR», «NACH», «HALB») nacheinander im 3×5-Font – statisch passt immer nur ein Wort ins 5er-Fenster; mit dem Wegfall der Laufschrift (10.11.2026) ist die Idee zurückgestellt.
- **12h/24h-Umschaltung** für die Binär-Modi (Modus 3/6 zählen standardmässig 24 h).

## 8. Offene Fragen (Entscheidliste)

1. **Shift-Mechanik:** ✅ entschieden (10.11.2026): Toggle mit 10-s-Timeout.
2. **Zeitverstellung:** ✅ entschieden (10.11.2026): Langdruck (T2–T5).
3. **Modus 9 (Analog):** erst am Gerät testen; bei ungenügender Lesbarkeit Platz an eine Reserve-Idee vergeben.
4. **Tasten-Zuordnung** der acht Neuen: Vorschlag in Kap. 3.1 – nach den ersten Demos festzurren.
5. **Grosse Ziffern:** 5×7-Standardfont (Zeile 7 frei für Sekundenpunkt, Empfehlung) oder eigener 5×8-Font?
6. **Boot-Verhalten:** immer Fibonacci-Modus und Shift aus (Empfehlung), oder letzten Modus in einer Datei merken?
7. **Tagesfortschritt:** ✅ entschieden (11.11.2026): tageszeitabhängiger Farbverlauf (Nacht blau, Morgen orange, Mittag gelb, Abend rot).
8. **Modus 7 (EierUhr):** ✅ entschieden (10.11.2026): EierUhr statt Laufschrift (die entfällt ganz); Zyklus an volle Minuten gebunden (Neustart x:00/x:03/…); Falllogik Variante 1 (semantisch korrekt, siehe Kap. 5); Umriss gedimmt, Kugeln gelb. Umsetzung in Stufe 3.
9. **Modus 6 (BCD):** ✅ entschieden (11.11.2026): mit Sekunden (Spalte E = Sekunden-Einer, gelb; Rendertakt 1 s).
10. **Modus 8 (Serpentine):** ✅ entschieden (11.11.2026): erweiterte Variante (Runde-1-LEDs bleiben gedimmt stehen, Runde 2 übermalt orange).
11. **EierUhr-Fall-Animation:** ✅ eingeplant (11.11.2026, Paul): fliessende Variante – Korn wandert in der Fallssekunde durch die Taille (C3 → C4), die Kugel landet erst danach; Umsetzung mit Stufe 4 (bringt das Frame-Timing, das Pong ebenfalls braucht).

## 9. Fahrplan

| Stufe | Inhalt |
|---|---|
| 0 | Entscheidungen zu Kap. 8.1 und 8.2 (Shift + Zeitverstellung) – ✅ erledigt 10.11.2026 |
| 1 | Schnittstelle: modes.py, display.show_frame, Shift-/Moduswahl und Langdruck in buttons.py – ✅ umgesetzt 10.11.2026 (siehe Kap. 10) |
| 2 | Modus 3 (Binärzähler) + Modus 4 (grosse Ziffern) mit font5x7.py – erster Mehrwert-Stand – ✅ umgesetzt + am Gerät bestätigt 10.11.2026 |
| 3 | Modus 5 (Tagesfortschritt), Modus 6 (BCD), Modus 7 (EierUhr), Modus 8 (Sekunden-Serpentine) – ✅ umgesetzt + am Gerät bestätigt 11.11.2026 (siehe Kap. 10) |
| 4 | EierUhr-Fall-Animation (Modus 7), Modus 9 (Analog, Test), Modus 10 (Pong, zuletzt; nutzt das Frame-Timing der Fall-Animation) |

Jede Stufe: Verifikation, Funktionstest am Gerät, README/Bauanleitung nachziehen.

## 10. Umsetzungs-Stand (Stand: 11.11.2026)

**Stufe 1 am Gerät bestätigt (10.11.2026):** Tastensteuerung inkl. Taste 6 = Shift funktioniert – Moduswahl T1–T5, Shift-Toggle mit 10-s-Timeout, Langdruck-Zeitverstellung und TM1637-Feedback live geprüft.

**Entschieden (Stufe 0) und umgesetzt (Stufe 1):**

- **Shift (T6):** Toggle an/aus; schaltet sich nach 10 s (SHIFT_TIMEOUT_SEC) automatisch ab. TM1637 zeigt kurz «SHIFT», danach wieder HH:MM:SS.
- **Moduswahl:** T1 = Platz 1 (Fibonacci), T2 = Platz 2 (Base4). Reservierte Plätze (T3–T5, Shift+T1–T5) quittieren mit «- n», ohne die Anzeige zu ändern.
- **Zeitverstellung:** Langdruck T2–T5 (gpiozero hold_time 1 s, wiederholend) = +1 min / +5 min / +1 h / Normalbetrieb; Feedback «1MIN», «5MIN», «1STD», «NORM».
- **Software:** neues Modul modes.py (Modus-Registry mit Rendertakt; Fibonacci und Base4 als Wrapper auf die bestehenden Funktionen, kein Code-Duplikat), display.show_frame() als generische Schnittstelle, buttons.py neu (Moduswahl/Shift/Langdruck; Langdruck-Kennzeichnung verhindert den Moduswechsel beim Loslassen), main.py auf (Modus, Takt)-gesteuertes Rendering umgestellt, tm1637_display.show_text() zeichensatz-sicher (Library-Zeichensatz im Quellcode geprüft: 0–9, a–z, A–Z, Leerzeichen, «-», «*»).
- **Boot-Verhalten:** Modus 1 (Fibonacci), Shift aus, Offset 0 – wie bisher.
- **Verifikation (Stub-Tests, 10.11.2026):** 16 Testgruppen bestanden – Registry, Fibonacci-Frame (inkl. Live-Fall 13:32 = A grün + D blau), Base4-Frame über 24 h, Rendertakt, Moduswahl/Shift/Timeout/Langdruck, show_frame, TM1637-Zeichensatz, main-Zustand. anzeige_test.py und steuerbox_test.py bleiben unberührt (eigene Taster-Abfragen, keine gemeinsamen Konstanten).

**Umgesetzt (Stufe 2, 10.11.2026):**

- **Modus 3 (T3) – drei Binärzähler h/m/s:** Spalte A = Stunden 0–23 (5 bit, rot), Spalte C = Minuten 0–59 (6 bit, grün), Spalte E = Sekunden 0–59 (6 bit, gelb); LSB unten (Zeile 7), Spalten B/D dunkel als Trenner. Rendertakt 1 s. Beispiel 14:35:49 → rot A4/A5/A6, grün C2/C6/C7, gelb E2/E3/E7 – exakt wie die Tabelle in Kap. 3.
- **Modus 4 (T4) – grosse statische Ziffern:** eine Ziffer füllt die Tafel (font5x7, Zeilen 0–6); Ziffernfolge H-Zehner → H-Einer → M-Zehner → M-Einer, Wechsel alle `ZIFFERN_WECHSEL_SEC` = 2 s, minutenorientiert (H-Zehner bei Sekunde 0, voller Zyklus 8 s); Stunden rot, Minuten grün; weisser Sekundenpunkt auf LED 23 (Spalte C, Zeile 7), an bei gerader Sekunde. Rendertakt 1 s.
- **Software:** neues Modul font5x7.py (klassischer gemeinfreier 5×7-Punktmatrix-Font im Adafruit/glcdf-Stil; Spaltenbytes, Bit 0 = oben; `glyph()` mit leerem Fallback für unbekannte Zeichen), modes.py um `_binary_frame()`/`_big_digit_frame()` ergänzt, config.py um `ZIFFERN_WECHSEL_SEC` ergänzt, main.py-Log gedrosselt (max. 1 Logzeile pro Minute und Modus, da Modus 3/4 sekündlich rendern).
- **Verifikation (Stub-Tests, 10.11.2026):** 16 Testgruppen bestanden – u. a. Binärzähler über 24 h gegen Referenzlogik, font5x7 (alle 10 Ziffern eindeutig), Ziffernfolge/Farbwahl/Sekundenpunkt von Modus 4 über den Tag, plus komplette Stufe-1-Regression (Fibonacci, Base4, Tasten inkl. «M 3»/«M 4» und «- 5» … «- 10», Langdruck).

**Gerätetest Stufe 2 + Fallstrick 33 (10.11.2026, Paul, Fotos IMG_8947–8950):**

- **Modus 3 (T3) läuft am Gerät** – Paul: «T3 ist OK!».
- **Modus 4 (T4) zeigte die Ziffern spiegelverkehrt** (links/rechts vertauscht) – «Zahlen müssen gewendet werden».
- **Ursache (Fallstrick 33):** Die reale Tafel hängt spaltenweise gespiegelt an der Datenkette: Die Kette beginnt real bei Spalte E (rechts), nicht wie in der Bauanleitung dokumentiert bei Spalte A (Kettensegment LED 0–7 = physische Spalte E usw.). Wie beim TM1637-Fallstrick 31 liegt die Spiegelung in der Verdrahtung des Panels, nicht in der Library.
- **Warum es bisher nicht auffiel:** Die Fibonacci-Anzeige ist spiegelinvariant lesbar – Feld B (3×3) und C (2×2) tauschen zwar die Seiten, aber die Werte wandern mit; die abgelesene Zeit blieb immer richtig. Base4 (Wertepositionen 48/3 seitenverkehrt) und Modus 3 (Stunden-Spalte rechts statt links) waren dagegen ebenfalls falsch herum – nach dem Fix mitkontrollieren.
- **Fix (10.11.2026):** display.py spiegelt die Spalte beim Schreiben zentral (_PHYS_LED-Tabelle: physische LED = (4 − Spalte) × 8 + Zeile); alle Module rechnen logisch unverändert weiter (LED-Index = Spalte × 8 + Zeile, Spalte A = links). anzeige_test.py (Direktschreib-Routine render()) nachgezogen; Kommentar in mapping.py korrigiert.
- **Verifikation (Stub-Test, 10.11.2026):** 22 Checks bestanden – Spiegel-Tabelle als Bijektion (A0 → physisch Segment E), Ziffern 1/4/5/7 aufrecht in Panel-Sicht, Sekundenpunkt unten Mitte (nur bei gerader Sekunde), Fibonacci-Feld C unten links, Base4-Wert 48 links in der Matrix, Modus-3-Spalten rot links / grün Mitte / gelb rechts, clear_all/show_frame-Randfälle, logische Frame-Regression unveraendert.
- **Fix am Gerät BESTÄTIGT (10.11.2026, Paul):** «Jetzt ist die gesamte Anzeige kohärent!» – Modus 4 aufrecht, Modus 3 Stunden-Spalte rot links, Base4 seitenrichtig, Fibonacci unverändert. Stufe 2 damit vollständig am Gerät bestätigt.

**Umgesetzt (Stufe 3, 11.11.2026):**

- **Modus 5 (T5) – Tagesfortschritt-Balken:** 40 LEDs = 1440 min (36 min je LED) in Kettenreihenfolge; LED i leuchtet, wenn floor(Minuten/36) ≥ i. Ganze Leiste in der Farbe der aktuellen Tagesphase (DAY_PHASES: Nacht 0–6/21–24 blau, Morgen 6–9 orange, Mittag 9–17 gelb, Abend 17–21 rot; Entscheid 11.11.2026). Rendertakt minütlich (tick = (h, m)).
- **Modus 6 (Shift+T1) – Binär-BCD-Uhr:** eine Spalte je Dezimalziffer, LSB unten (Zeile 7): A = H-Zehner (2 bit), B = H-Einer (4 bit), C = M-Zehner (3 bit), D = M-Einer (4 bit), E = S-Einer (4 bit; Entscheid 11.11.2026: mit Sekunden). A/B rot, C/D grün, E gelb. Rendertakt 1 s.
- **Modus 7 (Shift+T2) – EierUhr (Sanduhr):** exakt wie Kap. 5 – Umriss 25 LEDs gedimmt (COLOR_GLAS), 6 gelbe Kugeln à 30 s (COLOR_BASE4_BOTH), Zyklus elapsed = (m mod 3) × 60 + s, Falllogik Variante 1, oberer Raum leert sich von unten nach oben, unterer füllt sich von unten nach oben. Rendertakt 1 s.
- **Modus 8 (Shift+T3) – Sekunden-Serpentine:** LED = s mod 40 in Kettenreihenfolge; Runde 1 (0–39 s) grün füllend, Runde 2 (40–59 s) orange (COLOR_ORANGE) über den gedimmten Runde-1-LEDs (SERPENTINE_DIM_FAKTOR = 30 %; Entscheid 11.11.2026: erweiterte Variante). Rendertakt 1 s.
- **Software:** modes.py um vier Frame-Funktionen ergänzt (Platz 5–8 aktiviert, Platz 7 heisst jetzt «EierUhr (Sanduhr)»), config.py um COLOR_GLAS, COLOR_ORANGE, SERPENTINE_DIM_FAKTOR und DAY_PHASES ergänzt. main.py, buttons.py, display.py unverändert – die Registry-Schnittstelle aus Stufe 1 greift ohne Änderung (T5/Shift+T1–T3 schalten jetzt auf die neuen Modi, TM1637-Feedback «M 5» … «M 8» automatisch).
- **Verifikation (Stub-Test test_stufe3.py, 11.11.2026):** 65 Checks bestanden – Registry (Platz 1–8 verfügbar, 9/10 reserviert, Takte), Modus 5 gegen Referenz über 24 h × 4 Minuten + Phasenfarben + Doku-Beispiel 14:35 (LEDs 0–24 gelb), Modus 6 gegen Referenz über 24 h (14 976 Fälle) + Doku-Beispiele 14:35:49 und 23:59:59, Modus 7 gegen Referenz über 60 min (3 600 Fälle; nie mehr als 6 Kugeln, «alle 6 Kugeln unten» nie sichtbar, dunkel nur A4/E3/E4 + leerer unterer Raum) + Doku-Beispiel 14:37:30, Modus 8 gegen Referenz über 60 s (Grenzfall Sekunde 39 → 40) + Doku-Beispiel 23:57:47, Regression Stufe 1 + 2 (Modi 1–4 rendern, u. a. Modus-3-Live-Fall 14:35:49 und Modus-4-Sekundenpunkt). Bemerkung: Die ersten Testläufe deckten vier Rechenfehler in den handgerechneten Sollwerten des Tests auf (BCD 23:59:59, EierUhr-Grenzfall 149 s, Serpentine-Testargument, fehlender Import) – die Implementierung selbst blieb dabei unverändert.

**Am Gerät bestätigt (11.11.2026, Paul: «Die neuen Modi funktionieren!»):** T5 = Tagesfortschritt, Shift+T1 = Binär-BCD, Shift+T2 = EierUhr, Shift+T3 = Sekunden-Serpentine. Bauanleitung nachgezogen (neues Kap. 7.12 inkl. Standard-Sequenz für Gerätetests, ebenfalls in docs/Betriebsbefehle.md Kap. 3; Taster-Diagramm Kap. 4.4).

**Noch offen:**

- **Achtung (gemessen 10.11.2026):** main.py ohne sudo crasht sofort beim Start: RuntimeError: ws2811_init failed with code -9 (Failed to create mailbox device), gefolgt von Segmentation fault (Aufräumcode der SWIG-Bindung nach fehlgeschlagenem strip.begin()). rpi_ws281x braucht root für den DMA-/Mailbox-Zugriff (dev/vcio) – manuelle Tests deshalb immer mit sudo, wie in docs/Betriebsbefehle.md beschrieben. Kandidat für Fallstrick 32 in der Bauanleitung (mit Kap.-7-Nachzug).
- Bauanleitung: ✅ nachgezogen 10.11.2026 – Kap. 7.11 (Erweiterung Stufe 1 + 2), Fallstricke 32 + 33, Taster-Kap. 1.6/4.4, Verdrahtungs-Warnung Kap. 5.1, Intro + Revision-Log.
- Stufe 4 (auf Pauls Go, zurückgestellt 11.11.2026): EierUhr-Fall-Animation (Modus 7, Design siehe Kap. 5), Modus 9 (Analog, erst am Gerät testen), Modus 10 (Pong, zuletzt). Offene Doku-Fragen Kap. 8: Analog-Modus 8.3, Tasten-Zuordnung 8.4.