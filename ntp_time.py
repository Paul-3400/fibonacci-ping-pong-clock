# Autor: Paul Simmen mit Vibe (GLM-5-latest-short), 08.11.2026
# Lizenz: GNU GPL v2 (abgeleitet von github.com/pchretien/fibo)
# Projekt fibonacci-ping-pong-clock - Code-Entwurf aus der Bauanleitung Kap. 7
"""NTP-Zeitsynchronisation und lokale Zeit."""
import ntplib
import datetime
import time as time_module
from config import NTP_SERVER, TIMEZONE

_ntp_client = ntplib.NTPClient()
_last_sync = None

def sync_ntp():
    """Synchronisiert Zeit über NTP. Gibt True bei Erfolg zurück."""
    global _last_sync
    try:
        resp = _ntp_client.request(NTP_SERVER, version=3)
        _last_sync = time_module.time()
        return True
    except Exception as e:
        print(f"NTP-Fehler: {e}")
        return False

def get_local_time(offset_sec=0):
    """
    Gibt lokale Zeit als (hour, minute, second) zurück.
    offset_sec: Handbetrieb-Offset in Sekunden (Taster 2–4),
    0 = Normalbetrieb mit NTP-Zeit.
    """
    # Europe/Zurich: UTC+1 (Winter) oder UTC+2 (Sommer)
    # Python datetime nutzt System-Zeitzone (muss konfiguriert sein)
    now = datetime.datetime.now() + datetime.timedelta(seconds=offset_sec)
    return now.hour, now.minute, now.second

def needs_resync(interval_min=30):
    """Prüft, ob eine NTP-Resynchronisation fällig ist."""
    global _last_sync
    if _last_sync is None:
        return True
    elapsed_min = (time_module.time() - _last_sync) / 60
    return elapsed_min >= interval_min
