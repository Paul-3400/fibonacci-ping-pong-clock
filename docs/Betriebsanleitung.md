# Die Fibonacci Ping-Pong-Uhr – Betriebsanleitung

> Handout für Besucherinnen und Besucher: Wie Sie die Uhr mit den 40
> leuchtenden Ping-Pong-Bällen lesen und bedienen. Stand: 11.11.2026

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 11.11.2026
Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibao)

---

## 1. Was Sie hier sehen?

Eine Uhr der besonderen Art: **40 leuchtende Ping-Pong-Bälle** bilden
eine Tafel aus 5 Spalten und 8 Reihen. Je nach Anzeige-Modus leuchten
andere Bälle in **rot, grün, blau, gelb oder orange** – daraus lässt
sich die Uhrzeit ablesen. Ein kleines rotes Digital-Display zeigt die
Zeit zusätzlich im Klartext, falls Sie beim Entziffern Hilfe brauchen.

Die Zeit holt sich die Uhr automatisch aus dem Internet – sie geht
also immer richtig, auch nach einem Stromausfall.

## 2. Bedienung: die Taster

| Taster | kurzer Druck | Langdruck (ca. 1 s) |
|---|---|---|
| **T1** | Anzeige 1: Fibonacci-Uhr | Helligkeit einstellen (Kap. 4) |
| **T2** | Anzeige 2: Base4-Uhr | Zeitjustage (für den Hausherrn) |
| **T3** | Anzeige 3: Binärzähler | Zeitjustage (für den Hausherrn) |
| **T4** | Anzeige 4: Grosse Ziffern | Zeitjustage (für den Hausherrn) |
| **T5** | Anzeige 5: Tagesfortschritt | zurück in den Normalbetrieb |
| **T6** | Shift-Taste | – |

- **T6 (Shift)** zuerst drücken, dann innerhalb von 10 Sekunden T1–T5:
  damit wählen Sie die **Anzeigen 6–10**.
- Probieren Sie ruhig alles aus: Mit den Tastern kann nichts
  kaputtgehen. Nach dem Einschalten startet die Uhr immer mit
  Anzeige 1 (Fibonacci).

## 3. Die zehn Anzeigen – so lesen Sie die Uhr

### Anzeige 1: Fibonacci-Uhr (T1)

Die Tafel ist in fünf Flächen aufgeteilt, mit den Werten
**5, 3, 2, 1 und 1** (die Fibonacci-Folge).

| Farbe | Bedeutung |
|---|---|
| **rot** | zählt zur **Stunde** |
| **grün** | zählt zu den **Minuten** (Wert × 5) |
| **blau** | zählt zu **beidem** |

So gehen Sie vor: Leuchtende Flächen je Farbe zusammenzählen –
rot/blau ergibt die Stunde (12-Stunden-Format), grün/blau die Minuten
mal 5.

**Beispiel:** blau leuchtet die Fläche «2», grün die Fläche «5».
Stunde: 2 → es ist 2 Uhr (14 Uhr). Minuten: (5 + 2) × 5 = **14:35**.

Die Uhr wählt die Flächen unter allen gültigen Kombinationen zufällig
aus – das Bild kann bei gleicher Zeit anders aussehen, die Uhrzeit
stimmt immer.

### Anzeige 2: Base4-Uhr (T2)

Oben auf der Tafel leuchten bis zu **9 Bälle in einem 3×3-Quadrat**.
Jeder Ball hat einen festen Wert:

```
48   12    3
32    8    2
16    4    1
```

**rot** zusammenzählen = Stunde (0–24), **grün** zusammenzählen =
Minute (minutengenau!), **gelb** zählt zu beidem.

**Beispiel 14:35:** rot 12 + 2 (= 14), grün 32 + 3 (= 35).

### Anzeige 3: Binärzähler (T3)

Drei senkrechte Reihen: **rot** = Stunde, **grün** = Minute,
**gelb** = Sekunde. Jede Reihe ist ein Binärzähler – von unten nach
oben verdoppelt sich der Wert: **1, 2, 4, 8, 16, (32)**. Die Werte der
leuchtenden Bälle je Reihe zusammenzählen.

