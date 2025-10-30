### Testanpassungen vs. Codeänderungen

Wenn sich das beabsichtigte Verhalten ändert (z. B. neue SVG-Assets, andere Icons, überarbeitete Darstellung), dürfen Tests nicht der Grund sein, produktiven Code wieder rückgängig zu machen. Stattdessen:

- Passe die Tests an das neue, fachlich gewünschte Verhalten an.
- Lasse produktives Verhalten maßgeblich sein (Guides/ADRs/How-To).
- Dokumentiere die Anpassung im PR (kurz Was/Warum, Link zum Guide/ADR).

Ziel: Konsistenz zwischen fachlicher Entscheidung, Code und Tests. Veraltete Tests dürfen produktive Verbesserungen nicht blockieren.


