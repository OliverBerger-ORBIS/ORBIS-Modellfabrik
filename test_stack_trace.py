#!/usr/bin/env python3
"""
Test für Stack-Trace Tool
"""

from stack_trace_debug import start_stack_trace, stop_stack_trace, get_trace_summary

def test_function_a():
    """Test-Funktion A"""
    print("In test_function_a")
    test_function_b()

def test_function_b():
    """Test-Funktion B"""
    print("In test_function_b")
    return "test_result"

def main():
    print("🧪 Teste Stack-Trace Tool...")
    
    # Stack-Trace starten
    start_stack_trace()
    
    # Test-Funktionen aufrufen
    result = test_function_a()
    print(f"Result: {result}")
    
    # Stack-Trace stoppen
    stop_stack_trace()
    
    # Zusammenfassung anzeigen
    print("\n" + "="*50)
    print(get_trace_summary())
    
    print("\n✅ Stack-Trace Test abgeschlossen!")

if __name__ == "__main__":
    main()
