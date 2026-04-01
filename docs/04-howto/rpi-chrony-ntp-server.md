# Shopfloor-RPi: chrony als NTP-Server (LAN)

**Zweck:** Arduino **OSF_MultiSensor_R4WiFi** im ORBIS-LAN holt UTC per **UDP/NTP (Port 123)**. Wenn **ausgehendes** Internet-NTP für den Arduino blockiert ist, stellt der **RPi** (gleiche IP wie Mosquitto, typisch **`192.168.0.100`**) die Zeit **im LAN** bereit — **chrony** synchronisiert sich weiterhin **nach außen** zu Pool-Servern.

**Voraussetzung:** SSH auf den RPi (z. B. `ssh ff22@192.168.0.100`), `sudo` ohne Passwort oder interaktiv.

---

## 1. systemd-timesyncd durch chrony ersetzen

`systemd-timesyncd` und **chrony** dürfen **nicht** gleichzeitig **UDP 123** nutzen. Üblich: Timesyncd entfernen, chrony installieren (Paketmanager löst das Abhängigkeitskonflikt).

```bash
sudo systemctl stop systemd-timesyncd
sudo systemctl disable systemd-timesyncd
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y chrony
```

---

## 2. LAN-Clients erlauben (NTP-Server-Modus)

Auf Raspberry Pi OS liest chrony Zusatzkonfiguration aus **`/etc/chrony/conf.d/`** (siehe `confdir` in `/etc/chrony/chrony.conf`).

**Wichtig:** Dateien **nicht** unter `chrony.conf.d` ablegen — dort liegt die **Hauptdatei** `chrony.conf`; die Drop-ins für `confdir` gehören nach **`/etc/chrony/conf.d/`**.

```bash
echo 'allow 192.168.0.0/24' | sudo tee /etc/chrony/conf.d/10-allow-lan.conf
sudo systemctl restart chrony
```

Nur einzelne Hosts (z. B. nur Arduino): `allow 192.168.0.95`.

---

## 3. Prüfen

```bash
chronyc tracking
chronyc sources -v
sudo ss -ulnp | grep ':123'
```

Erwartung: **`chronyd`** lauscht auf **`0.0.0.0:123`**; **Leap status** / **Stratum** zeigen gültige Synchronisation nach einigen Sekunden.

Test von einem anderen Rechner im LAN:

```bash
sntp -d 192.168.0.100
```

---

## 4. Arduino-Sketch

Ab **Sketch v1.1.7** ist **`192.168.0.100`** (Shopfloor-RPi) in **`WIFI_MODE_ORBIS`** als **erster** NTP-Server in `servers[]` und im Fallback in `resolveUtcEpochForPayload()` eingetragen — neu flashen nach RPi-Einrichtung.

Siehe `integrations/Arduino/OSF_MultiSensor_R4WiFi/OSF_MultiSensor_R4WiFi.ino`.

---

## 5. Docker / andere Dienste

chrony läuft als **systemd-Dienst** auf dem **Host** und startet beim Boot mit dem RPi. Bestehende **Docker-Container** bleiben unberührt; es gibt keinen Portkonflikt, solange **kein** weiterer Dienst **UDP 123** auf dem Host bindet.
