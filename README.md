# hamann-xml
XML-Dateien & Einstellungen für hamann-ausgabe.de & development.hamann-ausgabe.de

## Branches
|Branch Name|Branch Zweck                                            |
|-----------|--------------------------------------------------------|
| main      | Code & Einstellungen für development.hamann-ausgabe.de |
| realease  | Code & Einstellungen für hamann-ausgabe.de             |

## Einstellungen
```
"FeatureManagement": {
    "AdminService":  true,
    "LocalPublishService": true
  },
```
`FeatureManagement` schaltet bestimmte Features auf der Webseite ein oder aus:
|Name                      |Funktion                                                                        |
|--------------------------|--------------------------------------------------------------------------------|
|AdminService              |Schaltet den Admin-Bereich ein oder aus                                         |
|LocalPublishService       |Schaltet den Bereich zum Auswählen einzelner Hamann-Dateiversionen ein oder aus |
|SyntaxCheck               |Schaltet den automatsichen erweiterten Syntax-Check ein oder aus                |
|Notifications             |Schaltet Benachrichtigungen über den Stand der XML Dateien und den Browser-Refresh ein oder aus                |

```
"FileSizeLimit": 52428800
```
Dateigrößen-Limit für XML=Dateien

```
"AvailableStartYear": 1700,
"AvailableEndYear": 1800,
```
Verfügbare Jahre auf der Webseite. Trotzdem wird bei der syntaktischen Überprüfung die gesamte Datei geprüft.

```
"LettersOnPage": 80
```
Anzahl der Briefe, die bei Inhaltsverzeichnis bzw. Trefferanzige auf einer Seite mindestens gezeigt werden.
