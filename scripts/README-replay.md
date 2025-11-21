# Session Replay Script

## Overview

The session replay script allows you to replay recorded MQTT session logs for smoke testing, stability testing, and performance validation of the omf3 application. This is particularly useful for:

- Testing application stability under realistic traffic patterns
- Memory leak detection during long-running sessions
- Performance profiling with real-world message volumes
- Reproducing issues found in production sessions

## Usage

### Basic Command

```bash
npx tsx scripts/replay-sessions.ts --session <path-to-log-file>
```

### Command-Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--session <path>` | Path to session log file (required) | - | `data/omf-data/sessions/default_test_session.log` |
| `--speedFactor <number>` | Speed multiplier for replay | 1.0 | `10` (10x faster) |
| `--once` | Play session once and exit | Loop continuously | - |
| `--help` | Display help message | - | - |

### Examples

#### 1. Replay at normal speed (real-time)
```bash
npx tsx scripts/replay-sessions.ts \
  --session data/omf-data/sessions/default_test_session.log
```

#### 2. Replay 10x faster for quick smoke testing
```bash
npx tsx scripts/replay-sessions.ts \
  --session data/omf-data/sessions/production_order_blue_20251110_180619.log \
  --speedFactor 10
```

#### 3. Replay once and exit
```bash
npx tsx scripts/replay-sessions.ts \
  --session data/omf-data/sessions/storage_order_white_20251110_181619.log \
  --once
```

#### 4. Continuous stress testing (loop mode)
```bash
npx tsx scripts/replay-sessions.ts \
  --session data/omf-data/sessions/Start_20251110_175151.log \
  --speedFactor 5
```
Press `Ctrl+C` to stop the loop.

## Session Log Format

Session logs are stored in `data/omf-data/sessions/*.log` and use JSON Lines format (one JSON object per line):

```json
{
  "timestamp": "2025-08-14T16:14:45.240146",
  "topic": "module/v1/ff/NodeRed/status",
  "payload": "{\"connectionState\":\"ONLINE\"}",
  "qos": 0,
  "retain": true
}
```

### Fields

- **timestamp**: ISO 8601 timestamp when the message was recorded
- **topic**: MQTT topic
- **payload**: Message payload (usually JSON string)
- **qos**: Quality of Service level (0, 1, or 2)
- **retain**: Whether message should be retained by broker

## How It Works

1. **Load**: Parses the session log file and loads all messages
2. **Connect**: Creates a MockMqttAdapter instance
3. **Subscribe**: Subscribes to all unique topics found in the session
4. **Replay**: Publishes messages with timing preserved relative to original recording
5. **Monitor**: Logs progress every 100 messages

The script preserves the relative timing between messages. For example, if two messages were recorded 5 seconds apart, they will be replayed 5 seconds apart (or proportionally faster with `--speedFactor`).

## Use Cases

### Stability Testing

Run a recorded session continuously to detect memory leaks or stability issues:

```bash
npx tsx scripts/replay-sessions.ts \
  --session data/omf-data/sessions/production_order_white_20251110_184459.log \
  --speedFactor 2
```

Monitor application memory and CPU usage over several hours.

### Performance Benchmarking

Replay at high speed to test message processing performance:

```bash
npx tsx scripts/replay-sessions.ts \
  --session data/omf-data/sessions/default_test_session.log \
  --speedFactor 100 \
  --once
```

### Regression Testing

Replay a session that previously caused issues to verify fixes:

```bash
npx tsx scripts/replay-sessions.ts \
  --session data/omf-data/sessions/auftrag-weiss_1.log \
  --once
```

### Integration Testing

Combine with application testing to verify end-to-end behavior:

```bash
# Terminal 1: Start the application
npm run serve:local

# Terminal 2: Replay session
npx tsx scripts/replay-sessions.ts \
  --session data/omf-data/sessions/default_test_session.log \
  --speedFactor 5 \
  --once
```

## Troubleshooting

### Script exits immediately
- Ensure the session file path is correct
- Check that the log file is not empty
- Verify file contains valid JSON Lines format

### Messages not appearing in UI
- The replay script uses MockMqttAdapter which may need integration with your application
- For live application testing, consider modifying the script to use WebSocketMqttAdapter

### High CPU usage
- Reduce `--speedFactor` to lower message rate
- Use `--once` mode instead of continuous loop

## Limitations

- Currently uses MockMqttAdapter (in-process only)
- Does not connect to real MQTT broker
- Timing precision limited to JavaScript setTimeout resolution (~4ms minimum)

## Future Enhancements

Potential improvements for future versions:

- Support for WebSocketMqttAdapter to replay via real MQTT broker
- Message filtering by topic pattern
- Ability to pause/resume replay
- Real-time metrics dashboard
- Session editing/splicing capabilities

## See Also

- [Message Monitor Service](../omf3/apps/ccu-ui/src/app/services/message-monitor.service.ts)
- [Connection Service](../omf3/apps/ccu-ui/src/app/services/connection.service.ts)
- [MQTT Client Library](../omf3/libs/mqtt-client/)
