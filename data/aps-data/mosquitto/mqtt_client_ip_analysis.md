# MQTT Client IP-Adressen Analyse

## 🌐 **IP-Adressen zu Modulen Mapping**

### **Docker-Container (172.18.0.x)**
- **172.18.0.3** - Node-RED Container (CCU)
  - `nodered_686f9b8f3f8dbcc7` (Haupt-CCU)
  - `nodered_55ae85707039403b`
  - `nodered_678002a407768a21`
  - `nodered_8f16f8e84439a9b0`
  - `nodered_847bd1b7099daa53`

- **172.18.0.5** - MQTT.js Container (Dashboard/Web)
  - `mqttjs_1802b4e7` (Haupt-Dashboard)
  - `mqttjs_39cbd4d4`

### **APS-Module (192.168.0.1xx)**
- **192.168.0.101** - Modul 1
  - `auto-89001F62-1074-0CEA-8F65-56687DFE1478`
  - `auto-B5711E2C-46E0-0D7B-90E6-AD95D8831099` (Logger/Recorder)

- **192.168.0.102** - Modul 2
  - `auto-84E1E526-F6B8-423D-8FEB-8ED1C3ECCD3C` (TXT-Controller)
  - `auto-3FFF7725-6D3F-09E6-F177-F10247BC8677`

- **192.168.0.103** - OMF Dashboard
  - `omf_dashboard_live` (OMF Dashboard)
  - `auto-32797BEF-4845-E39E-2A53-DBD7C903B7CE`
  - `auto-3A4AF5B2-D08E-97BA-E1AD-A7791A9F43B1`
  - `auto-81339D60-F02A-89EC-A169-F4FB38401ED4`
  - `auto-A571E3E9-6DEF-6D12-2F44-5CBA1AC1B2B0`
  - `auto-FEE5AA66-B68C-89BA-3875-D9C4FA03F090`

- **192.168.0.104** - Modul 4
  - `auto-C008CD41-06FC-EBC3-9F4C-E55802706B98`
  - `auto-BB4B3A28-3418-7CE4-D90A-1916D9B7DD3B`

- **192.168.0.105** - Modul 5 (FTS)
  - `auto-6F23F61F-54AE-0F34-5066-D3068F32B88B`
  - `auto-1F9067F2-0143-7A00-46AA-166AC0706A31`
  - `auto-29CDD50B-3CD8-12C8-577C-01DA62832C5F`

### **Web-Clients (::ffff:192.168.0.103)**
- `client-txo4qkcff6`
- `client-5xg72ydquas`
- `client-cal89ypr2ys`
- `client-ofpcy1zv0si`

## 📊 **Zusammenfassung**

**Identifizierte Module:**
- **TXT-Controller:** 192.168.0.102 (auto-84E1E526...)
- **Logger/Recorder:** 192.168.0.101 (auto-B5711E2C...)
- **OMF Dashboard:** 192.168.0.103 (omf_dashboard_live)
- **FTS:** 192.168.0.105 (mehrere auto-... Clients)
- **Weitere Module:** 192.168.0.101, 192.168.0.104

**Docker-Services:**
- **Node-RED (CCU):** 172.18.0.3
- **MQTT.js Dashboard:** 172.18.0.5

**Web-Clients:** 192.168.0.103 (IPv6-mapped IPv4)

