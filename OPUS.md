# Kurzbeschriebung Opus

## Dateien
| Dateiname                | XML-Pfad(e)                                 | Zweck                                         |
| :----------------------- | :------------------------------------------ | :-------------------------------------------- |
| `Bibel-Kommentar.xml`    | `opus/kommentare/kommcat[@value='bibel']`   | Bibelstellenregister                          |
| `briefe.xml`             | `opus/document/`                            | Brieftexte                                    |
| `edits.xml`              | `opus/edits`                                | Texteingriffe                                 |
| `Maginal-Kommentar.xml`  | `opus/marginalien`                          | Stellenkommentar                              |
| `meta.xml`               | `opus/descriptions`                         | Brief-Metadaten                               |
| `references.xml`         | `opus/definitions`                          | Personen-, Orts- und Kategorien(?)verzeichnis |
| `Register-Kommentar.xml` | `opus/kommentare/kommcat[@value='neuzeit']` | Personen- und Sachregister                    |
| `traditions.xml`         | `opus/traditions`                           | Textprovinienz und -zusätze                   |

| `forschung.xml`          | `opus/kommentare/kommcat[@value='forschung']` <br> `opus/kommentare/kommcat[@value='editionen']` <br> `opus/kommentare/kommcat[@value='nachschlagewerke']` | Sekundärliteratur      

## Dateistruktur
Alle Dateien müssen mit dem XML-Prolog
`<?xml version="1.0" encoding="utf-8"?>`
beginnen. Weiter erkennt man Dateien, die zum Hamann-Projekt gehören, am ersten Tag, auch "Root" genannt: 

```xml
<opus>          Root-Element für ein Hamann-Dokument
<data>          (nicht mehr benötigt) Zweites Element
```

## Datei-spezifische Tags
Manche XML-Tags ergeben nur Sinn in besonderen Kontexten. Die Tags `kommentare`, `document`, `edits`, `marginalien`, `definitions`, `descriptions` und `traditions` kennzeichnen die Kategorien Registerkommentare, Briefe, Texteingriffe, Marginalien, Verzeichnisse, Metadaten, und Daten zur Überlieferung. 

`kommentare`
```
opus/kommentare/kommcat                                     Kategorie von Registereinträgen
opus/kommentare/kommcat[@value]                             Identifiziert die Kategorie der Registereinträge eindeutig (Text)
opus/kommentare/kommcat[@sorting]                           Gibt die Reihenfolge der Kategorie in der Anzeige an (Nummer)
opus/kommentare/kommcat/kommentar                           Registereintrag
opus/kommentare/kommcat/kommentar[@id]                      Identifiziert den Registereitrag (Text)
opus/kommentare/kommcat/kommentar[@type]                    Gibt die Kategorie eines Registereintrags an (Text)
opus/kommentare/kommcat/kommentar/lemma
opus/kommentare/kommcat/kommentar/subsection/lemma          Lemma eines Register(unter)eintrags
opus/kommentare/kommcat/kommentar/lemma/titel
opus/kommentare/kommcat/kommentar/subsection/lemma/titel    Titel eines Werkes
opus/data/kommentare/kommcat/kommentar/eintrag  
opus/data/kommentare/kommcat/kommentar/subsection/eintrag   Register(unter)eintrag
```
- link 
- wwwlink
`descriptions`
```
opus/descriptions/letterDesc                                                Metadaten eines Briefes
opus/descriptions/letterDesc[@letter]                                       Identifiziert eine Brief eindeutig (Text)
opus/descriptions/letterDesc/date                                           Datum eines Briefes
opus/descriptions/letterDesc/date[@value]                                   Menschenlesbares Entstehungsdatum eines Briefes (Text)
opus/descriptions/letterDesc/sort                                           Maschinenlesbares Entstehungsdatum eines Briefes
opus/descriptions/letterDesc/sort[@value]                                   Maschinenlesbares Entstehungsdatum eines Briefes (ISO 8601 Datum)
opus/descriptions/letterDesc/sort[@notBefore]                               Datierung eines Briefes nach einem Datum (ISO 8601 Datum)
opus/descriptions/letterDesc/sort[@notAfter]                                Datierung eines Briefes vor einem Datum (ISO 8601 Datum)
opus/descriptions/letterDesc/sort[@from]                                    Beginn des Entstehungsdatums eines Briefes (ISO 8601 Datum)
opus/descriptions/letterDesc/sort[@to]                                      Ende des Entstehungsdatums eines Briefes (ISO 8601 Datum)
opus/descriptions/letterDesc/sort[@cert]                                    Angabe über die Zuverlässigkeit der Datierung low | high (Default)
opus/descriptions/letterDesc/location                                       Entstehungsort eines Briefes, wie er aus dem Text hervorgeht
opus/descriptions/letterDesc/location[@ref]                                 Verweis auf opus/definitions/locationDefs/locationDef[@index]
opus/descriptions/letterDesc/senders                                        Liste der Absender eines Briefes
opus/descriptions/letterDesc/senders/sender                                 Absender eines Briefes
opus/descriptions/letterDesc/senders/sender[@ref]                           Verweis auf opus/definitions/personDefs/personDef[@index]
opus/descriptions/letterDesc/receivers                                      Liste der Empfänger eines Briefes
opus/descriptions/letterDesc/receivers/receiver                             Empfänger eines Briefes
opus/descriptions/letterDesc/receivers/receiver[@ref]                       Verweis auf opus/definitions/personDefs/personDef[@index]
opus/descriptions/letterDesc/hasOriginal                                    Überlieferungsquelle: Original?
opus/descriptions/letterDesc/hasOriginal[@value]                            Überlieferungsquelle: Original true | false
opus/descriptions/letterDesc/isProofread                                    (abgekündigt) Status der kritischen Edition
opus/descriptions/letterDesc/isProofread[@value]                            (abgekündigt) Status der kritischen Edition true | false
opus/descriptions/letterDesc/isDraft                                        Status des Briefs: wurde der Brief abgeschickt?
opus/descriptions/letterDesc/isDraft[@value]                                Status des Briefs: Entwurf true | false
opus/descriptions/letterDesc/ZHInfo                                         Informationen zur Voredition von ZH
opus/descriptions/letterDesc/ZHInfo[@inZH]                                  Ob der Brief in ZH ediert wurde true | false
opus/descriptions/letterDesc/ZHInfo/dateChanged                             Ob sich die Datierung gegenüber der Edition ZH geändert hat
opus/descriptions/letterDesc/ZHInfo/dateChanged[@value]                     Ob sich die Datierung gegenüber der Edition ZH geändert hat true | false
opus/descriptions/letterDesc/ZHInfo/begin                                   Position des Briefs in ZH
opus/descriptions/letterDesc/ZHInfo/begin[@vol]                             Position des Briefes in ZH - Band (Nummer)
opus/descriptions/letterDesc/ZHInfo/begin[@page]                            Position des Briefes in ZH - Seite (Text)
opus/data/descriptions/letterDesc/ZHInfo/alternativeLineNumbering           Änderung der Zeilennummerierung gegnüber ZH
opus/data/descriptions/letterDesc/ZHInfo/alternativeLineNumbering[@value]   Änderung der Zeilennummerierung gegnüber ZH true | false
```