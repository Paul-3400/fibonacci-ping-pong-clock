# Helligkeit der Tafel: Justage & LDR-Automatik

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 11.11.2026
Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)

Status: **Phase 1 (manuelle Justage) umgesetzt** – Stub-Tests bestanden
(`test_helligkeit.py`, 56 Checks), **Gerätetest offen**. Phase 2
(LDR-Automatik) geplant, siehe Kap. 3.

## 1. Warum

Die 40 NeoPixel laufen standardmässig mit `LED_BRIGHTNESS = 102` von 255 –
das sind ca. 40 %, gut als Grundwert, aber abends zu hell und je nach Modus
unterschiedlich empfindlich. Ziel: die Helligkeit direkt an der Uhr
einstellen können (Phase 1) und sie später automatisch der Raumhelligkeit
anpassen (Phase 2, LDR/Lux-Sensor).

## 2. Phase 1: Manuelle Justage (11.11.2026)

| Schritt | Bedienung | TM1637 |
|---|---|---|
| Justage starten | **T1 lang** (≥ 1 s) | «br40» (b = brightness, Prozent) |
| Dunkler | **T2 kurz oder halten** (−5 % je Schritt) | z. B. «br35», «br 5» |
| Heller | **T3 kurz oder halten** (+5 % je Schritt) | z. B. «br45», «br100» |
| Beenden | nochmals **T1 lang** oder **T1 kurz** | Uhrzeit (HH:MM:SS) |
| Beenden (automatisch) | 10 s lang nichts tun (`HELL_TIMEOUT_SEC`) | Uhrzeit |

- Bereich **5–100 %** in 5-%-Schritten (Entscheid Paul, 11.11.2026);
  40 % entspricht dem Rohwert 102 – identisch mit dem bisherigen festen
  `LED_BRIGHTNESS`, am Startzustand ändert sich also nichts.
- Während der Justage sind Moduswahl (T1–T5 kurz) und Zeitverstellung
  (T2–T5 lang) unterdrückt: T2/T3 stellen die Helligkeit, T4/T5 tun
  nichts – kein versehentlicher Moduswechsel. T6 (Shift) bleibt möglich.
- Der Wert wird **bei jedem Schritt gespeichert** (`helligkeit.txt` im
  Projektordner) und überlebt den Reboot. Fehlt die Datei oder ist sie
  unlesbar («abc») oder ausserhalb des Bereichs, greift der Default 40 % –
  die Uhr startet nie ohne Anzeige.
- Die **Boot-Rampe bleibt** (Fallstrick 29): Von `SOFTSTART_BRIGHTNESS`
  stufenweise hoch zum Zielwert. Aenderungen zur Laufzeit (Justage)
  setzen sofort um – die Schritte sind klein (5 %), kein Last-Schlag
  fürs Netzteil.
- LED-Last: 100 % weiss ≈ 2,4 A am 4-A-Netzteil der Tafel – im Rahmen.
  Der Skalenwert gilt global für alle 40 LEDs (`strip.setBrightness`).
- TM1637-Zeichensatz (depklyon) hat kein «+», deshalb «br» als Präfix –
  alle Feedbacks sind zeichensatzsicher (im Stub-Test geprüft).

### Software

| Datei | Änderung |
|---|---|
| `helligkeit.py` | **neu**: Prozent-Verwaltung (`lese_prozent`, `schreibe_prozent`, `anpassen`, `prozent_raw`, `ziel_raw`) – der eine Ort, der die Ziel-Helligkeit definiert; Ankerpunkt für die LDR-Automatik in Phase 2 |
| `config.py` | ergänzt: `HELL_SCHRITT_PCT` (5), `HELL_MIN_PCT` (5), `HELL_MAX_PCT` (100), `HELL_DEFAULT_PCT` (40), `HELL_TIMEOUT_SEC` (10), `HELL_DATEI`; Taster-Kommentare nachgezogen (T1 lang = Justage) |
| `buttons.py` | T1 mit `hold_time` (Langdruck, kein `hold_repeat`) → Justage-Toggle; Justage-Zustand mit Timeout in `poll()` (analog Shift); T2/T3 kurz und lang = ±5 %; T4/T5 in der Justage ignoriert; Feedback «brNN» |
| `main.py` | Zielwert je Loop aus `helligkeit.ziel_raw()`; Boot-Rampe bis zum Ziel, danach sofortige Umsetzung; Log-Zeile je manueller Aenderung (für `journalctl`) |
| `test_helligkeit.py` | **neu**: Stub-Tests ohne Hardware (Fake-gpiozero, gepatchte Uhr) |

