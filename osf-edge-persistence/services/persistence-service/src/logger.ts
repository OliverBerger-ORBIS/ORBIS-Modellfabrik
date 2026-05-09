type Level = 'debug' | 'info' | 'warn' | 'error';

const order: Record<Level, number> = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
};

export class Logger {
  constructor(private readonly level: Level = 'info') {}

  private shouldLog(level: Level): boolean {
    return order[level] >= order[this.level];
  }

  private emit(level: Level, message: string, details?: unknown): void {
    if (!this.shouldLog(level)) {
      return;
    }
    const ts = new Date().toISOString();
    const payload = details === undefined ? '' : ` ${JSON.stringify(details)}`;
    const line = `[${ts}] [${level.toUpperCase()}] ${message}${payload}`;
    if (level === 'error') {
      console.error(line);
    } else if (level === 'warn') {
      console.warn(line);
    } else {
      console.log(line);
    }
  }

  debug(message: string, details?: unknown): void {
    this.emit('debug', message, details);
  }
  info(message: string, details?: unknown): void {
    this.emit('info', message, details);
  }
  warn(message: string, details?: unknown): void {
    this.emit('warn', message, details);
  }
  error(message: string, details?: unknown): void {
    this.emit('error', message, details);
  }
}
