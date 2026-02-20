# ORBIS SmartFactory Tests

**Session Manager Tests** liegen jetzt im Paket: **`session_manager/tests/`**

## Test-Ausführung

```bash
# Session Manager Tests (Python/pytest)
python -m pytest session_manager/tests/ -v

# OSF Angular/Jest Tests
nx test osf-ui
```

## Verzeichnis

- `session_manager/tests/` – Session Manager Python-Tests (Logging, Logger, Cleanup)
- `osf/` – OSF Angular-Tests in `*.__tests__/` und `*.spec.ts`

---

*Hinweis: `tests/test_helper_apps/` wurde entfernt – Tests nach `session_manager/tests/` migriert.*
