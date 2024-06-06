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
| `forschung.xml`          | `opus/kommentare/kommcat[@value='forschung']` <br> `opus/kommentare/kommcat[@value='editionen']` <br> `opus/kommentare/kommcat[@value='nachschlagewerke']` | Sekundärliteratur |

## Dateistruktur
Alle Dateien müssen mit dem XML-Prolog
`<?xml version="1.0" encoding="utf-8"?>`
beginnen. Weiter erkennt man Dateien, die zum Hamann-Projekt gehören, am ersten Tag, auch "Root" genannt: 

```xml
<opus>          Root-Element für ein Hamann-Dokument
<data>          (nicht mehr benötigt) Zweites Element
```

## Datei-spezifische Tags & Attribute
Die Tags `kommentare`, `document`, `edits`, `marginalien`, `definitions`, `descriptions` und `traditions` kennzeichnen die Kategorien Registerkommentare, Briefe, Texteingriffe, Marginalien, Verzeichnisse, Metadaten, und Daten zur Überlieferung. Hier sind Tags und Attribute dokumentiert, die aussschließlich als Kind-Elemente eines dieser Tags vorkommen und Sinn ergeben (`kommcat` kommt nur als Kind von `kommentare` infrage, `isProofread` nur in `descriptions` usw.).

### `kommentare`
```
opus/kommentare/kommcat                                     Registereinträge
opus/kommentare/kommcat[@value]                             Identifiziert die Kategorie der Registereinträge eindeutig (Text)
opus/kommentare/kommcat[@sorting]                           Gibt die Reihenfolge der Kategorie in der Anzeige an (Nummer)
opus/kommentare/kommcat/kommentar                           Registereintrag
opus/kommentare/kommcat/kommentar[@id]                      Identifiziert den Registereitrag (Text). Wird zur Sortierung verwendet!
opus/kommentare/kommcat/kommentar[@type]                    Gibt die Kategorie eines Registereintrags an (Text)
opus/kommentare/kommcat/kommentar/lemma
opus/kommentare/kommcat/kommentar/subsection/lemma          Lemma eines Register(unter)eintrags
opus/kommentare/kommcat/kommentar/lemma/titel
opus/kommentare/kommcat/kommentar/subsection/lemma/titel    Titel eines Werkes
opus/kommentare/kommcat/kommentar/eintrag  
opus/kommentare/kommcat/kommentar/subsection/eintrag        Register(unter)eintrag
```
- link 
- wwwlink

