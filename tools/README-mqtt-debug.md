# MQTT WebSocket Debug Tools

Quick reference for diagnosing MQTT WebSocket connection issues.

## 🚀 Quick Start

### Option 1: Standalone Debug Tool (Easiest)

1. Open `tools/mqtt-debug.html` in your browser
2. Enter broker URL: `ws://192.168.0.100:9001`
3. Click "Test Connection"
4. Copy results using "Copy Log" button

**When to use**: First step in debugging, or when you need to test raw WebSocket connectivity.

### Option 2: Application Diagnostic Mode

1. Open Chrome DevTools Console
2. Run: `window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true`
3. Reload your application
4. Watch console for detailed diagnostic output

**When to use**: When you need to debug the actual application's MQTT connection behavior.

## 📋 What's Included

### Files

- **`mqtt-debug.html`** - Standalone diagnostic tool
  - Tests raw WebSocket connections
  - Tests MQTT.js connections
  - Shows system information
  - Copy/export results

- **`mqtt-debug-results-template.md`** - Template for organizing results
  - Structured format for all test outputs
  - Sections for each diagnostic test
  - Analysis and diagnosis sections

- **`../docs/04-howto/mqtt-websocket-debug-guide.md`** - Complete guide
  - Step-by-step testing procedures
  - Interpretation of results
  - Troubleshooting tips
  - Reference documentation

## 🔍 Common Scenarios

### "Chrome on Mac fails, but Safari works"

**Quick test**:
1. Open `mqtt-debug.html` in Chrome
2. Test raw WebSocket
3. If raw WebSocket fails → Chrome security policy issue
4. If raw WebSocket succeeds but MQTT.js fails → MQTT.js configuration issue

**Possible causes**:
- Chrome's Private Network Access policy
- Service Worker interference
- Browser extensions

**Try**:
- Test in Chrome Incognito mode
- Start Chrome with: `--disable-features=BlockInsecurePrivateNetworkRequests`
- Disable Service Workers in DevTools → Application

### "Works on localhost, fails on 192.168.x.x"

**Quick test**:
1. Terminal: `nc -vz 192.168.0.100 9001`
2. If nc succeeds → Browser policy blocking
3. If nc fails → Network/firewall issue

**Possible causes**:
- Firewall blocking private IPs
- Private Network Access policy
- Network proxy

### "Connection timeout"

**Quick test**:
1. Open `mqtt-debug.html`
2. Check "System Information" section
3. Test raw WebSocket
4. Check DevTools → Network → WS filter

**Possible causes**:
- Broker not running
- Wrong port
- Network unreachable
- Firewall

## 📊 Collecting Results

### Minimal Set (Quick Investigation)

1. **tools-mqtt-debug-log.txt**
   - From `mqtt-debug.html`, click "Copy Log"
   - Save to file

2. **chrome-console.txt**
   - Enable diagnostic mode
   - Copy console output

### Complete Set (Full Analysis)

Follow the template in `mqtt-debug-results-template.md`:

1. ✅ tools-mqtt-debug-log.txt
2. ✅ chrome-console.txt (with diagnostic mode)
3. ✅ network.har (DevTools → Network → Save as HAR)
4. ✅ nc-wscat-output.txt (terminal commands)
5. ⭕ mosquitto.log (broker-side, if accessible)
6. ⭕ mqtt-test.pcap (packet capture, if needed)

## 🛠️ Command Reference

### Test Basic Connectivity

```bash
# TCP connectivity
nc -vz 192.168.0.100 9001

# Or with telnet
telnet 192.168.0.100 9001
```

### Test WebSocket (Node.js)

```bash
# Install wscat
npm install -g wscat

# Test connection
wscat -c ws://192.168.0.100:9001
```

### Capture Network Traffic (requires sudo)

```bash
# On broker machine
sudo tcpdump -i any -w mqtt-test.pcap host <client-ip> and port 9001

# Let it run for 30-60 seconds during your tests
# Press Ctrl+C to stop
```

### Start Chrome with Debug Flags

```bash
# macOS
open -a "Google Chrome" --args --disable-features=BlockInsecurePrivateNetworkRequests

# Windows
chrome.exe --disable-features=BlockInsecurePrivateNetworkRequests

# Linux
google-chrome --disable-features=BlockInsecurePrivateNetworkRequests
```

## 🎯 Interpretation Guide

| Raw WS | MQTT.js | wscat | Likely Issue |
|--------|---------|-------|--------------|
| ✅ | ❌ | ✅ | MQTT.js config (path, headers) |
| ❌ | ❌ | ✅ | Browser security policy |
| ❌ | ❌ | ❌ | Network/firewall |
| ✅ | ✅ | ✅ | No issue (verify environment) |

**Legend**: ✅ = Works, ❌ = Fails

## 📖 Full Documentation

For detailed procedures, troubleshooting, and interpretation:

👉 **Read**: `../docs/04-howto/mqtt-websocket-debug-guide.md`

## 💡 Tips

1. **Always start with `mqtt-debug.html`** - It's the fastest way to isolate the issue
2. **Enable diagnostic mode early** - More information is better
3. **Test in Incognito first** - Rules out extensions quickly
4. **Compare working vs non-working** - Side-by-side comparison helps
5. **Check broker logs** - Connection attempts should be visible there
6. **Save everything** - You never know what detail will be important

## 🐛 Reporting Issues

When reporting WebSocket connection issues, please include:

1. Completed `mqtt-debug-results-template.md`
2. All log files mentioned above
3. Browser version: `chrome://version`
4. OS version
5. Network environment (VPN, proxy, corporate network, etc.)

## ❓ Need Help?

1. Read the full guide: `../docs/04-howto/mqtt-websocket-debug-guide.md`
2. Check existing issues in the repository
3. Create a new issue with your diagnostic results

## 🔗 Related Documentation

- [MQTT WebSocket Debug Guide](../docs/04-howto/mqtt-websocket-debug-guide.md)
- MQTT-Verbindungsverwaltung (OSF-UI): [MessageMonitorService Storage](../docs/03-decision-records/12-message-monitor-service-storage.md)
- [mqtt.js GitHub](https://github.com/mqttjs/MQTT.js)

---

**Version**: 1.0  
**Last Updated**: 2025-11-20  
**Maintainer**: ORBIS SmartFactory Team
