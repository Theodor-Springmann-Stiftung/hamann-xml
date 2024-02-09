# Kurzbeschriebung Opus

## Dateien
| Dateiname                | XML-Pfad(e)                                                                                                                                                  | Zweck                                         |
| :----------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------- |
| `Bibel-Kommentar.xml`    | `opus/kommentare/kommcat[@value='bibel']`                                                                                                                    | Bibelstellenregister                          |
| `briefe.xml`             | `opus/document/`                                                                                                                                             | Brieftexte                                    |
| `edits.xml`              | `opus/edits`                                                                                                                                                 | Texteingriffe                                 |
| `forschung.xml`          | `opus/kommentare/kommcat[@value='forschung']` <br/> `opus/kommentare/kommcat[@value='editionen']` <br/> `opus/kommentare/kommcat[@value='nachschlagewerke']` | Sekundärliteratur                             |
| `Maginal-Kommentar.xml`  | `opus/marginalien`                                                                                                                                           | Stellenkommentar                              |
| `meta.xml`               | `opus/descriptions`                                                                                                                                          | Brief-Metadaten                               |
| `references.xml`         | `opus/definitions`                                                                                                                                           | Personen-, Orts- und Kategorien(?)verzeichnis |
| `Register-Kommentar.xml` | `opus/kommentare/kommcat[@value='neuzeit']`                                                                                                                  | Personen- und Sachregister                    |
| `traditions.xml`         | `opus/traditions`                                                                                                                                            | Textprovinienz und -zusätze

## Dateistruktur
Alle Dateien müssen mit dem XML-Prolog
`<?xml version="1.0" encoding="utf-8"?>`
beginnen. Weiter erkennt man Dateien, die zum Hamann-Projekt gehören oder der spezisfischen Syntax folgen, am ersten Tag, auch "Root" genannt: 

```xml
<opus>          Root-Element für ein Hamann-Dokument
<data>          (nicht mehr benötigt) Zweites Element
```

## Datei-spezifische Tags
Manche XML-Tags ergeben nur Sinn in besonderen Kontexten.

