# MQTT WebSocket Connection Diagnostic Results

## Test Information

- **Date**: [YYYY-MM-DD HH:MM:SS]
- **Tester**: [Your Name]
- **Browser**: Chrome [Version]
- **Operating System**: macOS [Version] / Windows [Version]
- **Environment**: Live / Replay / Development
- **Broker URL**: ws://192.168.0.100:9001 (or your broker URL)

## System Information

```
User Agent: [Copy from tools/mqtt-debug.html System Info]
Platform: [Copy from tools/mqtt-debug.html System Info]
Language: [Copy from tools/mqtt-debug.html System Info]
Screen Resolution: [Copy from tools/mqtt-debug.html System Info]
Service Workers Active: [Number]
Location Protocol: [http: / https:]
Location Host: [hostname:port]
```

## Test Results Summary

### 1. Raw WebSocket Test (tools/mqtt-debug.html)

**Status**: ✓ SUCCESS / ✗ FAILURE

**Test Configuration**:
- URL: ws://192.168.0.100:9001
- Protocol: [none/mqtt/other]

**Result Details**:
```
[Paste the log output from mqtt-debug.html "Raw WebSocket Connection Test" section]
```

**Key Observations**:
- Connection opened: [YES / NO]
- Error code: [if any]
- Time to connect: [milliseconds]
- ReadyState at failure: [0=CONNECTING, 1=OPEN, 2=CLOSING, 3=CLOSED]

---

### 2. MQTT.js Connection Test (tools/mqtt-debug.html)

**Status**: ✓ SUCCESS / ✗ FAILURE

**Test Configuration**:
- Broker URL: 192.168.0.100:9001
- Username: [default / none / other]
- Password: [yes / no]

**Result Details**:
```
[Paste the log output from mqtt-debug.html "MQTT.js Connection Test" section]
```

**Key Observations**:
- MQTT.js client created: [YES / NO]
- Connection established: [YES / NO]
- CONNACK received: [YES / NO]
- Error message: [if any]

---

### 3. Application Diagnostic Mode

**Status**: ✓ SUCCESS / ✗ FAILURE

**Activation**: Confirmed window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true

**Console Output**:
```
[Paste complete console output from Chrome DevTools, including all [WebSocketMqttAdapter] messages]

Key lines to include:
- [WebSocketMqttAdapter] Original wsUrl parameter: ...
- [WebSocketMqttAdapter] Final mqtt.connect URL: ...
- [WebSocketMqttAdapter] mqtt.connect options: ...
- [WebSocketMqttAdapter] Raw WebSocket test result: ...
- Any error messages
```

**Analysis**:
- Original URL: [...]
- Final URL: [...]
- URL differences: [note any changes]
- Raw WebSocket test in app context: [SUCCESS / FAILURE]
- Connection timeout: [YES / NO / N/A]

---

### 4. TCP Connectivity Tests

#### netcat (nc)

**Command**: `nc -vz 192.168.0.100 9001`

**Output**:
```
[Paste nc output]
```

**Result**: ✓ SUCCESS / ✗ FAILURE

#### telnet

**Command**: `telnet 192.168.0.100 9001`

**Output**:
```
[Paste telnet output]
```

**Result**: ✓ SUCCESS / ✗ FAILURE

#### wscat (if available)

**Command**: `wscat -c ws://192.168.0.100:9001`

**Output**:
```
[Paste wscat output]
```

**Result**: ✓ SUCCESS / ✗ FAILURE / N/A

**Interpretation**:
- TCP connection possible: [YES / NO]
- WebSocket from command line works: [YES / NO / N/A]
- Suggests browser vs network issue: [BROWSER / NETWORK / UNCLEAR]

---

### 5. Chrome DevTools Network Analysis

**HAR File**: [Attached as network.har / Not captured]

**WebSocket Request Details**:
```
Request URL: [ws://...]
Request Method: [GET]
Status Code: [101 Switching Protocols / 403 / 404 / 502 / failed]
Request Headers:
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Key: [...]
  Sec-WebSocket-Version: [13]
  Origin: [...]

Response Headers (if any):
  [paste headers]
```

