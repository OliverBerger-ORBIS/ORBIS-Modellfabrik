# FTS / AGV: Encoder-Motor tauschen (APS-Trainingsmodell)

**Stand:** 06.08.2026  
**Kontext:** AGV-2 / FTS Nr. 2 — rechter Vorderradantrieb (M2/C2) ausgefallen; Ersatzmotor von fischertechnik (03.08.2026); **Tausch erfolgreich 06.08.2026**.

---

## Reparatur FTS Nr. 2 – rechter Vorderradantrieb (06.08.2026) ✅

### Fehlerbild

Der rechte Vorderradantrieb (**M2/C2**) lief zunächst nur sehr langsam bei maximaler Ansteuerung und fiel anschließend vollständig aus. Die übrigen drei Antriebe funktionierten im ROBO Pro Coding-Schnittstellentest normal.

### Antriebszuordnung (verifiziert)

| Kanal | Position |
|-------|----------|
| M1/C1 | links vorne |
| M2/C2 | rechts vorne |
| M3/C3 | links hinten |
| M4/C4 | rechts hinten |

### Diagnose

- Mechanische Blockade / Verspannung des rechten Vorderrads geprüft und **ausgeschlossen**.
- Am vorhandenen Motorkabel von M2 bei maximaler Ansteuerung ca. **7,9–8,2 V** gemessen → TXT-Ausgang und Motorleitung grundsätzlich OK.
- Ersatzmotor **vor Einbau** direkt an das vorhandene M2-Kabel angeschlossen → lief im Schnittstellentest **einwandfrei** (Fehler lokalisiert am alten Motor).

### Maßnahme

Defekter rechter Vordermotor durch Ersatzmotor ausgetauscht.

### Ergebnis

Schnittstellentest nach Einbau: **alle vier Antriebsmotoren** laufen. FTS Nr. 2 wieder funktionsfähig.

**Nächster Schritt:** AGV-2 aufladen; danach wieder im Shopfloor einsetzen. Danach möglich: Sprint-28 **Session-Teil B (2-AGV)**.

---

## Hersteller-Hinweise (Mail Steiger, 06.08.2026)

| Frage | Antwort (fischertechnik) |
|-------|--------------------------|
| Eigene Bauanleitung für APS-FTS / Trainingsmodelle? | **Nein** — Modelle von externem Zulieferer. |
| Orientierung? | Ähnlich Omniwheel; PDF ab **S. 26** Antrieb — für APS-Zerlegeweg **wenig hilfreich** (Erfahrung 06.08.). |
| Vor Demontage? | Fotos; zweites FTS als Referenz. |
| Fallback | FTS an fischertechnik einsenden. |

Omniwheel-PDF (nur Hintergrund): [BA_185600_BAUANLEITUNG_HIGHTECH.pdf](https://fiproductmedia.azureedge.net/media/Marketing%20Materials/Operating%20instructions/BA_185600_BAUANLEITUNG_HIGHTECH.pdf)

---

## Empfohlenes Vorgehen (nächster Motortausch)

1. Schnittstellentest: welcher Kanal (M×/C×) fällt aus? Zuordnung oben nutzen.
2. Spannung am Motorkabel messen; Ersatzmotor **am vorhandenen Kabel** vor Einbau testen.
3. Mechanik (Blockade/Verspannung) ausschließen.
4. Motor tauschen; Schnittstellentest aller vier Antriebe.
5. Aufladen → Shopfloor-Einsatz → ggf. 2-AGV-Sessions.

---

## Abgrenzung

- Kein öffentliches APS-Zerlege-Manual (Stand Mail 06.08.2026); Praxis: Diagnose + Motortausch vor Ort.
- Software: [TXT-FTS](../06-integrations/TXT-FTS/README.md), `integrations/TXT-FTS/`.
- Sprint: [sprint_28.md](../sprints/sprint_28.md)

---

## Historie

| Datum | Ereignis |
|-------|----------|
| 23.07.2026 | RoboPro-Schnittstellen-Test — Verdacht Kabelbruch oder Motor |
| 27.07.2026 | Multimeter: Encoder-Motor defekt |
| 30.07.2026 | fischertechnik sendet Ersatzmotor (Mail Steiger) |
| 03.08.2026 | Ersatzmotor eingetroffen |
| 04.08.2026 | Aufbau-Anleitung bei Herrn Steiger angefragt |
| 06.08.2026 | Antwort: keine APS-Bauanleitung; Omniwheel-PDF |
| **06.08.2026** | **Reparatur OK:** M2/C2 (rechts vorne) getauscht; alle 4 Antriebe laufen; Aufladen → Wiedereinsatz |
