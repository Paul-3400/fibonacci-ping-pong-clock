<!-- Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026 -->
<!-- Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo) -->

# ⌨️ Betriebsbefehle – Fibonacci Ping-Pong-Uhr

Kurzreferenz zum Steuern und Überwachen der Uhr auf dem Raspberry Pi Zero WH.
Alle Befehle sind auf dem Pi selbst auszuführen (Konsole vor Ort oder remote
über Raspberry Pi Connect bzw. SSH: `ssh paul-rppi@RpPiZeroW-001.local`).

**Voraussetzungen:** Benutzer `paul-rppi`, Host `RpPiZeroW-001`,
Projektordner `~/fibonacci-clock` mit virtuellem Umfeld `venv`,
systemd-Dienst `fibonacci-clock` (Autostart, siehe Bauanleitung Kap. 7.10).

## Die fünf wichtigsten Befehle

| Zweck | Befehl |
|---|---|
| Läuft die Uhr? | `systemctl status fibonacci-clock` |
| Uhr anhalten (vor manuellen Tests!) | `sudo systemctl stop fibonacci-clock` |
| Uhr wieder starten | `sudo systemctl start fibonacci-clock` |
| Log live mitverfolgen | `journalctl -u fibonacci-clock -f` |
| Neue Software laden und neu starten | `cd ~/fibonacci-clock && git pull && sudo systemctl restart fibonacci-clock` |

## 1. Dienst steuern (systemd)

| Befehl | Wirkung |
|---|---|
| `systemctl status fibonacci-clock` | Zustand, Laufzeit seit Start, letzte Logzeilen |
| `systemctl is-active fibonacci-clock` | Nur `active` / `inactive` / `failed` |
| `sudo systemctl start fibonacci-clock` | Uhr starten |
| `sudo systemctl stop fibonacci-clock` | Uhr anhalten – **immer vor manuellen Tests** |
| `sudo systemctl restart fibonacci-clock` | Neu starten (z. B. nach `git pull`) |
| `sudo systemctl enable fibonacci-clock` | Autostart beim Boot einschalten |
| `sudo systemctl disable fibonacci-clock` | Autostart ausschalten |
| `systemctl is-enabled fibonacci-clock` | Ist Autostart aktiv? |

> Der Dienst läuft als root (rpi_ws281x braucht GPIO/DMA-Zugriff) – Start,
> Stopp und Neustart brauchen `sudo`, reine Abfragen wie `status` nicht.

## 2. Logs lesen (journalctl)

| Befehl | Wirkung |
|---|---|
| `journalctl -u fibonacci-clock -f` | Live mitschauen (beenden mit Strg+C) |
| `journalctl -u fibonacci-clock -n 100` | Letzte 100 Zeilen |
| `journalctl -u fibonacci-clock --since today` | Alles seit Mitternacht |
| `journalctl -u fibonacci-clock -b` | Alles seit dem letzten Boot |
| `journalctl -u fibonacci-clock -p err -b` | Nur Fehler seit dem letzten Boot |
| `journalctl -u fibonacci-clock --disk-usage` | Speicherplatz der Logs |

Typische Logzeilen im Regelbetrieb:

```
Zeit: 10:35 – Felder: {0: 'both', 1: 'hours', 2: 'both', 3: 'off', 4: 'off'}
Base4: 10:35
Feldmodus: A (Wert 5)
```

`off` = Feld dunkel – das ist normal und kein Fehler.

## 3. Manuelle Tests (Service vorher stoppen!)

Dienst und Testprogramm würden sich die GPIOs streitig machen – deshalb zuerst:

```bash
sudo systemctl stop fibonacci-clock
```

**Standard-Sequenz «neue Software am Gerät testen» (11.11.2026):**

```bash
sudo systemctl stop fibonacci-clock
cd ~/fibonacci-clock && git pull
sudo venv/bin/python3 main.py
```

