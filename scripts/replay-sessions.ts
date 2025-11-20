#!/usr/bin/env tsx
/**
 * Session Replay Script
 * 
 * Replays MQTT session logs to test application stability under realistic traffic.
 * Reads session logs from data/omf-data/sessions/*.log and emits messages via MockMqttAdapter.
 * 
 * Usage:
 *   tsx scripts/replay-sessions.ts --session <path> [--speedFactor <number>] [--once]
 * 
 * Options:
 *   --session <path>         Path to session log file (required)
 *   --speedFactor <number>   Speed multiplier (default: 1.0, e.g., 2.0 = twice as fast)
 *   --once                   Play session once and exit (default: loop continuously)
 * 
 * Examples:
 *   tsx scripts/replay-sessions.ts --session data/omf-data/sessions/default_test_session.log
 *   tsx scripts/replay-sessions.ts --session data/omf-data/sessions/default_test_session.log --speedFactor 10
 */

import * as fs from 'fs';
import * as path from 'path';
import { MockMqttAdapter } from '../omf3/libs/mqtt-client/src/mock-adapter';

interface SessionLogEntry {
  timestamp: string;
  topic: string;
  payload: string;
  qos?: number;
  retain?: boolean;
  message_type?: string;
  module_type?: string;
  serial_number?: string;
  status?: string;
}

interface ReplayOptions {
  sessionPath: string;
  speedFactor: number;
  once: boolean;
}

class SessionReplayer {
  private adapter: MockMqttAdapter;
  private entries: SessionLogEntry[] = [];
  private startTime?: Date;
  private messageCount = 0;
  private isRunning = false;

  constructor(private options: ReplayOptions) {
    this.adapter = new MockMqttAdapter();
  }

  async loadSession(): Promise<void> {
    console.log(`[SessionReplayer] Loading session from: ${this.options.sessionPath}`);
    
    const fileContent = fs.readFileSync(this.options.sessionPath, 'utf-8');
    const lines = fileContent.split('\n').filter(line => line.trim());
    
    this.entries = [];
    for (const line of lines) {
      try {
        const entry = JSON.parse(line) as SessionLogEntry;
        this.entries.push(entry);
      } catch (error) {
        console.warn('[SessionReplayer] Failed to parse line, skipping:', line.substring(0, 100));
      }
    }
    
    console.log(`[SessionReplayer] Loaded ${this.entries.length} messages`);
  }

  async connect(): Promise<void> {
    console.log('[SessionReplayer] Connecting MockMqttAdapter...');
    await this.adapter.connect('mock://replay');
    console.log('[SessionReplayer] Connected');
  }

  async subscribeAll(): Promise<void> {
    // Extract unique topics from the session
    const topics = new Set(this.entries.map(e => e.topic));
    
    console.log(`[SessionReplayer] Subscribing to ${topics.size} topics...`);
    for (const topic of topics) {
      await this.adapter.subscribe(topic);
    }
    console.log('[SessionReplayer] Subscribed to all topics');
  }

  async replay(): Promise<void> {
    if (this.entries.length === 0) {
      console.error('[SessionReplayer] No entries to replay');
      return;
    }

    this.isRunning = true;
    this.messageCount = 0;
    this.startTime = new Date();

    console.log('[SessionReplayer] Starting replay...');
    console.log(`[SessionReplayer] Speed factor: ${this.options.speedFactor}x`);
    console.log(`[SessionReplayer] Mode: ${this.options.once ? 'once' : 'loop'}`);

    do {
      await this.replayOnce();
      
      if (!this.options.once) {
        console.log('[SessionReplayer] Looping session...');
      }
    } while (!this.options.once && this.isRunning);

    console.log(`[SessionReplayer] Replay complete. Total messages: ${this.messageCount}`);
  }

