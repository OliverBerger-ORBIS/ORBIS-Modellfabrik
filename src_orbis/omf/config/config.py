import os

# Live (APS) ist Default – bitte Host/Port/Benutzer an eure Umgebung anpassen:
LIVE_CFG = {
    "host": os.getenv("OMF_LIVE_HOST", "192.168.0.100"),
    "port": int(os.getenv("OMF_LIVE_PORT", "1883")),
    "username": os.getenv("OMF_LIVE_USER", "default"),
    "password": os.getenv("OMF_LIVE_PASS", "default"),
    "client_id": "omf_dashboard_live",
    "keepalive": 60,
    "tls": False,
}

# Replay (optional, z. B. lokaler Mosquitto auf 1884, wenn keine APS-Verbindung verfügbar ist)
REPLAY_CFG = {
    "host": os.getenv("OMF_REPLAY_HOST", "localhost"),
    "port": int(os.getenv("OMF_REPLAY_PORT", "1884")),
    "username": os.getenv("OMF_REPLAY_USER", ""),
    "password": os.getenv("OMF_REPLAY_PASS", ""),
    "client_id": "omf_dashboard_replay",
    "keepalive": 45,
    "tls": False,
}
