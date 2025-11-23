/**
 * Simple centralized logger for the metrics service
 */

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}

class Logger {
  private formatMessage(level: LogLevel, message: string, data?: any): string {
    const timestamp = new Date().toISOString();
    let logMessage = `[${timestamp}] [${level}] ${message}`;
    
    if (data !== undefined) {
      if (data instanceof Error) {
        logMessage += ` - ${data.message}\n${data.stack}`;
      } else {
        logMessage += ` - ${JSON.stringify(data)}`;
      }
    }
    
    return logMessage;
  }

  debug(message: string, data?: any): void {
    console.log(this.formatMessage(LogLevel.DEBUG, message, data));
  }

  info(message: string, data?: any): void {
    console.log(this.formatMessage(LogLevel.INFO, message, data));
  }

  warn(message: string, data?: any): void {
    console.warn(this.formatMessage(LogLevel.WARN, message, data));
  }

  error(message: string, data?: any): void {
    console.error(this.formatMessage(LogLevel.ERROR, message, data));
  }
}

export const logger = new Logger();
