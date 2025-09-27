# omf2 Refactoring-Branch

Dies ist das neue Refactoring-Verzeichnis für die nächste Generation der Anwendung.

- **Registry**: Vorübergehend in `omf2/registry/`
- **Komponenten**: Komplett refaktoriert in `omf2/`
- **Migration**: Nach Abschluss → alles nach Projekt-Root verschieben!

**Wichtige Hinweise:**
- Während der Entwicklung und Tests greift alles in `omf2/` ausschließlich auf die Registry in `omf2/registry/` zu.
- Nach erfolgreichem Abschluss werden die alten Verzeichnisse gelöscht und `omf2/` → `omf/`, `omf2/registry/` → `registry/` verschoben.

## Migration

1. `rm -rf omf/ registry/`
2. `mv omf2 omf`
3. `mv omf/registry registry`

Jetzt ist das neue System live und aufgeräumt!