# Entwicklung

Der Kurs ist ein [LiaScript](https://liascript.github.io)-Kurs. Der gesamte
Kurstext steht in `README.md`, die Grafiken liegen als SVG in `img/`.

## Kurs lokal ansehen

```bash
./serve.sh -l
```

Danach im Browser öffnen:
<http://localhost:3000/liascript/index.html?http://localhost:3000/README.md>

`-l` lädt die Vorschau neu, sobald sich `README.md` ändert.

**Wichtig:** LiaScript speichert Kurse im Browser zwischen und lädt sie erst
neu, wenn sich im Kurskopf die `version` ändert. Nach jeder Änderung daher
die Versionsnummer erhöhen.

## SCORM-Paket erzeugen

```bash
./export-scorm.sh              # SCORM 1.2
./export-scorm.sh -f scorm2004 # SCORM 2004
./export-scorm.sh -m 60        # bestanden ab 60 % der Quizpunkte
```

Das Paket landet in `export/` (nicht im Repository). Das Skript repariert das
vom LiaScript-Exporter erzeugte Paket mit `tools/patch_scorm.py`:

- **Startpunkt:** Der Exporter trägt nur `index.html` als Startseite ein.
  LiaScript braucht aber die Adresse der Kursdatei als Parameter, sonst
  erscheint die leere LiaScript-Startseite.
- **Bilder:** Die Kursadresse muss absolut sein. Bei nur `?README.md` sucht
  LiaScript die Bilder im Wurzelverzeichnis des Servers, in einem LMS wie
  ILIAS liegt das Paket aber in einem Unterordner.
- **Stylesheets:** Im SCORM-Build bindet LiaScript die `link:`-Stylesheets
  aus dem Kurskopf nicht ein. Das Skript trägt sie direkt in `index.html` ein.

**Hinweis zu ILIAS:** ILIAS liefert Lernmodul-Dateien mit einer Gültigkeit
von 5 Tagen aus. Wer ein Modul schon geöffnet hat, sieht ausgetauschte
Dateien unter Umständen erst nach Ablauf dieser Frist.

## Grafiken neu erzeugen

Drei Grafiken werden per Skript erzeugt:

```bash
python3 tools/make_ki_svgs.py img   # Transformer und Diffusion (3.4)
python3 tools/make_web_svg.py img   # Aufruf einer Webseite (4.5)
```

Die übrigen SVGs sind von Hand gezeichnete Nachbauten der Abbildungen aus
der Vorlage.

## Externe Abhängigkeiten zur Laufzeit

- Python in den Code-Beispielen: [Pyodide](https://pyodide.org) über das
  LiaScript-Template `LiaTemplates/Pyodide` (Version 0.3.5) und
  `cdn.jsdelivr.net`
- Live-DNS-Abfrage in 4.5: `dns.google`

Ohne Internetzugang funktionieren die Code-Beispiele nicht, der restliche
Kurs schon.
