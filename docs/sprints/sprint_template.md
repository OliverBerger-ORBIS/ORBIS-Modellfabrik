# Sprint X – [Titel]

**Zeitraum:** [von] – [bis] · **Status:** Laufend | Abgeschlossen  
**Vorheriger Sprint:** [sprint_XX.md](./sprint_XX.md)

**Kurz:** [Ein Satz]

---

## Releases (optional)

| Version | Datum | Inhalt |
|---------|--------|--------|
| … | … | … |

---

## Externe Termine & Outreach (optional)

*Tabelle: Datum, Event (Kundentermin / Messe / Demo / **Blog**), Nutzen für OSF. Blog-Artikel gleichrangig zu Terminen (externe Wirkung). Größere Ereignisse zusätzlich bei Sprint-Abschluss in **PROJECT_STATUS** → Spalte **Externe Events** eintragen.*

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| … | … | … |

---

## Coverage Standing

**Pflicht** in jedem Sprint (Position: nach Externe Termine, vor Aufgaben). Ohne Standing kein Sprint-Abschluss.

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline aus Vorgänger-Endmessung) | … | …% | …% | …% | …% | 30 / 42 / 47 / 46 | … |
| Aktuell | … | …% | …% | …% | …% | 30 / 42 / 47 / 46 | … |

- **Messmethode:** `npm run test:coverage` → `coverage/osf-ui/index.html` (Details: [test-coverage-status.md](../07-analysis/test-coverage-status.md))
- **Top-3 Gaps (Test-Fokus):**
  1. …
  2. …
  3. …
- **Pflege:** Baseline unverändert; nach Messung nur **Aktuell** + Top-Gaps. Am Sprintende Pflicht-Messung vor Abschluss.

---

## Aufgaben (thematisch, mit Haken)

Unter **`### Thema`** nur Zeilen mit `- [ ]` oder `- [x]`. **Nicht** zwei Listen „offen“ und „erledigt“.

### [Thema A]

- [ ] Noch zu tun …
- [x] Erledigt …

### [Thema B]

- [ ] …

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] **Coverage Standing:** Endmessung (`npm run test:coverage`) → `Aktuell` + Top-Gaps; bei Bedarf [test-coverage-status.md](../07-analysis/test-coverage-status.md) aktualisieren
- [ ] Sprint X: Status Abgeschlossen, Datum
- [ ] Sprint X+1 anlegen, offene `[ ]` übernehmen; Coverage-Baseline = Endmessung dieses Sprints
- [ ] PROJECT_STATUS
- [ ] Roadmap kurz prüfen

---

## Später (Backlog)

*Hier nur Stichpunkte ohne Checkbox, wenn es keine klaren Sprint-Tasks sind.*

---

## Links

- …

---

*Stand: [Datum]* · Doku-Workflow: [sprints_README.md](sprints_README.md)
