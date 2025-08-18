# Orbis Tests

This directory contains the Orbis-specific tests for the Agile Production Simulation system.

## 📁 Purpose

This folder contains custom tests developed by Orbis, distinct from the original Fischertechnik content. It follows the naming convention of using the "orbis" suffix to clearly identify Orbis customizations.

## 🧪 Testing Strategy

- **Unit Tests**: Individual component testing
- **Integration Tests**: System integration testing
- **Simulation Tests**: Production simulation validation
- **Performance Tests**: System performance validation

## 📋 Structure

```
tests-orbis/
├── README.md           # This file
├── unit/              # Unit tests
├── integration/       # Integration tests
├── simulation/        # Simulation tests
└── performance/       # Performance tests
```

## 🚀 Running Tests

```bash
# Run all tests
pytest tests-orbis/

# Run specific test category
pytest tests-orbis/unit/
pytest tests-orbis/integration/

# Run with coverage
pytest tests-orbis/ --cov=src-orbis/
```

## 🔗 Related Folders

- `docs-orbis/` - Orbis documentation
- `src-orbis/` - Orbis source code
- `Node-RED/` - Original Fischertechnik Node-RED flows
- `PLC-programs/` - Original Fischertechnik PLC programs

---

*Orbis Development Team* 