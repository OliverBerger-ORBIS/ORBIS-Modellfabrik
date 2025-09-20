# Mermaid Hybrid-Modell Test

## Shared Diagram (aus _shared)

```mermaid
graph TD
    A[APS-Fabrik] -->|MQTT Messages| B[MQTT-Broker]
    B -->|Live Data| C[Session Recorder]
    C -->|SQLite + Logs| D[Sessions Directory]
    D -->|Session Files| E[Session Replay]
    E -->|MQTT Messages| B
    B -->|Test Data| F[OMF-Dashboard]
    
    G[Session Analysis] -->|Read| D
    H[Template Analysis] -->|Read| D
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#e8f5e8
    style F fill:#e1f5fe
    style G fill:#fff3e0
    style H fill:#fff3e0
```

## Lokales Diagramm (für diese Sektion)

```mermaid
graph LR
    A[Test Start] --> B[Test Process]
    B --> C[Test End]
    
    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style C fill:#fff3e0
```

## Verwendung

### **Markdown Preview testen:**
1. **Strg+Shift+V** für Markdown Preview
2. **Mermaid-Diagramme** sollten gerendert werden

### **In anderen Dateien referenzieren:**
```markdown
<!-- Shared Diagram -->
![System Overview](../_shared/diagrams/system-overview.md)

<!-- Lokales Diagram -->
![Test Flow](./test-hybrid.md)
```

---

*Test für Mermaid Hybrid-Modell | [Zurück zur README](../README.md)*
