# MQTT WebSocket Connection Debugging Guide

## Overview

This guide provides step-by-step instructions for diagnosing WebSocket MQTT connection issues, particularly for cases where connections fail on specific browser/OS combinations (e.g., Mac + Chrome + Live Environment).

## Problem Context

**Symptom**: Connection failures on Mac + Chrome when connecting to live broker (e.g., `ws://192.168.0.100:9001`) while the same setup works on other platforms/browsers (Safari on Mac, Chrome on Windows). Replay environment (`localhost:9001`) works in all tested combinations.

**Suspected Causes**:
- Trailing slash or path handling in MQTT.js
- Browser security policies (Mixed Content, Private Network Access)
- Proxy/redirect/service worker interference
- CORS or WebSocket upgrade issues

## Debugging Tools

### 1. Raw WebSocket Browser Test (`tools/mqtt-debug.html`)

This standalone HTML tool tests raw WebSocket connectivity separate from MQTT.js.

**How to use**:

1. Open `tools/mqtt-debug.html` in your browser
2. Enter the WebSocket URL: `ws://192.168.0.100:9001`
3. Click "Test Connection"
4. Observe results and copy the log output

**What it tests**:
- Browser's ability to establish raw WebSocket connection
- Distinguishes between browser-level and MQTT.js-level issues
- Provides detailed connection state and error information

### 2. Diagnostic Mode in Application

Enable detailed logging in the actual application:

**Steps**:

1. Open Chrome DevTools Console
2. **Before loading the app**, run:
   ```javascript
   window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true
   ```
3. Reload the page/application
4. Copy all console logs, specifically:
   - Final mqtt.connect URL
   - mqtt.connect options
   - Raw WebSocket test results
   - Any error messages

**What it provides**:
- Detailed connection parameters used by MQTT.js
- Raw WebSocket test results within the app context
- Browser and environment information
- Error stack traces

## Step-by-Step Diagnostic Procedure

### Step 1: Raw WebSocket Browser Test

**Procedure**:
1. Open `tools/mqtt-debug.html` in Chrome on Mac
2. Test URL: `ws://192.168.0.100:9001`
3. Click "Test Connection"
4. Save output to: `tools-mqtt-debug-log.txt`

**Expected Results**:
- ✓ Success: "WebSocket connection opened successfully"
- ✗ Failure: "WebSocket error occurred" or "Connection timeout"

**Interpretation**:
- If raw WebSocket succeeds → Issue is with MQTT.js library behavior (path, headers, upgrade)
- If raw WebSocket fails → Issue is browser/network-level (firewall, proxy, policy)

### Step 2: Application Diagnostic Mode

**Procedure**:
1. Open Chrome DevTools Console
2. Run: `window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true`
3. Reload application
4. Wait for connection attempt
5. Copy entire console output to: `chrome-console.txt`

**Key Information to Capture**:
```
[WebSocketMqttAdapter] Original wsUrl parameter: 192.168.0.100:9001
[WebSocketMqttAdapter] Final mqtt.connect URL: ws://192.168.0.100:9001
[WebSocketMqttAdapter] mqtt.connect options: { connectTimeout: 10000, ... }
[WebSocketMqttAdapter] Raw WebSocket test result: { success: true/false, ... }
```

### Step 3: TCP-Level Network Tests

Test basic TCP connectivity from the Mac:

**Using netcat**:
```bash
nc -vz 192.168.0.100 9001
```

**Using telnet**:
```bash
telnet 192.168.0.100 9001
```

**Expected Output**:
- Success: "Connection to 192.168.0.100 port 9001 [tcp/*] succeeded!"
- Failure: "Connection refused" or timeout

Save output to: `nc-wscat-output.txt`

### Step 4: Node WebSocket Test (if Node.js available)

**Install wscat**:
```bash
npm install -g wscat
```

**Test connection**:
```bash
wscat -c ws://192.168.0.100:9001
```

**Expected Results**:
- Success: "Connected" (shows prompt)
- Failure: Error message or timeout

**Interpretation**:
- If wscat succeeds but browser fails → Browser policy issue
- If wscat fails → Network/firewall issue

### Step 5: Chrome DevTools Network Analysis

**Procedure**:
1. Open Chrome DevTools
2. Go to Network tab
3. Filter by "WS" (WebSocket)
4. Reload page / trigger connection
5. Right-click in Network panel → "Save all as HAR with content"
6. Save as: `network.har`

**What to look for**:
- WebSocket upgrade request
- Response status codes (101 Switching Protocols = success)
- Error codes (403, 404, 502, etc.)
- Request/response headers

### Step 6: Service Worker and Extension Check

**Check Service Workers**:
1. DevTools → Application tab → Service Workers
2. Temporarily unregister all service workers
3. Test connection again

**Test without extensions**:
1. Open Chrome in Incognito mode (or with `--disable-extensions`)
2. Test connection
3. If successful in Incognito → Extension is interfering

**Test Private Network Access flag**:
```bash
# Start Chrome with flag (macOS)
open -a "Google Chrome" --args --disable-features=BlockInsecurePrivateNetworkRequests

# Start Chrome with flag (Windows)
chrome.exe --disable-features=BlockInsecurePrivateNetworkRequests
```

### Step 7: Broker-Side Logging

If you have access to the broker (192.168.0.100):

**Check Mosquitto logs**:
```bash
tail -f /var/log/mosquitto/mosquitto.log
```

**Run while testing**:
- Watch for connection attempts
- Note client IP addresses
- Look for connection rejections or errors

