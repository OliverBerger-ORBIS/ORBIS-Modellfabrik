# Agile Production Simulation

> ⚠️ **VERIFIKATION AUSSTEHEND**: Diese Dokumentation basiert auf einer Hypothese und wurde noch nicht verifiziert. Die beschriebenen Systemkomponenten und Architektur müssen noch getestet und validiert werden.

## Überblick

Effizienz, Agilität und Flexibilität sind beim Aufbau aktueller und zukünftiger Fabriken unverzichtbar. fischertechnik stellt nun ein Trainingsmodell solch einer flexiblen und modularen Fabrik vor – die Agile Production Simulation.

## Systemkomponenten

Die Fabrik besteht aus einzelnen Modulen wie:
- Warenein- und Ausgang
- Hochregallager
- Frässtation
- Bohrstation
- Qualitätssicherung mit KI

Ein fahrerloses Transportsystem transportiert Werkstücke flexibel zwischen den einzelnen Stationen und gewährleistet einen flexiblen Produktionsprozess, der an die Kundenwünsche angepasst werden kann. Die Fabrik kann um einen Brennofen, weitere Bohr- oder Frässtationen und auch um zusätzliche fahrerlose Transportsysteme erweitert werden.

## Werkstück-Management

Jedes Werkstück enthält einen NFC-Tag, auf den Produktionsdaten geschrieben werden:
- Farbe des Werkstücks
- Zeitpunkt Anlieferung
- Zeitpunkt Ein- und Auslagerung
- Durchgeführte Produktionsschritte
- Durchführung Qualitätsprüfung

Die verschieden farbigen Werkstücke (weiß, rot, blau) durchlaufen verschiedene Produktionsprozesse und durchlaufen somit unterschiedliche Stationen in der Fabrik und haben unterschiedliche Durchlaufzeiten.

## Steuerungssystem

Gesteuert wird die Fabrik von einer zentralen Steuerung (Raspberry Pi 4 Model B), die mit den Steuerungen der einzelnen Fabrikmodule, SPS Siemens S7 1200 in der 24V Version, vernetzt ist. Die zentrale Steuerung kommuniziert über die standardisierte FTS-Schnittstelle VDA 5050 und steuert die Transportaufträge für das FTS. Für die Kommunikation wird das MQTT-Protokoll (Message Queuing Telemetry Transport) verwendet.

## Cloud-Integration

Die Fabrik ist außerdem über einen WLAN-Router mit der fischertechnik Cloud verbunden, in der sich ein Online-Shop für die Bestellung von Werkstücken durch den Kunden befindet. Darüber hinaus sind Dashboards verfügbar für:
- Auftragssteuerung
- Visualisierung des Fabrikzustands
- Ermittlung von Kennzahlen

Zur Simulation von Fernwartung werden die Bilder, die die bewegliche Kamera in der Fabrik aufnimmt, im Dashboard angezeigt, so dass der Zustand der Fabrik remote eingesehen werden kann.

## Physische Struktur

Physisch werden die Grundplatten einzelnen Module der Fabrik über ein Nut- und Federprinzip miteinander zu einer zusammenhängenden Grundplatte verbunden. An den offenen Enden können weitere Module hinzugefügt und im Dashboard konfiguriert werden.

## Didaktisches Material

Das didaktische Begleitmaterial bietet neben einer detaillierten Einführung in die Handhabung der Fabrik umfangreiches Lehrmaterial. Inhalte sind bspw.:
- Grundlagen von Industrie 4.0
- Modulare Produktion
- Intelligente Vernetzung
- Mensch-Technik-Organisation
- Digital Twin
- Sensordatenauswertung in Echtzeit
- Und vieles mehr