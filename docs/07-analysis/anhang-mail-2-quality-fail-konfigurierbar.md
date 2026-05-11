# Anhang Mail 2 – APS-CCU Änderung: Quality-Fail-Verhalten konfigurierbar

Stand: 2026-05-11

## Fachliche Zielsetzung

Bei `PRODUCTION`-Orders mit `CHECK_QUALITY = FAILED` an AIQS soll das Verhalten konfigurierbar sein:

- Modus A: bisheriges Fischertechnik-Verhalten (automatischer Ersatzauftrag)
- Modus B: kein automatischer Ersatzauftrag; Entscheidung über übergeordneten Business-Prozess (SAP/ERP/MES/DSP)

Wichtig: Andere parallele Orders sollen normal weiterlaufen; Module/FTS sollen nicht unnötig blockieren.

## Aktuell umgesetztes Verhalten (ORBIS-Version)

Derzeit ohne Schalter, hart auf „kein automatischer Ersatzauftrag“ gesetzt.

Ablauf im Quality-Fail-Pfad:

1. AIQS wird für die betroffene Order freigegeben
2. Step auf `ERROR`
3. verbleibende Steps werden abgebrochen
4. Order auf `ERROR`
5. Order wird von aktiv nach completed verschoben
6. FTS wird per `sendClearModuleNodeNavigationRequest(...)` von AIQS wegbewegt
7. blockierte FTS-Schritte werden mit `retriggerFTSSteps()` erneut angestoßen

## Relevante Upstream-Dateien (Agile-Production-Simulation-24V-Dev, Branch `release`)

- `central-control/src/modules/order/management/order-management.ts`
- `central-control/src/modules/order/management/order-management.test.ts`
- `central-control/src/modules/fts/navigation/navigation.ts`

## Relevante Stellen im ORBIS-Spiegel (mit Zeilen)

- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L614-L631)
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L88-L105)
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L888-L905)
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L842-L858)
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L300-L399)
- [navigation.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts#L338-L390)
- [order-management.test.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.test.ts#L653-L712)

## Kritischer Hinweis zur heutigen Implementierung

`sendClearModuleNodeNavigationRequest(...)` wählt kein fachlich fixes Ziel wie HBW, sondern das erste freie verbundene Modul (ohne Charger).
Dadurch kann das Verhalten je nach Belegung/Modulreihenfolge variieren.

- [navigation.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts#L347-L356)

## Bitte an Fischertechnik

1. Prüfen, ob das Verhalten als optionale Erweiterung sinnvoll ist.
2. Falls ja: Bitte konfigurierbar (Schalter/Config) implementieren.
3. Bitte unsere aktuelle technische Umsetzung auf Korrektheit im Parallelbetrieb prüfen und ggf. Rückmeldung geben.

Mögliche Konfiguration:

- `autoReplaceOnQualityFail = true` → automatischer Ersatzauftrag
- `autoReplaceOnQualityFail = false` → keine automatische Ersatzorder; externe Business-Entscheidung