**Capture packet dump** (optional):
```bash
sudo tcpdump -i any -w mqtt-test.pcap host <client-ip> and port 9001
```
Run for 30-60 seconds while testing, then save `mqtt-test.pcap`

## Collecting Results

Create a results archive with the following files:

### Required Files:
1. `tools-mqtt-debug-log.txt` - Output from mqtt-debug.html
2. `chrome-console.txt` - Complete console output with diagnostic mode
3. `network.har` - Chrome DevTools network capture
4. `test-summary.txt` - Brief summary of results (see template below)

### Optional Files:
5. `nc-wscat-output.txt` - Terminal output from nc/telnet/wscat
6. `mosquitto.log` - Broker logs during test period
7. `mqtt-test.pcap` - Network packet capture

### Test Summary Template (`test-summary.txt`):

```
MQTT WebSocket Connection Test Summary
======================================

Date: [YYYY-MM-DD]
Tester: [Name]
Environment: Mac + Chrome [version]

Test Results:
-------------

1. Raw WebSocket (tools/mqtt-debug.html):
   Status: [SUCCESS / FAILURE]
   Details: [Brief description]

2. Application Diagnostic Mode:
   Status: [SUCCESS / FAILURE]
   Final URL: [ws://...]
   Details: [Brief description]

3. TCP Connectivity (nc/telnet):
   Status: [SUCCESS / FAILURE]
   Details: [Brief description]

4. wscat Test:
   Status: [N/A / SUCCESS / FAILURE]
   Details: [Brief description]

5. Service Worker interference:
   Status: [NO / YES - describe]

6. Incognito Mode Test:
   Status: [SUCCESS / FAILURE]
   Details: [Brief description]

7. Broker Logs:
   Connection attempts visible: [YES / NO]
   Details: [Brief description]

Conclusion:
-----------
[Brief analysis of where the issue likely is]

Key Findings:
-------------
- [Finding 1]
- [Finding 2]
- [Finding 3]
```

## Interpretation Guide

### Scenario 1: Raw WebSocket succeeds, MQTT.js fails

**Diagnosis**: Issue with MQTT.js library configuration

**Likely causes**:
- Path handling (trailing slash)
- Protocol subprotocol mismatch
- MQTT.js adding unexpected headers or query parameters

**Next steps**:
- Check `Final mqtt.connect URL` in diagnostic logs
- Compare with working environments
- Check for URL differences (paths, query strings)

### Scenario 2: Raw WebSocket fails, wscat succeeds

**Diagnosis**: Browser-specific security policy

**Likely causes**:
- Mixed Content policy (HTTPS page loading WS://)
- Private Network Access (public page accessing private IP)
- CORS or CSP restrictions

**Next steps**:
- Check browser console for policy warnings
- Try with `--disable-features=BlockInsecurePrivateNetworkRequests`
- Check if page is served over HTTPS

### Scenario 3: Everything fails except localhost

**Diagnosis**: Network-level blocking

**Likely causes**:
- Firewall (client or broker side)
- Network proxy
- VPN interference
- Router/switch ACLs

**Next steps**:
- Check firewall rules
- Test from different network
- Check VPN settings

### Scenario 4: Works in Safari, fails in Chrome

**Diagnosis**: Chrome-specific policy or behavior

**Likely causes**:
- Chrome's stricter Private Network Access checks
- Chrome extension interference
- Different WebSocket implementation quirks

**Next steps**:
- Compare Safari vs Chrome Network inspector
- Test in Chrome Canary or Beta
- Check Chrome flags affecting network

## Browser Console Errors Reference

Common error patterns and their meanings:

| Error | Meaning | Likely Cause |
|-------|---------|--------------|
| `net::ERR_CONNECTION_REFUSED` | Server not listening or firewall block | Broker down or unreachable |
| `net::ERR_CONNECTION_TIMED_OUT` | No response from server | Network issue or broker unreachable |
| `net::ERR_FAILED` | Generic failure | Various causes, check details |
| `net::ERR_CERT_AUTHORITY_INVALID` | SSL certificate issue | Only for wss:// connections |
| `Failed to construct 'WebSocket': The URL's scheme must be either 'ws' or 'wss'` | Invalid URL scheme | URL construction error |
| `SecurityError` | Security policy violation | Mixed Content or CSP |

## Troubleshooting Tips

### If Mixed Content is suspected:
- Ensure page is served over HTTP (not HTTPS) when using ws://
- Or use wss:// if page is HTTPS

### If Private Network Access is suspected:
- Check for "Private Network Access" warnings in console
- Use Chrome flag: `--disable-features=BlockInsecurePrivateNetworkRequests`
- Consider serving from same network as broker

### If path/URL is suspected:
- Compare exact URLs between working and non-working environments
- Check for trailing slashes
- Verify MQTT.js version consistency

### If broker configuration is suspected:
- Verify WebSocket listener is enabled in mosquitto.conf:
  ```
  listener 9001
  protocol websockets
  ```
- Check broker accepts connections from client IP
- Verify no authentication issues

## References

- [mqtt.js Documentation](https://github.com/mqttjs/MQTT.js)
- [WebSocket API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Chrome Private Network Access](https://developer.chrome.com/blog/private-network-access-preflight/)
- [Mosquitto WebSocket Configuration](https://mosquitto.org/man/mosquitto-conf-5.html)

## Contact

For questions or to report results, please create an issue in the repository with:
- Test summary
- All collected log files
- Browser/OS versions
- Network environment details