**Observations**:
- WebSocket request sent: [YES / NO]
- Upgrade response received: [YES / NO]
- Status code: [...]
- Notable headers: [any unusual headers]
- Timing: [how long before failure]

---

### 6. Service Worker & Extension Tests

#### Service Workers Check

**Active Service Workers**:
```
[List from DevTools → Application → Service Workers]
- Scope 1: [URL]
- Scope 2: [URL]
...or "None active"
```

**Test After Unregistering Service Workers**:
- Unregistered all: [YES / NO / N/A]
- Re-tested connection: [YES / NO]
- Result: ✓ SUCCESS / ✗ FAILURE / NOT TESTED

#### Incognito Mode Test

**Test Configuration**: Chrome Incognito Mode (no extensions)

**Result**: ✓ SUCCESS / ✗ FAILURE / NOT TESTED

**Interpretation**:
- If succeeds in Incognito: [Extension likely interfering]
- If fails in Incognito: [Not extension-related]

#### Chrome Flags Test

**Flag Used**: `--disable-features=BlockInsecurePrivateNetworkRequests`

**Result**: ✓ SUCCESS / ✗ FAILURE / NOT TESTED

**Interpretation**:
- If succeeds with flag: [Private Network Access policy is blocking]
- If fails with flag: [Not PNA-related]

---

### 7. Broker-Side Analysis

#### Mosquitto Log

**Log File Location**: /var/log/mosquitto/mosquitto.log

**Relevant Log Entries** (during test period):
```
[Paste relevant log lines from broker, with timestamps]
```

**Observations**:
- Connection attempts visible: [YES / NO]
- Client IP in logs: [YES / NO]
- Authentication attempts: [SUCCESS / FAILURE / NONE]
- Disconnection reasons: [if any]
- Broker errors: [if any]

#### Network Packet Capture

**Capture File**: [Attached as mqtt-test.pcap / Not captured]

**tcpdump Command**: `sudo tcpdump -i any -w mqtt-test.pcap host [client-ip] and port 9001`

**Observations**:
- SYN packets sent: [YES / NO]
- SYN-ACK received: [YES / NO]
- TCP connection established: [YES / NO]
- WebSocket upgrade request: [YES / NO]
- Data exchanged: [YES / NO]

---

## Error Messages & Warnings

### Console Errors
```
[Paste any error messages from browser console, including net::ERR_* codes]
```

### Console Warnings
```
[Paste any warnings, especially about Mixed Content, CORS, CSP, or Private Network Access]
```

---

## Comparative Analysis

### Working Environments

**Environment 1**: Safari on Mac
- Status: ✓ WORKS / ✗ FAILS
- Notes: [any differences observed]

**Environment 2**: Chrome on Windows
- Status: ✓ WORKS / ✗ FAILS
- Notes: [any differences observed]

**Environment 3**: Replay (localhost:9001)
- Status: ✓ WORKS / ✗ FAILS
- Notes: [any differences observed]

### Key Differences
- [List any URL, header, timing, or behavior differences between working and non-working cases]
- [Note any platform-specific observations]

---

## Preliminary Diagnosis

Based on the test results:

**Most Likely Cause**: [Brief statement]

**Evidence**:
1. [Key piece of evidence 1]
2. [Key piece of evidence 2]
3. [Key piece of evidence 3]

**Confidence Level**: HIGH / MEDIUM / LOW

**Reasoning**:
[Explain the logic connecting the evidence to the diagnosis]

---

## Recommended Next Steps

1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

---

## Additional Notes

[Any other observations, context, or information that might be relevant]

---

## Attachments Checklist

- [ ] tools-mqtt-debug-log.txt (raw WebSocket + MQTT.js test outputs)
- [ ] chrome-console.txt (complete console output with diagnostic mode)
- [ ] network.har (Chrome DevTools network capture)
- [ ] nc-wscat-output.txt (terminal outputs from connectivity tests)
- [ ] mosquitto.log (broker logs during test period)
- [ ] mqtt-test.pcap (network packet capture, if available)
- [ ] This completed template as mqtt-debug-results.md

---

**Tester Signature**: [Name]
**Date Completed**: [YYYY-MM-DD HH:MM:SS]