### `descriptions`
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
opus/descriptions/letterDesc/ZHInfo/alternativeLineNumbering                Änderung der Zeilennummerierung gegnüber ZH
opus/descriptions/letterDesc/ZHInfo/alternativeLineNumbering[@value]        Änderung der Zeilennummerierung gegnüber ZH true | false
```

### `definitions`
```
opus/definitions/structureDefs/*                                            Abgekündigt
opus/definitions/sourceDefs/*                                               Abgekündigt
opus/definitions/locationDefs/                                              Ortsverzeichnis
opus/definitions/locationDefs/locationDef                                   Ortsverzeichniseintrag
opus/definitions/locationDefs/locationDef[@index]                           Identifiziert einen Ortsverzeichniseintrag eindeutig (Zahl)
opus/definitions/locationDefs/locationDef[@name]                            Name des Ortes (jeder physische Ort kommt einmal vor)
opus/definitions/locationDefs/locationDef[@ref]                             GeoNames-URL (optional)
opus/definitions/personDefs/                                                Personenverzeichnis
opus/definitions/personDefs/personDef                                       Personenverzeichniseintrag
opus/definitions/personDefs/personDef[@index]                               Identifiziert einen Personenverzeichniseintrag eindeutig (Zahl)
opus/definitions/personDefs/personDef[@name]                                Name der Person (jede Person kommt einmal vor)
opus/definitions/personDefs/personDef[@vorname]                             Vorname der Person (unbenutzt)
opus/definitions/personDefs/personDef[@nachname]                            Nachname der Person (zur Sortierung, Pflichtfeld)
opus/definitions/personDefs/personDef[@ref]                                 GND-URL (optional)
opus/definitions/personDefs/personDef[@komm]                                ID des Registereintrags der Person (optional)
opus/definitions/handDefs/                                                  Dokumentation von Briefautorinnen (bald: abgekündigt)
opus/definitions/handDefs/handDef                                           Briefautor:in
opus/definitions/handDefs/handDef[@index]                                   Identifiziert eine:n Briefautor:in eindeutig (Zahl)
opus/definitions/handDefs/handDef[@name]                                    Personenname
opus/definitions/appDefs/                                                   Liste von Apperaten, in tradition.xml referenziert
opus/definitions/appDefs/appDef                                             Apparat
opus/definitions/appDefs/appDef[@index]                                     Identifiziert einen Apparat eindeutig (Zahl)
opus/definitions/appDefs/appDef[@name]                                      Name des Apparats
opus/definitions/appDefs/appDef[@category]                                  Kategorie des Apparats zur Gruppierung
```

### `edits`
```
opus/edits/                                                                 Verzeichnis von Texteingriffen (haupsächlich Korrekturen ggü. ZH)
opus/edits/editreason                                                       Texteingriff, Editorischer Kommentar zu einer Textstelle
opus/edits/editreason[@id]                                                  Identifiziert den Texteingriff eindeutig (Nummer)
opus/edits/editreason/zh                                                    Textstelle, wie sie in ZH steht
```


### `traditions`
```
opus/traditions/                                                            Verzeichnis von Textprovinienzen, -zusätzen & -apparaten
opus/traditions/letterTradition                                             Textprovinienz, -zusatz oder -apparat
opus/traditions/letterTradition[@letter]                                    Verweis auf den zugehörigen Brief (Text)
opus/traditions/letterTradition/app                                         Apparat
opus/traditions/letterTradition/app[@ref]                                   Verweis auf opus/definitions/appDefs/appDef[@index]
opus/traditions/letterTradition/app/ZHText                                  Zusätzliches, zeilengenaues Textmaterial
opus/traditions/letterTradition/app/ZHText/edit                             Texteingriff, Verweis auf opus/edits/editreason[@id]
opus/traditions/letterTradition/app/text                                    Textmaterial, nicht zeilengenau (Übersetzungen etc.)
```

### `marginalien`
```
opus/marginalien/                                                           Verzeichnis von Marginalien
opus/marginalien/marginal                                                   Marginalie
opus/marginalien/marginal[@letter]                                          Verweis auf den zugehörigen Brief (Text)
opus/marginalien/marginal[@page]                                            Verweis auf die zugehörige Seite (Text)
opus/marginalien/marginal[@line]                                            Verweis auf die zugehörige Zeile (Text)
opus/marginalien/marginal[@sort]                                            Gibt die Reihenfolge der Marginalie in der Anzeige an (Nummer)
opus/marginalien/marginal/bzg                                               Lemma der Marginalie
```

### `document`
```
opus/document/                                                              Verzeichnis von Brieftexten
opus/document/letterText/                                                   Brieftext
opus/document/letterText[@letter]                                           Verweis auf den zughörigen Brief (Text)
opus/document/letterText/edit                                               Texteingriff
opus/document/letterText/edit[@ref]                                         Verweis auf opus/edits/editreason[@id]
```

## Tags und Attribute zur Textformatierung und Links 
Die folgenden Tags und Attribute sind in allen Dateien erlaubt und dienen der Textformatierung und der Verlinkung von Textstellen. Sie können in verschiedenen Kontexten vorkommen:
```
opus/document/letterText/
opus/edits/editreason/
opus/marginalien/marginal/
opus/traditions/letterTradition/app/
opus/kommentare/kommcat/kommentar/
```

Außer den leeren Elementen insb. `line` und `page` können alle Tags beliebig verschachtelt werden. Die Reihenfolge der Tags ist nicht relevant.

Textformatierung:
```
added                   Editorischer Texteingriff, hinzugefügt [Text]
align                   Textausrichtung
align[@value]           Textausrichtung left | right | center
anchor                  Fußnotenanker
anchor[@ref]            Verweis auf die fn[@index] der Fußnote
aq                      Text in lateinischen Buchstaben
del                     Gestrichener Text
dul                     Doppelt unterstrichener Text
fn                      Fußnote
fn[@index]              Identifiziert die Fußnote eindeutig (Nummer)
ful                     Linie im Text (Tabellenkontext)
gr                      Text in griechischen Buchstaben
hand                    Text fremder Hand
hand[@ref]              Verweis auf opus/definitions/handDefs/handDef[@index]
hb                      Text in hebräischen Buchstaben
insertion               Von Hamann nachträglich eingefügt (transkribierte Originale)
note                    Anmerkung der Editor:innen
nr                      Unentziffert
sub                     Tiefgestellter Text
super                   Hochgestellter Text
tabs                    Tabellenkontext
tabs/tab                Tabellenzelle
tabs/tab[@value]        Position der Zelle in der Zeile als Bruch (z.B. 1-3 = 1/3, die Zelle beginnt also bei 1/3 der Zeilenbreite)
                        0-3 1-3 2-3 wären also drei gleich weite Zellen in einer Zeile, jeweils ein Drittel der Zeile weit.
                        0-6 3-6 5-6 wären drei Zellen, die 1/2, 1/4 und 1/6 der Zeilenbreite einnehmen.
tul                     Dreifach unterstrichener Text
ul                      Unterstrichener Text
```

Semantische Auszeichnungen (zzt. Unbenutzt, dennoch getaggt, ausser `sal`):
```
sal                     Briefanrede
address                 Adresszeile
datum                   Datum
ps                      Postskriptum
sig                     Unterschrift
```

Seiten- und Zeilengrenzen:
```
page                    Zeilengrenze
page[@index]            Seitenangabe. Bezieht sich auf Seiten in ZH, oder Seiten im Manuskript, je nach Kontext
page[@autopsic]         Abgekündigt
line                    Zeilengrenze
line[@index]            Zeilenangabe. Bezieht sich auf Zeilen in ZH, oder Zeilen im Manuskript, je nach Kontext
                        Fehlt index, wird die Zeile nicht gezählt (etwa bei Zeilen @type="empty")
line[@autopsic]         Abgekündigt
line[@tab]              Einzug der Zeile:
                        1 = Absatzeinzug
                        2 = Weiter Einzug für Briefanreden
                        3 = Weiter Einzug für Briefanreden
                        4 = Weiter Einzug für Briefanreden, eingerückte Verse & Gedichte
                        5 = Weiter Einzug für extra eingerückte Verse
                        6 = Strophenüberschriften & Sprecherrollen bei Gedichten
                        7 = Rechts eingerückte Autorangabe meist unter Gedichten
line[@type]             Zeilentyp:
                        empty = Leerzeile
                        break = Erzwungener, semantisch relevanter Zeilenumbruch, der nicht durch tab deutlich wird
                        line  = Horizontale Linie
```

Mit folgenden Tags wird innerhalb der Datei verlinkt:
```
link                    Verweis auf einen Registereintrag
link[@ref]              Verweis auf opus/kommentare/kommcat/kommentar[@id]
link[@subref]           Verweis auf opus/kommentare/kommcat/kommentar/subsection/eintrag[@id]
link[@linktext]         Bei leerem Element oder linktext = true wird der Linktext automatisch aus dem Eintrtag generiert
wwwlink                 Verweis auf eine externe URL
wwwlink[@address]       URL
intlink                 Verweis auf eine Briefstelle
intlink[@letter]        Verweis auf opus/document/letterText[@letter]
intlink[@page]          Verweis auf die zugehörige Seite
intlink[@line]          Verweis auf die zugehörige Zeile
intlink[@linktext]      Bei leerem Element oder linktext = true wird der Linktext automatisch generiert
```

Links sind erlaubt in
```
opus/marginalien/marginal/*
opus/traditions/letterTradition/app/*
opus/kommentare/kommcat/kommentar/*
opus/edit/editreason/*
```
