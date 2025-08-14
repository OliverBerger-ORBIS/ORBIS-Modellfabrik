# MQTT Data Storage - Fischertechnik APS

## 📁 Structure

### `/logs/` - Raw MQTT Log Files
- **`aps_persistent_traffic_*.log`** - Persistent logger output
- **`aps_mqtt_traffic.log`** - Live MQTT traffic
- **`mqtt_traffic.log`** - Legacy traffic logs

### `/sessions/` - Session Data (RECOMMENDED)
- **Structure**: Flat files in `/sessions/`
- **Example**: `Order_cloud_blue_ok.db`, `Order_cloud_blue_ok.log`
- **Contains**: Both `.db` and `.log` files for each session
- **Purpose**: Organized, labeled data for analysis

### `/exports/` - Analysis Results
- **`*.png`** - Generated charts and visualizations
- **`*.csv`** - Exported data for external analysis

## 📊 Current Data

### Active Sessions (in `/sessions/`)
- **`Order_cloud_blue_ok`** - Blaue Cloud-Bestellung
  - Database: `aps_persistent_traffic_bestellung_blau_20250814.db` (13MB)
  - Log: `aps_persistent_traffic_bestellung_blau_20250814.log` (12MB)

## 🔄 Directory Purpose

### **Best Practice:**
- **All Sessions**: Store in `/sessions/` as flat files
- **Naming**: `{Session_Label}.db` and `{Session_Label}.log`
- **Example**: `Order_cloud_blue_ok.db`, `Order_cloud_white_ok.db`

## 🧹 Cleanup Status

### ✅ Completed
- **Deleted**: Problematic test database
- **Organized**: Session data in `/sessions/`
- **Cleaned**: Legacy large log files

### 🔄 Next Steps
1. **New Sessions**: Use `aps_session_logger.py` for organized logging
2. **Dashboard**: Updated to show clean session names
3. **Analysis**: Focus on `/sessions/` data only
