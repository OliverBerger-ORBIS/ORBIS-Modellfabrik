# 🚀 Quick Start: Debug WebSocket MQTT Connection Issues

## The Problem
Mac + Chrome fails to connect to `ws://192.168.0.100:9001` (Live Environment)
While: Safari on Mac works ✅, Chrome on Windows works ✅, localhost:9001 works ✅

## Solution: 3-Minute Quick Diagnostic

### Test 1: Raw WebSocket (30 seconds)

**Open**: `tools/mqtt-debug.html` in Chrome on Mac

**Do**:
1. Enter URL: `ws://192.168.0.100:9001`
2. Click "Test Connection"
3. Wait 5 seconds

**Result**:
- ✅ **Success** = Browser can connect → Problem is MQTT.js or app
- ❌ **Failure** = Browser blocked it → Check results below

### Test 2: Application Diagnostic (1 minute)

**In Chrome DevTools Console** (before loading app):
```javascript
window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true
```

**Then**: Reload app

**Look for** in console:
```
[WebSocketMqttAdapter] Final mqtt.connect URL: ws://...
[WebSocketMqttAdapter] Raw WebSocket test result: { success: true/false }
```

**Save**: Copy entire console output

### Test 3: Basic Network (30 seconds)

**In Terminal**:
```bash
nc -vz 192.168.0.100 9001
```

**Result**:
- ✅ = Network is fine
- ❌ = Firewall or network issue

## Interpret Results

| Raw WS | App Diag | nc | Issue |
|--------|----------|----|----|
| ❌ | ❌ | ✅ | Chrome security policy blocking |
| ✅ | ❌ | ✅ | MQTT.js configuration (path/headers) |
| ❌ | ❌ | ❌ | Network/Firewall |

## Quick Fixes to Try

### If Chrome is blocking:
```bash
# Start Chrome with disabled PNA check
open -a "Google Chrome" --args --disable-features=BlockInsecurePrivateNetworkRequests
```

### If Service Worker might interfere:
1. DevTools → Application → Service Workers
2. Click "Unregister" on all
3. Test again

### If extension might interfere:
1. Open Chrome Incognito (Cmd+Shift+N)
2. Test there

## Collect Full Diagnostic Data

If quick tests don't solve it:

1. **Fill out**: `tools/mqtt-debug-results-template.md`
2. **Attach**:
   - tools-mqtt-debug-log.txt (from mqtt-debug.html "Copy Log")
   - chrome-console.txt (console output with diagnostic mode)
   - network.har (DevTools → Network → Save as HAR)
3. **Create issue** with files

## Full Documentation

📖 **Complete Guide**: `docs/04-howto/mqtt-websocket-debug-guide.md`
- All test procedures
- Detailed interpretation
- Troubleshooting steps
- Reference information

## Common Scenarios & Solutions

### "Works on localhost, fails on 192.168.x.x"
**Likely**: Private Network Access policy
**Try**: Chrome with `--disable-features=BlockInsecurePrivateNetworkRequests`
**Fix**: Use wss:// or serve app from same network

### "Works in Safari, fails in Chrome"
**Likely**: Chrome-specific security policy
**Try**: Check console for "Private Network Access" warnings
**Fix**: See Chrome Private Network Access docs

### "Connection timeout"
**Check**:
1. Is broker running? `nc -vz 192.168.0.100 9001`
2. Can broker see attempts? Check `/var/log/mosquitto/mosquitto.log`
3. Firewall blocking? Check macOS firewall settings

### "WebSocket error immediately"
**Check**:
1. URL correct? (ws:// not http://)
2. Port correct? (9001 not 1883)
3. Broker has WebSocket enabled? (listener 9001 / protocol websockets)

## Help & Support

**Questions?** Check the full guide first: `docs/04-howto/mqtt-websocket-debug-guide.md`

**Found the issue?** Great! Please document it so others can learn.

**Still stuck?** Create an issue with:
- Completed results template
- All diagnostic files
- Browser/OS versions

---

**Version**: 1.0  
**Created**: 2025-11-20  
**For Issue**: Mac + Chrome WebSocket connection debugging
