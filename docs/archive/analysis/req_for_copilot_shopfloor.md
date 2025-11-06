Darstellung eines Grundrisses einer Fabrikhalle (shopfloor)
Bestehend aus 12 Komponenten (Zellen)
Angeordnet in 3 Reihen und 4 Spalten.
Zur Formalisierung wird dafür die ZELLE[row,col] verwendet.
Wenn es sich um Quadrate handeln würde, wäre das einfach.
Aber es gibt folgende Abweichungen in den Dimensionen
Ich wähle als Normierung  Einheiten in px (Breite x Höhe)
ZELLE [0,0]: Name "COMPANY" Maße [200px x 100px] (blaues Rechteck)
ZELLE [0,1]: Name "MILL" Maße [200px x 200px] rotes Quadrat
ZELLE [0,2]: Name "AIQS" Maße [200px x 200px] rotes Quadrat
ZELLE [0,3]: Name "SOFTWARE" Maße [200px x 100px] blaues Rechteck
ZELLE [1,0]: Name "HBW" Maße [200px x 300px] (grünes Rechteck)
ZELLE [1,1]: Name "INTERSECTION-1" Maße [200px x 200px] lila Quadrat
ZELLE [1,2]: Name "INTERSECTION-2" Maße [200px x 200px] lila Quadrat
ZELLE [1,3]: Name "DPS" Maße [200px x 300px] grünes Rechteck
ZELLE [2,0]: Name "DRILL" Maße [200px x 200px] (rotes Quadrat)
ZELLE [2,1]: Name "INTERSECTION-3" Maße [200px x 200px] lila Quadrat
ZELLE [2,2]: Name "INTERSECTION-4" Maße [200px x 200px] lila Quadrat
ZELLE [2,3]: Name "CHRG" Maße [200px x 200px] rotes Quadrat

Insgesamt das der Shopfloor die Dimension 800px x 600 px.

Für die Visualisierung, werden über ein Mapping SVGs verwendet.
Das Layout soll als ganzes skalierbar dargestellt werden 100% = (800 x 600), Darstellung aber auch mit Skalierung 0,5 -> (400 x 300)
Normalerweise ist keine Umrandung sichtbar.
Bei klick in die Darstellung, wird die entsprechende Zelle gehighlightet, durch dicke Umrandung der Zelle. (klickbare Darstellung)
Außerdem soll es eine nicht klickbaren Darstellung geben, bei der entsprechende Zellen gehighlightet werden können. (Z.B active cell = DRILL -> highlight von Zelle [2,0])
Außerdem soll es eine Mouse-Over Möglichkeit geben: Mit Mouse über eine Zelle bewegen (Info über Inhalt der Zelle wird dargestellt Mouse bewegt sich über Zelle [2,0] -> INFO : "DRILL"+ ggf weitere Infos)und die ZELLE wird farblich hervorgehoben (dünner Rand und Füllung mit orange).
Die Zellpositionen werden zur Ermittlung von Routen verwendet. Beispiel Route von Zelle [1,1] nach Zelle [1,3]. Darstellung einer Route vom Rand der ZELLE [1,1] zum Rand der Zelle [1,3] Die Route verläuft immer exakt durch die Mittelpunkte dere Zellen mit Namen INTERSECTION-1-4.:
DIE ZELLEN [0,0] und [0,3] nehmen nicht an der Routenberechnung teil. Sie haben Sonderstatus.
START und ZIEL einer Route ist immer einer Zelle mit roter oder grüner UMrandung. Ausnahme, WENN HBW das ZIEL ist und kein START angegeben, dann ist INTERSECTION-2 der Start. WENN DPS das ZIEL und kein START angegeben , dann ist INTERSECTION-1 der Start.
Besonderheit bei ZELLE [1,0] und [1,3]. Hierbei handelt es sich um Compound-Zellen. Diese werden beim Highlight als ganzes umrandet. Bestehen aber intern aus 3 Unterkomponenten.
Zur Bestimmung von Routen wird die Hauptkomponente verwendet (rotes Quadrat). Die UnterKomponenten (gelbe Quadrate) sind nur visuellen Darstellung des Inhaltes der Zelle wichtig. 

Die Darstellung des shopfloor_layouts nwird in einer streamlit app verwendet.
(wir haben schon eine Impementierung, aber da funktinioniert das Highlighting nicht wie erwünscht)


