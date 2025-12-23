# ROBO Pro Coding - Troubleshooting

**Datum:** 22.12.2025  
**Problem:** Projekte können nicht in ROBO Pro Coding geöffnet werden

## 🚨 Bekanntes Problem

**Symptom:** ROBO Pro Coding findet/öffnet Projekte nicht  
**Status:** ROBO Pro Coding erkennt Controller im WLAN ✅  
**Mögliche Ursache:** ROBO Pro Coding will Update machen (nicht gewünscht) oder Projekte können nicht geöffnet werden

## 🔍 Diagnose

### Problem 1: ROBO Pro Coding Update-Anfrage

**Symptom:** ROBO Pro Coding erkennt Controller, möchte aber ein Update durchführen  
**Lösung:** Update ablehnen, SSH-Methode verwenden (siehe unten)

**Hinweis:** Wenn SSH/SCP funktionieren, liegt es **NICHT** am Router oder Netzwerk-Firewall!

**Bekannte Probleme:**
- ROBO Pro Coding erkennt Controller im WLAN ✅
- ROBO Pro Coding möchte Update machen (nicht gewünscht)
- Projekte können möglicherweise nicht geöffnet werden (aus anderen Gründen)

**Mac Firewall (möglich, aber unwahrscheinlich):**
- System Preferences → Security & Privacy → Firewall
- Prüfen, ob Firewall aktiviert ist
- ROBO Pro Coding zu erlaubten Apps hinzufügen

### Problem 2: Netzwerk-Verbindung

**Prüfen:**
```bash
# Controller erreichbar?
ping <TXT-IP>

# Port 22 (SSH) offen?
nc -zv <TXT-IP> 22

# Port 80 (HTTP) offen?
nc -zv <TXT-IP> 80
```

### Problem 3: ROBO Pro Coding Einstellungen

**Prüfen:**
- ROBO Pro Coding → Preferences → Network
- Controller-IP-Adresse korrekt?
- Verbindungsmethode (USB/WLAN) korrekt gewählt?

---

## 🔧 Lösungsansätze

### Lösung 1: ROBO Pro Coding Update-Anfrage umgehen

**Problem:** ROBO Pro Coding erkennt Controller, möchte aber Update machen  
**Lösung:** SSH-Methode verwenden (siehe Lösung 4)

**Alternative (falls Update gewünscht):**
- ROBO Pro Coding Update durchführen
- Danach Projekte öffnen

**Hinweis:** Router-Firewall ist **NICHT** das Problem, da SSH/SCP funktionieren!

### Lösung 2: Netzwerk-Verbindung prüfen

```bash
# Alle Controller testen
for ip in 192.168.0.{101,102,107,158}; do
  echo "Testing $ip..."
  ping -c 1 $ip
done
```

### Lösung 3: ROBO Pro Coding neu starten

1. ROBO Pro Coding komplett beenden
2. Neu starten
3. Controller erneut verbinden

### Lösung 4: Alternative: Direkt über SSH/SCP (EMPFOHLEN)

**Wenn ROBO Pro Coding Update machen will oder Projekte nicht öffnet:**
- ✅ SSH-Verbindung verwenden (siehe `TXT-SOURCE-COPY-PROCESS.md`)
- ✅ Dateien direkt kopieren
- ✅ Keine ROBO Pro Coding-Abhängigkeit
- ✅ Umgeht Update-Anfrage
- ✅ Funktioniert zuverlässig im WLAN

---

## ✅ Empfohlene Vorgehensweise

**Wenn ROBO Pro Coding Update machen will oder Projekte nicht öffnet:**

1. **SSH-Methode verwenden** (siehe `TXT-SOURCE-COPY-PROCESS.md`) ⭐ EMPFOHLEN
   - ✅ Funktioniert immer (wenn SSH aktiviert)
   - ✅ Keine ROBO Pro Coding-Abhängigkeit
   - ✅ Schneller und zuverlässiger
   - ✅ Umgeht Update-Anfrage
   - ✅ Funktioniert im WLAN

2. **ROBO Pro Coding Update durchführen** (falls gewünscht)
   - Update akzeptieren
   - Danach Projekte öffnen

3. **ROBO Pro Coding für visuelle Programmierung**
   - Nur wenn Update durchgeführt wurde
   - Oder für Blockly-Programmierung

---

## 📝 Notizen

**Wichtig:** 
- ✅ ROBO Pro Coding erkennt Controller im WLAN
- ⚠️ ROBO Pro Coding möchte Update machen (nicht gewünscht)
- ✅ SSH-Methode ist zuverlässiger als ROBO Pro Coding
- ✅ **Wenn SSH/SCP funktionieren, liegt es NICHT am Router/Firewall**
- ✅ Direkter SSH-Zugriff funktioniert immer (wenn aktiviert)
- ✅ SSH-Methode umgeht ROBO Pro Coding Update-Anfrage

