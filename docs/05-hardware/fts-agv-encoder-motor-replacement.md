# FTS / AGV: Encoder-Motor tauschen (APS-Trainingsmodell)

**Stand:** 06.08.2026  
**Kontext:** AGV-2 / FTS Nr. 2 — Encoder-Motor defekt (Multimeter 27.07.2026); Ersatzmotor von fischertechnik eingetroffen (03.08.2026).  
**Quelle:** Mail fischertechnik (Herr Steiger), Antwort auf Anfrage Aufbau-/Zerlege-Anleitung (06.08.2026).

---

## Kurzfassung

| Frage | Antwort (fischertechnik) |
|-------|--------------------------|
| Eigene Bauanleitung für APS-FTS / Trainingsmodelle? | **Nein** — Modelle werden von einem **externen Zulieferer** aufgebaut (eigene Konstruktionssoftware). |
| Orientierung für Motortausch? | Aufbau **ähnlich Omniwheel-Modell**; in der Omniwheel-Bauanleitung ab **Seite 26** Montage der **Antriebseinheiten / Motoren**. |
| Vor Demontage? | **Fotos** aus verschiedenen Perspektiven; zweites FTS als **Referenz**. |
| Falls Umbau scheitert? | FTS an fischertechnik **einsenden** — Motortausch dort im Haus. |

---

## Referenz-Bauanleitung (Omniwheel / Hightech)

Offizielle PDF (fischertechnik Product Media):

[BA_185600_BAUANLEITUNG_HIGHTECH.pdf](https://fiproductmedia.azureedge.net/media/Marketing%20Materials/Operating%20instructions/BA_185600_BAUANLEITUNG_HIGHTECH.pdf)

**Relevant für Motortausch:** ab **Seite 26** — Montage der Antriebseinheiten bzw. Motoren.

> Das APS-FTS ist **nicht** identisch mit dem Omniwheel-Bausatz, aber laut Hersteller **grundsätzlich sehr ähnlich**. Omniwheels-/Smarttech-PDFs ersetzen keine APS-Zerlege-Doku — sie dienen nur als **Analogie** für den Antrieb.

---

## Empfohlenes Vorgehen (vor Ort)

1. **Dokumentieren vor Demontage**
   - Fotos von mehreren Seiten (Gehäuse, Kabelwege, Motorlage, Encoder-Seite).
   - Bei Bedarf kurze Notizen zu Steckerfarben / Kabelrouting.
2. **Zweites FTS parallel**
   - Das intakte FTS (AGV-1) als Orientierung für Zusammenbau und Lage der Teile nutzen — nicht demontieren.
3. **Montage analog Omniwheel S. 26ff**
   - Antriebseinheit / Motor gemäß PDF; APS-Abweichungen visuell am zweiten FTS abgleichen.
4. **Nach Einbau**
   - RoboPro-Schnittstellen-Test / Encoder-Prüfung (wie Sprint-26/27).
   - Kurzfahrt und Pairing im FT-LAN verifizieren.
5. **Fallback**
   - Umbau nicht erfolgreich → FTS an fischertechnik zur Überprüfung / Motortausch einsenden (Angebot aus der Mail).

---

## Abgrenzung

- **Kein** öffentliches Zerlege-Manual speziell für das APS-24V-FTS (Stand Mail 06.08.2026).
- TXT-/MQTT-/VDA-5050-Software: siehe [TXT-FTS](../06-integrations/TXT-FTS/README.md) und `integrations/TXT-FTS/`.
- Sprint-Status: [sprint_27.md](../sprints/sprint_27.md) — Aufgabe „Kontrolle FTS Nr. 2“.

---

## Historie

| Datum | Ereignis |
|-------|----------|
| 23.07.2026 | RoboPro-Schnittstellen-Test — Verdacht Kabelbruch oder Motor |
| 27.07.2026 | Multimeter: **Encoder-Motor defekt** |
| 30.07.2026 | fischertechnik sendet Ersatzmotor (Mail Steiger) |
| 03.08.2026 | Ersatzmotor eingetroffen |
| 04.08.2026 | Aufbau-Anleitung bei Herrn Steiger angefragt |
| 06.08.2026 | Antwort: keine separate APS-Bauanleitung; Omniwheel-PDF ab S. 26; Fotos + 2. FTS; Einsende-Option |