**Beispiel grüne Reihe:** unten (1) und an vierter Stelle von unten (4)
leuchten → 5 Minuten.

### Anzeige 4: Grosse Ziffern (T4)

Eine **riesige Ziffer** füllt die ganze Tafel. Die vier Ziffern der
Uhrzeit wechseln sich alle 2 Sekunden ab: erst die **Stunden**
(**rot**), dann die **Minuten** (**grün**). Der weisse Punkt unten in
der Mitte blinkt im Sekundentakt mit.

### Anzeige 5: Tagesfortschritt (T5)

Die Bälle füllen sich in Kettenreihenfolge von oben links nach unten
rechts. **Jeder Ball steht für ca. 36 Minuten des Tages.** Die Farbe
zeigt die Tageszeit: **blau** Nacht (bis 6 Uhr), **orange** Morgen
(6–9), **gelb** Tag (9–17), **rot** Abend (17–21), **blau** Nacht
(ab 21 Uhr).

### Anzeige 6: Binär-BCD (Shift + T1)

Jede Ziffer einzeln in Binär: **rot** die beiden Stunden-Ziffern,
**grün** die beiden Minuten-Ziffern, **gelb** die Einer-Ziffer der
Sekunden. Pro Reihe gilt wieder unten = 1, dann 2, 4, 8 …

### Anzeige 7: EierUhr (Shift + T2) – der Eierkoch-Timer

Eine Sanduhr mit **6 gelben Kugeln und gedimmtem Glas-Rahmen**.
Alle 30 Sekunden fällt eine Kugel von oben nach unten – in der
Fallssekunde sieht man das Korn durch die Taille wandern.

**So kochen Sie ein Perfektes Ei:**

1. Warten Sie, bis oben wieder alle **6 Kugeln** erscheinen
   (Beginn des 3-Minuten-Zyklus).
2. Jetzt das Ei in den Kocher geben.
3. Sobald die letzte Kugel unten angekommen ist: **3 Minuten sind um –
   Ei herausnehmen!**

### Anzeige 8: Sekunden-Serpentine (Shift + T3)

Die laufende Minute füllt die Tafel wie eine Schlange: In den ersten
40 Sekunden wächst eine **grüne** Kette ball für ball, ab Sekunde 40
füllt eine **orange** Kette die Tafel ein zweites Mal (die grüne
bleibt gedimmt stehen). Wenn die orange Kette den letzten Ball
erreicht, ist die Minute voll.

### Anzeige 9: Analog-Uhr (Shift + T4)

Eine grobe **Zeigeruhr**: Die **rote** LED zeigt die Stunde, die
**grüne** die Minute im 5-Minuten-Raster. Sitzen beide auf derselben
LED, leuchtet sie **gelb**. Die vier schwach weissen Punkte markieren
die Positionen 12, 3, 6 und 9.

### Anzeige 10: Pong-Uhr (Shift + T5)

Das klassische Ping-Pong-Spiel als Uhr: **Drehen Sie die Uhr um 90°
im Uhrzeigersinn** – dann ist die schmale Spalte oben. Ein Lichtpunkt
(Ball) springt zwischen den beiden **roten Schlägern** hin und her.
In den letzten 5 Sekunden jeder Minute erscheint der Spielstand:
erst die **Stunde in rot**, dann die **Minuten in grün** (je 2,5 s).

## 4. Helligkeit einstellen

1. **T1 lang drücken** – das Display zeigt «br» mit dem Prozentwert.
2. **T2** drücken = dunkler, **T3** drücken = heller (Schritte 5 %).
3. Beenden: **T1 lang drücken** oder 10 Sekunden warten – die
   Einstellung bleibt gespeichert.

## 5. Gut zu wissen

- Die Uhr stellt sich über das Internet automatisch (NTP).
- Nach einem Stromausfall startet sie von selbst im
  Fibonacci-Modus (Anzeige 1).
- Das kleine Display zeigt während der Bedienung kurz an, was die
  Taster gewählt haben.
- Technische Details, Bau und Programmierung: siehe Bauanleitung
  (docs/Fibonacci_PingPong_Uhr_Bauanleitung.md) im Projekt-Repo.

Viel Vergnügen beim Uhr-Entziffern – und beim Eierkochen!