Dienst stoppen → Software aktualisieren → Hauptprogramm im Vordergrund
testen (Modi über die Taster, Ende mit Strg+C). Danach den Dienst wieder
starten: `sudo systemctl start fibonacci-clock`.

Alle Testbefehle im Projektordner `~/fibonacci-clock`:

| Zweck | Befehl |
|---|---|
| Hauptprogramm im Vordergrund (Ende mit Strg+C) | `sudo venv/bin/python3 main.py` |
| Steuerbox-Selbsttest (Uhrzeit + Tasten T1–T6) | `venv/bin/python3 steuerbox_test.py` |
| Anzeige-Test (T6 = Anzeige ein/aus, T1–T5 = Einzelfelder) | `sudo venv/bin/python3 anzeige_test.py` |

`main.py` und `anzeige_test.py` brauchen sudo (NeoPixel über rpi_ws281x);
`steuerbox_test.py` läuft ohne – bei Rechte-Fehlern einfach sudo voransetzen.

**TM1637-Roh-Befehl** (schreibt '123456' direkt aufs Modul, ohne sudo):

```bash
venv/bin/python3 -c "import tm1637; d=tm1637.TM1637(clk=23,dio=24); d.brightness(4); d.write(d.encode_string('123456'),0)"
```

> **Erwartete Anzeige: «321654»** – das 6-stellige Modul spiegelt die
> Segmentliste je Hälfte (Fallstrick 31, Bauanleitung Kap. 12). Der Roh-Befehl
> umgeht die Korrektur in `tm1637_display.py`; die Uhr selbst zeigt die
> Zeit korrekt. «321654» ist also der Beweis, dass das Modul funktioniert.

Danach nicht vergessen:

```bash
sudo systemctl start fibonacci-clock
```

## 4. Zeit & NTP prüfen

| Befehl | Wirkung |
|---|---|
| `timedatectl` | Lokale Zeit, Zeitzone, Synchronisations-Status |
| `date` | Aktuelle Systemzeit |

Erwartung im Regelbetrieb: `System clock synchronized: yes`,
`NTP service: active`, Zeitzone `Europe/Zurich`. Die Uhr holt sich alle
30 Minuten frische NTP-Zeit (`ch.pool.ntp.org`, siehe `config.py`).
Erscheint beim Start `WARNUNG: NTP-Sync fehlgeschlagen`, läuft die Uhr
vorerst mit der Systemzeit weiter und synchronisiert sich später selbst.

## 5. Software aktualisieren

```bash
cd ~/fibonacci-clock
git pull
sudo systemctl restart fibonacci-clock
```

Danach kontrollieren: `systemctl status fibonacci-clock` – und kurz prüfen,
ob Tafel und TM1637 wieder anzeigen.

## 6. System-Überwachung

| Befehl | Wirkung |
|---|---|
| `vcgencmd measure_temp` | CPU-Temperatur (dauerhaft über ~70 °C = untersuchen) |
| `free -h` | Speicherverbrauch |
| `df -h` | Speicherplatz auf der SD-Karte |
| `uptime` | Laufzeit seit Boot, durchschnittliche Last |
| `top` | Prozesse live (beenden mit `q`) |
| `hostname -I` | IP-Adresse(n) des Pi |

## 7. Notfall-Anker

Macht der Dienst beim Boot Ärger, kann man ihn für den nächsten Boot
ausser Kraft setzen, ohne ihn zu deinstallieren:

| Befehl | Wirkung |
|---|---|
| `sudo systemctl mask fibonacci-clock` | Dienst wird beim Boot übergangen (gesperrt) |
| `sudo systemctl unmask fibonacci-clock` | Sperre aufheben |

Hilft das nicht mehr (Pi bootet nicht mehr sauber): SD-Karte am anderen
Rechner mounten und in `cmdline.txt` den Rettungsanker
`systemd.mask=fibonacci-clock.service` anhängen (Bauanleitung Kap. 12,
Fallstrick 29), booten, Problem beheben, Anker wieder entfernen.

---

Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 10.11.2026
