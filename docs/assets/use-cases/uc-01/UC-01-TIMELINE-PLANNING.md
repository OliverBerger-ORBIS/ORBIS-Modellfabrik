UC-01 Track & Trace Genealogy - Timeline Planning Template
==========================================================

**Status:** Wird umgearbeitet (2026-01-21)
**Ziel:** Layout-Planung in visuellen Tools vor Code-Implementierung

Dieses Dokument dient als Vorlage für die Planung der Timeline-Synchronisation in einem visuellen Tool (Figma, Draw.io, Inkscape, etc.).

**WICHTIG:** Basierend auf ChatGPT-Analyse werden zwei getrennte Visuals empfohlen:
1. Objekt-Geflecht (ER/Domain-Mesh) - zeigt Korrelationen
2. Event-Flow mit Soll/Ist-Overlay (Timeline) - zeigt Plan vs. Ist

Siehe auch: `UC-01_Track_Trace-genealogy.md` → Abschnitt "Umarbeitung & Verbesserungsvorschläge"

COLUMN DIMENSIONS
-----------------
- ViewBox: 1920 x 1300px
- Column Y: 300px
- Column Height: 900px
- Header Height: 50px
- Available Height for Timeline: 900 - 50 = 850px (mit Padding: ~750px)

COLUMN STRUCTURE
----------------
1. Business Events (x: 80, width: 400)
2. Production Plan (x: 520, width: 400)
3. Actual Path (x: 960, width: 400)
4. Correlated Timeline (x: 1400, width: 480)

TIMELINE EVENTS (Chronological Order)
--------------------------------------
T0: Purchase Order Created
    - Business Events: purchase-order-chip

T1: Storage Order: Goods Receipt (DPS)
    - Production Plan: storage-plan-dps

T2: Storage Order: NFC Read
    - Production Plan: storage-plan-nfc

T3: Storage Order: Order Created
    - Production Plan: storage-plan-order

T4: Storage Order: Transport to Warehouse
    - Production Plan: storage-plan-transport
    - Correlated Timeline: timeline-1 (START TRANSFER)

T5: Storage Order: Warehouse Storage
    - Production Plan: storage-plan-warehouse
    - Actual Path: actual-warehouse
    - Correlated Timeline: timeline-2 (WAREHOUSE MOVE)

T6: Customer Order Created
    - Business Events: customer-order-id

T7: Production Order: Warehouse
    - Production Plan: production-plan-warehouse

T8: Production Order: Drill - PICK
    - Production Plan: production-plan-drill
    - Actual Path: actual-drill
    - Correlated Timeline: timeline-3 (DRILL PICK)

T9: Production Order: Drill - PROCESS
    - Correlated Timeline: timeline-4 (DRILL PROCESS)

T10: Production Order: Drill - DROP
    - Correlated Timeline: timeline-5 (DRILL DROP)

T11: Production Order: Quality - PICK
    - Production Plan: production-plan-quality
    - Actual Path: actual-quality
    - Correlated Timeline: timeline-6 (QUALITY PICK)

T12: Production Order: Quality - PROCESS
    - Correlated Timeline: timeline-7 (QUALITY PROCESS)

T13: Production Order: Quality - DROP
    - Correlated Timeline: timeline-8 (QUALITY DROP)

T14: Production Order: DPS
    - Production Plan: production-plan-dps
    - Actual Path: actual-dps

TIMELINE CALCULATION
--------------------
- Number of Time Points: 15 (T0-T14)
- Number of Gaps: 14
- Available Height: ~750px (with padding)
- Time Step: 750 / 14 ≈ 53.6px per time point
- Base Y: 300 (column.y) + 50 (header) + 60 (padding) = 410px

Y-COORDINATE FORMULA
--------------------
y = baseY + (timeIndex * timeStep)
y = 410 + (timeIndex * 53.6)

Example:
- T0: y = 410 + (0 * 53.6) = 410px
- T5: y = 410 + (5 * 53.6) = 678px
- T14: y = 410 + (14 * 53.6) = 1160px

ADDITIONAL ELEMENTS (Not Timeline-Synchronized)
------------------------------------------------
Business Events - Purchase Order Lane:
- purchase-order-id (below purchase-order-chip)
- supplier-id
- material-batch
- erp-id-purchase

Business Events - Customer Order Lane:
- customer-id (below customer-order-id)
- production-order-id
- erp-id-customer

Actual Path:
- actual-mill (no events, parallel RED production)

Correlated Timeline - NFC Tag:
- nfc-tag-chip (static, not timeline-synchronized)

Correlated Timeline - Order Context:
- order-production
- order-customer
- order-material
- order-erp

PLANNING CHECKLIST
------------------
[ ] Alle Timeline-Events sind korrekt zugeordnet
[ ] Y-Koordinaten bleiben innerhalb Column-Grenzen (300-1200px)
[ ] Zeitliche Abfolge ist logisch korrekt
[ ] Events, die gleichzeitig auftreten, haben gleiche Y-Koordinate
[ ] Abstände zwischen Zeitpunkten sind gleichmäßig
[ ] Nicht-Timeline-Elemente sind korrekt positioniert

NOTES
-----
- MILL Station (actual-mill) hat keine Events im Timeline (parallel RED production)
- FTS ist transparent (keine Station in Actual Path)
- Events werden nur in Column 4 (Correlated Timeline) dargestellt
- PICK/Process/DROP Events sind in Column 4 für Drill und Quality
