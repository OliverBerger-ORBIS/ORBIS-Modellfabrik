# Git Commit-Regeln

**Grundprinzip:** Alles was wir behalten sollen, gehört in den Commit. Alles was wir nicht behalten, soll gelöscht werden.

---

## Entscheidungsfragen vor dem Commit

1. **Was wurde seit dem letzten Commit gemacht?**
2. **Ist es wichtig?** Sollen wir es behalten?
3. **Ja** → In den Commit aufnehmen (auch wenn es mehrere Features sind)
4. **Nein** → Löschen

---

## Was gehört in den Commit

- **Feature-Code** inkl. Services, Specs, Tests
- **Dokumentation** zu den Änderungen (Analysen, DRs, How-tos)
- **Konfiguration** die zur Funktionalität gehört
- **Session-Logs** die aufwendig erstellt wurden und nicht einfach reproduzierbar sind (Infrastruktur fehlt, spezielle Abläufe, Stillstände etc.)
  - Lieber eine Session zu viel im Repo als wertvolle Info zu verlieren

---

## Was nicht in den Commit gehört

- **On-the-fly Analyse-Skripte** – temporär erstellt, nicht produktiv genutzt
- **Umsetzungspläne/Implementierungspläne** – dienen der strukturierten Vorgehensweise (und Cursor-Crash-Recovery), nicht der dauerhaften Dokumentation. Wichtige Infos gehören in How-tos und DRs.
- **Lokale Build-Artefakte** – gehören in .gitignore
- **Persönliche/experimentelle** Änderungen, die verworfen werden

---

## Session-Logs: Umgang

- Session-Logs können wertvoll sein (Hardware-Aufnahmen, Stillstand-Szenarien, Quality-Fail)
- Bei Unsicherheit: **lieber committen** als verlieren
- Übersicht: [data/osf-data/sessions/INVENTORY.md](../../data/osf-data/sessions/INVENTORY.md) – welcher Log für welche Analyse?

---

## Referenz

- [.cursorrules – Commit vorbereiten](../../.cursorrules) (Abschnitt „Commit vorbereiten“)
- [Session Inventory](../../data/osf-data/sessions/INVENTORY.md)
