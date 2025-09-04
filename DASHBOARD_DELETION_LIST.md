# Dashboard Deletion List - Original Dashboard Dateien

## 🎯 **Zweck:**
Diese Liste enthält alle Original-Dashboard-Dateien, die gelöscht werden sollen, um Platz für die finale Migration von Dashboard2 zu Dashboard zu schaffen.

## ⚠️ **WICHTIG:**
- **Commit Hash vor Löschung:** `756c9b8` (Dashboard2 Live-Test erfolgreich)
- **Branch:** `debug/steering-b6e579b`
- **Wiederherstellung:** `git reset --hard 756c9b8` (falls nötig)

## 📁 **Zu löschende Original-Dashboard-Dateien:**

### **Haupt-Dashboard:**
```
src_orbis/omf/dashboard/
├── omf_dashboard.py                    # Original Haupt-Dashboard
```

### **Original Components:**
```
src_orbis/omf/dashboard/components/
├── overview.py                         # Original Overview (monolithisch)
├── settings.py                         # Original Settings (monolithisch)
├── factory_steering.py                 # Original Factory Steering
├── generic_steering.py                 # Original Generic Steering
├── message_center.py                   # Original Message Center
├── steering.py                         # Original Steering Wrapper
```

### **Zu behaltende Dashboard2-Dateien:**
```
src_orbis/omf/dashboard/
├── omf_dashboard2.py                   # → wird zu omf_dashboard.py
```

### **Zu behaltende Dashboard2 Components:**
```
src_orbis/omf/dashboard/components/
├── overview2.py                        # → wird zu overview.py
├── settings2.py                        # → wird zu settings.py
├── steering2.py                        # → wird zu steering.py
├── message_center2.py                  # → wird zu message_center.py
├── order2.py                           # → wird zu order.py
├── overview_module_status.py           # Sub-Komponente (behalten)
├── overview_order.py                   # Sub-Komponente (behalten)
├── overview_order_raw.py               # Sub-Komponente (behalten)
├── overview_inventory.py               # Sub-Komponente (behalten)
├── order_management.py                 # Sub-Komponente (behalten)
├── order_current.py                    # Sub-Komponente (behalten)
├── steering_factory.py                 # Sub-Komponente (behalten)
├── steering_generic.py                 # Sub-Komponente (behalten)
├── settings_dashboard.py               # Sub-Komponente (behalten)
├── settings_modul_config.py            # Sub-Komponente (behalten)
├── settings_nfc_config.py              # Sub-Komponente (behalten)
├── settings_mqtt_config.py             # Sub-Komponente (behalten)
├── settings_topic_config.py            # Sub-Komponente (behalten)
└── settings_message_templates.py       # Sub-Komponente (behalten)
```

## 🗑️ **Löschungs-Befehle:**

### **Schritt 1: Original Haupt-Dashboard löschen**
```bash
rm src_orbis/omf/dashboard/omf_dashboard.py
```

### **Schritt 2: Original Components löschen**
```bash
rm src_orbis/omf/dashboard/components/overview.py
rm src_orbis/omf/dashboard/components/settings.py
rm src_orbis/omf/dashboard/components/factory_steering.py
rm src_orbis/omf/dashboard/components/generic_steering.py
rm src_orbis/omf/dashboard/components/message_center.py
rm src_orbis/omf/dashboard/components/steering.py
```

## 🔄 **Umbenennungs-Befehle (nach Löschung):**

### **Schritt 3: Dashboard2 zu Dashboard umbenennen**
```bash
# Haupt-Dashboard
mv src_orbis/omf/dashboard/omf_dashboard2.py src_orbis/omf/dashboard/omf_dashboard.py

# Components
mv src_orbis/omf/dashboard/components/overview2.py src_orbis/omf/dashboard/components/overview.py
mv src_orbis/omf/dashboard/components/settings2.py src_orbis/omf/dashboard/components/settings.py
mv src_orbis/omf/dashboard/components/steering2.py src_orbis/omf/dashboard/components/steering.py
mv src_orbis/omf/dashboard/components/message_center2.py src_orbis/omf/dashboard/components/message_center.py
mv src_orbis/omf/dashboard/components/order2.py src_orbis/omf/dashboard/components/order.py
```

## 🚨 **Wiederherstellung bei Problemen:**

### **Vollständige Wiederherstellung:**
```bash
git reset --hard 756c9b8
```

### **Einzelne Dateien wiederherstellen:**
```bash
git checkout 756c9b8 -- src_orbis/omf/dashboard/omf_dashboard.py
git checkout 756c9b8 -- src_orbis/omf/dashboard/components/overview.py
git checkout 756c9b8 -- src_orbis/omf/dashboard/components/settings.py
git checkout 756c9b8 -- src_orbis/omf/dashboard/components/factory_steering.py
git checkout 756c9b8 -- src_orbis/omf/dashboard/components/generic_steering.py
git checkout 756c9b8 -- src_orbis/omf/dashboard/components/message_center.py
git checkout 756c9b8 -- src_orbis/omf/dashboard/components/steering.py
```

## 📊 **Zusammenfassung:**

### **Zu löschende Dateien:** 7 Dateien
- `omf_dashboard.py` (Original)
- `overview.py` (Original)
- `settings.py` (Original)
- `factory_steering.py` (Original)
- `generic_steering.py` (Original)
- `message_center.py` (Original)
- `steering.py` (Original)

### **Zu behaltende Dateien:** 18+ Dateien
- Alle Dashboard2-Dateien (werden umbenannt)
- Alle Sub-Komponenten
- Alle Assets und Konfigurationsdateien

### **Sicherheit:**
- ✅ **Commit Hash dokumentiert:** `756c9b8`
- ✅ **Wiederherstellung möglich:** `git reset --hard 756c9b8`
- ✅ **Einzelne Dateien wiederherstellbar**
- ✅ **Vollständige Backup-Strategie**

---

*Erstellt am: Januar 2025*  
*Commit Hash: 756c9b8*  
*Status: Bereit für sichere Migration*
