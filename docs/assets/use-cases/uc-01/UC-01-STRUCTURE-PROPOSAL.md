# UC-01 Track & Trace Genealogy - Struktur-Vorschlag

## Problem-Analyse

### Aktuelle Probleme:
1. **I18n-Texte werden nicht ersetzt**: Keys werden nicht korrekt geladen/ersetzt
2. **Business Events Struktur unklar**: Zu viele Lanes, Verlinkungen nicht klar
3. **Zeitliche Abfolge nicht deutlich**: Purchase Order → Storage Order → Customer Order → Production Order

## Neue Struktur-Vorschlag

### Column 1: Business Events (ERP-Quellen)
**Zweck**: Zeigt die ursprünglichen Business-Events aus dem ERP

**Lanes:**
1. **Purchase Order (Supplier Order)**
   - Purchase Order ID
   - Supplier ID (aus ERP)
   - Bestelldatum
   - ERP-ID
   - Material/Batch (optional)
   
2. **Customer Order**
   - Customer Order ID
   - Customer ID (aus ERP)
   - Bestelldatum
   - ERP-ID
   - Produktionsanforderungen (optional)

**Verlinkungen:**
- Purchase Order → Storage Order (Column 2)
- Customer Order → Production Order (Column 2)

### Column 2: Production Plan (Geplante Sequenz)
**Zweck**: Zeigt die geplante Produktionssequenz basierend auf den Business-Events

**Lanes:**
1. **Storage Order (Plan)**
   - Storage Order ID
   - Verlinkt mit Purchase Order
   - Geplante Lagerbewegung
   
2. **Production Order (Plan)**
   - Production Order ID
   - Verlinkt mit Customer Order
   - Geplante Sequenz:
     - Warehouse
     - DRILL
     - Quality
     - DPS

**Verlinkungen:**
- Storage Order → Actual Path (Column 3)
- Production Order → Actual Path (Column 3)

### Column 3: Actual Path (Tatsächlicher Weg)
**Zweck**: Zeigt den tatsächlichen Weg, der von FTS/AGV gefahren wurde

**Lanes:**
1. **FTS Route (Actual)**
   - Tatsächliche Sequenz (kann von Plan abweichen):
     - Warehouse
     - FTS Transfer
     - DRILL (oder andere Station)
     - Quality (oder andere Station)
     - DPS (oder andere Station)
     - Weitere Stationen (wenn FTS andere Ware gleichzeitig transportiert)

**Verlinkungen:**
- Actual Path → Correlated Timeline (Column 4)
- NFC-Tag wird während Anlieferung vergeben (Verlinkung zu Purchase Order)

### Column 4: Correlated Timeline (Korrelierte Events)
**Zweck**: Zeigt die korrelierte Timeline aller Events entlang der NFC-Tag/Workpiece-ID

**Lanes:**
1. **NFC-Tag / Workpiece ID**
   - NFC-Tag ID (z.B. A5873A2-A4525)
   - Verlinkt mit Purchase Order (während Anlieferung vergeben)
   - Verlinkt mit Storage Order
   - Verlinkt mit Production Order
   
2. **Event Timeline**
   - Timeline mit nummerierten Events:
     1. START TRANSFER (Purchase Order Anlieferung)
     2. WAREHOUSE MOVE (Storage Order)
     3. STATION PROCESS (DRILL oder andere)
     4. QUALITY CHECK
     5. END TRANSPORT
   
3. **Order Context**
   - Production Order ID
   - Customer Order ID
   - Material / Batch
   - ERP-ID

**Verlinkungen:**
- NFC-Tag → Alle Business Events (Purchase Order, Customer Order)
- NFC-Tag → Event Timeline
- Event Timeline → Order Context

## Implementierungs-Plan

### Phase 1: I18n-Problem beheben
- Prüfen, ob Keys korrekt geladen werden
- Debug-Logging hinzufügen
- Fallback-Mechanismus verbessern

### Phase 2: Business Events überarbeiten
- Nur 2 Lanes: Purchase Order und Customer Order
- Entfernen: Storage Order Lane aus Column 1
- Entfernen: Supplier Info, Material Batch, ERP-ID als separate Chips (in Purchase Order integrieren)

### Phase 3: Production Plan anpassen
- 2 Lanes: Storage Order (Plan) und Production Order (Plan)
- Storage Order verlinkt mit Purchase Order
- Production Order verlinkt mit Customer Order

### Phase 4: Actual Path anpassen
- Kann von Plan abweichen
- Markierung von Abweichungen (optional: andere Farbe)

### Phase 5: Correlated Timeline anpassen
- NFC-Tag als zentrales Element
- Verlinkungen zu allen Business Events
- Event Timeline mit korrekter Sequenz

## Datenfluss

```
Purchase Order (ERP) 
  → Storage Order (Plan)
    → Actual Path (FTS Route)
      → Correlated Timeline (via NFC-Tag)

Customer Order (ERP)
  → Production Order (Plan)
    → Actual Path (FTS Route)
      → Correlated Timeline (via NFC-Tag)

NFC-Tag (während Anlieferung vergeben)
  → Verlinkt mit Purchase Order
  → Verlinkt mit Storage Order
  → Verlinkt mit Production Order
  → Verlinkt mit Event Timeline
```

## Offene Fragen

1. Soll die Storage Order in Column 2 als Timeline dargestellt werden oder als einzelner Chip?
2. Wie sollen Abweichungen im Actual Path visuell markiert werden?
3. Sollen Bestelldaten (Datum) als separate Chips oder innerhalb der Order-Chips angezeigt werden?
4. Wie soll die Verlinkung zwischen Purchase Order und Storage Order dargestellt werden (Connection-Linie)?