  private async replayOnce(): Promise<void> {
    if (this.entries.length === 0) return;

    // Calculate time deltas between messages
    const baseTimestamp = new Date(this.entries[0].timestamp).getTime();
    
    for (let i = 0; i < this.entries.length; i++) {
      if (!this.isRunning) break;

      const entry = this.entries[i];
      const currentTimestamp = new Date(entry.timestamp).getTime();
      const delta = currentTimestamp - baseTimestamp;
      
      // Calculate delay with speed factor
      const delay = i === 0 ? 0 : delta / this.options.speedFactor;
      
      // Wait for the calculated delay (from first message)
      if (delay > 0) {
        const nextTimestamp = i > 0 ? new Date(this.entries[i - 1].timestamp).getTime() : baseTimestamp;
        const actualDelay = (currentTimestamp - nextTimestamp) / this.options.speedFactor;
        if (actualDelay > 0) {
          await this.sleep(actualDelay);
        }
      }

      // Publish the message
      try {
        await this.adapter.publish(entry.topic, entry.payload, {
          qos: entry.qos as 0 | 1 | 2 | undefined,
          retain: entry.retain,
        });
        
        this.messageCount++;
        
        // Log progress every 100 messages
        if (this.messageCount % 100 === 0) {
          const elapsed = ((new Date().getTime() - this.startTime!.getTime()) / 1000).toFixed(1);
          const rate = (this.messageCount / parseFloat(elapsed)).toFixed(1);
          console.log(`[SessionReplayer] Progress: ${this.messageCount} messages in ${elapsed}s (${rate} msg/s)`);
        }
      } catch (error) {
        console.error(`[SessionReplayer] Failed to publish message ${i}:`, error);
      }
    }
  }

  stop(): void {
    console.log('[SessionReplayer] Stopping replay...');
    this.isRunning = false;
  }

  async disconnect(): Promise<void> {
    console.log('[SessionReplayer] Disconnecting...');
    await this.adapter.disconnect();
  }

  getMessageCount(): number {
    return this.messageCount;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

function parseArgs(): ReplayOptions {
  const args = process.argv.slice(2);
  let sessionPath = '';
  let speedFactor = 1.0;
  let once = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--session' && i + 1 < args.length) {
      sessionPath = args[++i];
    } else if (arg === '--speedFactor' && i + 1 < args.length) {
      speedFactor = parseFloat(args[++i]);
      if (isNaN(speedFactor) || speedFactor <= 0) {
        console.error('Error: --speedFactor must be a positive number');
        process.exit(1);
      }
    } else if (arg === '--once') {
      once = true;
    } else if (arg === '--help' || arg === '-h') {
      printUsage();
      process.exit(0);
    } else {
      console.error(`Unknown argument: ${arg}`);
      printUsage();
      process.exit(1);
    }
  }

  if (!sessionPath) {
    console.error('Error: --session is required');
    printUsage();
    process.exit(1);
  }

  // Resolve path relative to current working directory
  sessionPath = path.resolve(process.cwd(), sessionPath);

  if (!fs.existsSync(sessionPath)) {
    console.error(`Error: Session file not found: ${sessionPath}`);
    process.exit(1);
  }

  return { sessionPath, speedFactor, once };
}

function printUsage(): void {
  console.log(`
Session Replay Script

Usage:
  tsx scripts/replay-sessions.ts --session <path> [--speedFactor <number>] [--once]

Options:
  --session <path>         Path to session log file (required)
  --speedFactor <number>   Speed multiplier (default: 1.0, e.g., 2.0 = twice as fast)
  --once                   Play session once and exit (default: loop continuously)

Examples:
  tsx scripts/replay-sessions.ts --session data/omf-data/sessions/default_test_session.log
  tsx scripts/replay-sessions.ts --session data/omf-data/sessions/default_test_session.log --speedFactor 10
  tsx scripts/replay-sessions.ts --session data/omf-data/sessions/default_test_session.log --once
  `);
}

async function main(): Promise<void> {
  const options = parseArgs();
  
  console.log('='.repeat(60));
  console.log('Session Replay Script');
  console.log('='.repeat(60));
  
  const replayer = new SessionReplayer(options);
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n[Main] Received SIGINT, shutting down...');
    replayer.stop();
    await replayer.disconnect();
    console.log(`[Main] Final message count: ${replayer.getMessageCount()}`);
    process.exit(0);
  });

  try {
    await replayer.loadSession();
    await replayer.connect();
    await replayer.subscribeAll();
    await replayer.replay();
    await replayer.disconnect();
    
    console.log('='.repeat(60));
    console.log('Replay complete!');
    console.log('='.repeat(60));
  } catch (error) {
    console.error('[Main] Fatal error:', error);
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
}
