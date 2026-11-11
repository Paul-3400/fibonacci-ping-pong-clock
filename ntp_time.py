# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""NTP-Zeitsynchronisation und lokale Zeit.

Fix 09.11.2026 (Fallstrick 30): sync_ntp() wertet die NTP-Antwort jetzt
selbst aus. Vorher wurde die Serverzeit abgefragt und verworfen - die Uhr
lief unbemerkt auf der Systemzeit, die nach einem frischen SD-Flash oft
noch nicht synchronisiert ist (bis systemd-timesyncd greift).
"""
import time as time_module
from datetime import datetime, timedelta, timezone
import ntplib
from config import NTP_SERVER, TIMEZONE

try:
    from zoneinfo import ZoneInfo
    _tz = ZoneInfo(TIMEZONE)          # Europe/Zurich inkl. Sommerzeit
except Exception:
    _tz = None                        # Fallback: Systemzeitzone

_ntp_client = ntplib.NTPClient()
_last_sync = None      # time.monotonic() des letzten erfolgreichen Syncs
_ntp_epoch = None      # NTP-Epoch (resp.tx_time) zu diesem Moment

def sync_ntp():
    """Synchronisiert die Uhrzeit ueber NTP. Gibt True bei Erfolg zurueck.

    Speichert die Serverzeit als Referenz-Epoch; get_local_time() rechnet
    ab da mit time.monotonic() weiter. monotonic() kann nicht springen -
    auch dann nicht, wenn systemd-timesyncd die Systemzeit unterdessen
    umstellen sollte.
    """
    global _last_sync, _ntp_epoch
    try:
        resp = _ntp_client.request(NTP_SERVER, version=3, timeout=2)
        _ntp_epoch = resp.tx_time
        _last_sync = time_module.monotonic()
        return True
    except Exception as e:
        print(f"NTP-Fehler: {e}")
        return False

def get_local_time_precise(offset_sec=0):
    """
    Gibt lokale Zeit als (hour, minute, second, millisekunde) zurueck -
    Stufe 4 (11.11.2026): Millisekunden fuer die EierUhr-Fall-Animation
    (Modus 7) und die Pong-Uhr (Modus 10), siehe
    docs/Erweiterungen_Anzeigemodi.md Kap. 5.

    Gleiche Referenz-Logik wie get_local_time(): NTP-Epoch +
    time.monotonic() (+ offset), Fallback auf Systemzeit vor dem ersten
    erfolgreichen Sync. Die Millisekunde kommt vom Bruchteil der Epoche
    (microsecond // 1000) - nicht aus einer zweiten Zeitquelle, damit
    Sekunde und Millisekunde nie auseinanderlaufen.
    """
    if _ntp_epoch is not None and _last_sync is not None:
        epoch = _ntp_epoch + (time_module.monotonic() - _last_sync) \
                + offset_sec
        jetzt = datetime.fromtimestamp(epoch, tz=timezone.utc)
        if _tz is not None:
            jetzt = jetzt.astimezone(_tz)
        else:
            jetzt = jetzt.astimezone()   # Systemzeitzone
        return jetzt.hour, jetzt.minute, jetzt.second, jetzt.microsecond // 1000
    # Fallback vor dem ersten Sync: Systemzeit
    now = datetime.now() + timedelta(seconds=offset_sec)
    return now.hour, now.minute, now.second, now.microsecond // 1000

def get_local_time(offset_sec=0):
    """
    Gibt lokale Zeit als (hour, minute, second) zurueck.
    offset_sec: Handbetrieb-Offset in Sekunden (Taster 2-4),
    0 = Normalbetrieb mit NTP-Zeit.

    Nach dem ersten erfolgreichen NTP-Sync laeuft die Uhr ausschliesslich
    auf der NTP-Referenz (unabhaengig von der Systemzeit). Vor dem ersten
    Sync: Fallback auf Systemzeit.
    Seit Stufe 4 (11.11.2026) delegiert diese Funktion an
    get_local_time_precise() - beide liefern garantiert dieselbe Sekunde.
    """
    stunde, minute, sekunde, _ms = get_local_time_precise(offset_sec)
    return stunde, minute, sekunde

def needs_resync(interval_min=30):
    """Prueft, ob eine NTP-Resynchronisation faellig ist."""
    if _last_sync is None:
        return True
    elapsed_min = (time_module.monotonic() - _last_sync) / 60
    return elapsed_min >= interval_min
