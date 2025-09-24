#!/usr/bin/env python3
"""
Stack-Trace Debug Tool für OMF Dashboard
Vergleicht Funktionsaufrufe vor und nach APS-Tabs Implementierung
"""

import sys
import os
from pathlib import Path
from datetime import datetime

class StackTracer:
    def __init__(self, output_file="stack_trace.log"):
        self.output_file = output_file
        self.trace_data = []
        self.enabled = False
        
    def trace_calls(self, frame, event, arg):
        """Trace-Funktion für alle Funktionsaufrufe"""
        if not self.enabled:
            return
            
        if event == 'call':
            filename = frame.f_code.co_filename
            func_name = frame.f_code.co_name
            line_no = frame.f_lineno
            
            # Nur OMF-relevante Dateien loggen
            if 'omf' in filename or 'dashboard' in filename or 'stack_trace' in filename:
                # Relative Pfade für bessere Lesbarkeit
                rel_path = os.path.relpath(filename, Path.cwd())
                
                trace_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'event': event,
                    'file': rel_path,
                    'function': func_name,
                    'line': line_no,
                    'args': str(arg) if arg else None
                }
                
                self.trace_data.append(trace_entry)
                
                # Sofort in Datei schreiben
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(f"{trace_entry['timestamp']} | {event.upper()} | {rel_path}:{line_no} | {func_name}()\n")
    
    def start_tracing(self):
        """Startet das Tracing"""
        self.enabled = True
        # Alte Trace-Datei löschen
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        print(f"🔍 Stack-Trace gestartet -> {self.output_file}")
        sys.settrace(self.trace_calls)
    
    def stop_tracing(self):
        """Stoppt das Tracing"""
        self.enabled = False
        sys.settrace(None)
        print(f"⏹️ Stack-Trace gestoppt -> {len(self.trace_data)} Einträge")
    
    def get_trace_summary(self):
        """Gibt eine Zusammenfassung der Trace-Daten zurück"""
        if not self.trace_data:
            return "Keine Trace-Daten verfügbar"
            
        # Gruppiere nach Dateien
        file_counts = {}
        function_counts = {}
        
        for entry in self.trace_data:
            file_counts[entry['file']] = file_counts.get(entry['file'], 0) + 1
            function_counts[entry['function']] = function_counts.get(entry['function'], 0) + 1
        
        summary = f"Stack-Trace Zusammenfassung ({len(self.trace_data)} Einträge):\n"
        summary += f"\n📁 Dateien (Top 10):\n"
        for file, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            summary += f"  {file}: {count} Aufrufe\n"
            
        summary += f"\n🔧 Funktionen (Top 10):\n"
        for func, count in sorted(function_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            summary += f"  {func}(): {count} Aufrufe\n"
            
        return summary

# Globale Instanz
tracer = StackTracer()

def start_stack_trace():
    """Startet das Stack-Tracing"""
    tracer.start_tracing()

def stop_stack_trace():
    """Stoppt das Stack-Tracing"""
    tracer.stop_tracing()

def get_trace_summary():
    """Gibt Trace-Zusammenfassung zurück"""
    return tracer.get_trace_summary()

if __name__ == "__main__":
    print("Stack-Trace Debug Tool für OMF Dashboard")
    print("Verwendung:")
    print("  from stack_trace_debug import start_stack_trace, stop_stack_trace, get_trace_summary")
    print("  start_stack_trace()  # Vor dem Test")
    print("  # ... Dashboard testen ...")
    print("  stop_stack_trace()   # Nach dem Test")
    print("  print(get_trace_summary())  # Zusammenfassung anzeigen")