### Verifikation

Stub-Test `test_helligkeit.py`, **56 Checks bestanden** (11.11.2026):

- G1 `helligkeit.py` (14 Checks): Mapping Prozent → Rohwert
  (40 % → 102, 5 % → 12, 100 % → 255), int-Typ (Fallstrick 27),
  Datei-Roundtrip, Fallbacks (Datei fehlt / «abc» / Wert 150),
  Clamping bei 5 und 100 %.
- G2 `buttons.py` (34 Checks): komplette Taster-Logik mit Fake-gpiozero –
  Justage starten/beenden (T1 lang Toggle, T1 kurz), Timeout nach 10 s,
  Timeout-Verlängerung bei Aktivität, ±5 % kurz und wiederholend lang,
  kein Doppel-Schritt nach Loslassen, T4/T5 ignoriert, kein Moduswechsel,
  Shift möglich, Zeitverstellung unterdrückt und danach wieder intakt
  (+1 min, NORM), «brNN»-Feedbacks.
- G3 Konfiguration (8 Checks): Bereich-Konsistenz (5 < 40 ≤ 100),
  Timeout = 10 s, alle Feedbacks TM1637-darstellbar (Regex gegen den
  Zeichensatz des depklyon-Treibers).

## 3. Phase 2: LDR-Automatik (geplant)

Der Pi Zero 2 W hat **keinen analogen Eingang** – drei sinnvolle Wege:

| Lösung | Aufwand | Präzision | Bemerkung |
|---|---|---|---|
| **BH1750-Lichtsensor (I2C)** – Empfehlung | ~3–5 CHF + 4 Drähte | hoch | Lux-Wert fertig kalibriert, digitale I²C-Schnittstelle (GPIO 2/3, Pull-ups sind auf dem Modul), Bibliotheken vorhanden |
| KY-018-LDR-Modul + Kondensator | ~1–2 CHF | mittel | Ladezeit-Trick (RCTime) direkt am GPIO – kein ADC nötig, driftet aber und muss selbst kalibriert werden |
| ADS1115 (I²C-ADC) + LDR-Spannungsteiler | ~8–12 CHF | hoch | für Puristen; mehr Bauteile und Konfiguration |

Design-Vorschlag (Stand 11.11.2026, Konfidenz mittel – Details bei der
Umsetzung festzurren):

- `helligkeit.py` bekommt einen AUTOMATIK-Modus: Sensorwert → Lux →
  **Prozent über eine Log-Kurve**, z. B. Dunkelraum 10 lux → 10 %,
  Raumlicht 300 lux → 50 %, Tageslicht 10 000 lux → 100 %. Logarithmisch,
  weil die Augenempfindlichkeit ebenfalls logarithmisch arbeitet.
- **Hysterese ±5 %** und Update alle 30 s – kein Flackern an
  Grenzwerten; Übergänge sanft (ca. ±1 %/s statt Sprüngen).
- Manuelle Justage (T1 lang + T2/T3) schaltet auf MANUELL und
  überschreibt – die Schnittstelle `ziel_raw()` bleibt für `main.py`
  unverändert, nur die Quelle dahinter ändert sich.

## 4. Gerätetest (offen)

```bash
sudo systemctl stop fibonacci-clock
cd ~/fibonacci-clock && git pull
sudo venv/bin/python3 main.py
```

Prüfen:

1. Langdruck T1 → TM1637 zeigt «br40».
2. T2/T3 kurz und halten → Tafel wird sichtbar dunkler/heller,
   TM1637 zählt in 5er-Schritten mit.
3. T4/T5 drücken während der Justage → keine Reaktion (kein Moduswechsel).
4. Reboot → Wert bleibt (Datei `helligkeit.txt` im Projektordner).
5. Normale Tasterfunktion (Moduswahl, +1 min, NORM) nach der Justage intakt.
