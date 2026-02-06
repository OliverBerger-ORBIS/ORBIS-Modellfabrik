# Documentation Overview

- [Project Strategy](01-strategy/README.md)
- [Architecture](02-architecture/README.md)
- [Decision Records](03-decision-records/README.md)
- [How-To Guides](04-howto/README.md)
- [Integrations](06-integrations/00-REFERENCE/README.md)

Key How-To Guides
- [UI Symbols Usage Guide](04-howto/ui_symbols.md) - Centralized SVG icons for headings and shopfloor
- [Shopfloor Layout Guide](04-howto/SHOPFLOOR_LAYOUT_GUIDE.md)
- [MQTT Client Connection](04-howto/mqtt_client_connection.md)

## 📂 Asset Structure & Diagrams

We distinguish between the architecture of the **OSF Demonstrator** (the tool) and the **ORBIS Products** (the content being simulated).

- **`docs/assets/architecture/osf-architecture/`**  
  Diagrams explaining the internal structure of the OSF application (Angular, Services, MQTT-Flows).
- **`docs/assets/products/`**  
  Diagrams covering the functional logic of the simulated systems.
  - **`products/common/domain-model/`** → Shared entities (Machine, SinglePart, Order) used across DSP and MES.
  - **`products/dsp/`** → Specifics of the Distributed Shopfloor Processing architecture.
- **`docs/assets/use-cases/{uc-id}/diagrams/`**  
  Flow charts and timelines specific to a single use case (e.g., Track & Trace sequence).

(Former icon guides have been archived; see `docs/archive/` if needed.)