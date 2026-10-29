"""Repariert ein LiaScript-SCORM-Paket für den Einsatz in ILIAS.

1. Startpunkt: Der LiaScript-Exporter trägt im SCORM-Manifest nur
   "index.html" als Startseite ein. Ohne den Zusatz "?README.md" zeigt
   LiaScript seine leere Startseite statt des Kurses, und genau so startet
   ILIAS das Paket. Eine Weiterleitung in index.html ergänzt die Angabe.
2. Stylesheets: Im SCORM-Build lädt LiaScript die per "link:" im Kurskopf
   angegebenen CSS-Dateien zwar herunter, bindet sie aber nicht ein. Sie
   werden daher aus dem Kurskopf gelesen und direkt in index.html
   eingetragen. Ohne "link:"-Zeilen wird nichts eingetragen.

Das Skript lässt sich mehrfach auf dasselbe Paket anwenden.

Aufruf: python3 patch_scorm.py paket.zip
"""

import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

START = "<!-- lia-ilias-fix:start -->"
ENDE = "<!-- lia-ilias-fix:end -->"
# Vorgängerfassungen dieses Skripts, die vor dem Neueintrag entfernt werden
ALTE_FIXES = re.compile(
    r"<!-- lia-scorm-start-fix(?:-v2)? --><script>.*?</script>", re.DOTALL
)

# LiaScript liest den gesamten Query-String als Kursadresse. Hängt ILIAS
# eigene Parameter an, wäre die Adresse kaputt; daher alles andere ersetzen.
# Die Adresse muss absolut sein: Bei nur "?README.md" löst LiaScript Bilder
# gegen das Wurzelverzeichnis des Servers auf ("/img/..."), und in ILIAS, wo
# das Paket unter /data/.../lm_data/lm_<id>/ liegt, fehlen dann alle Bilder.
WEITERLEITUNG = (
    "<script>(function(){"
    "var u=location.href.split(/[?#]/)[0].replace(/[^/]*$/,'')+'README.md';"
    "if(location.search!=='?'+u){"
    "location.replace(location.pathname+'?'+u+location.hash)}})()</script>"
)

LINK_ZEILE = re.compile(r"^link:\s*(\S+)\s*$", re.MULTILINE)


def stylesheets_aus_kurskopf(readme: str) -> list[str]:
    kopf = readme.split("-->", 1)[0]
    return LINK_ZEILE.findall(kopf)


def entferne_alte_fixes(html: str) -> str:
    html = ALTE_FIXES.sub("", html)
    return re.sub(re.escape(START) + ".*?" + re.escape(ENDE), "", html, flags=re.DOTALL)


def patch_html(html: str, stylesheets: list[str]) -> str:
    html = entferne_alte_fixes(html)
    # Die Weiterleitung muss vor allen Skripten stehen, damit LiaScript gar
    # nicht erst mit leerer Adresse startet.
    html = html.replace("<head>", f"<head>{START}{WEITERLEITUNG}{ENDE}", 1)
    # Die Stylesheets kommen ans Ende des <head>, damit sie die
    # LiaScript-Styles überschreiben.
    if not stylesheets:
        return html
    links = "".join(f'<link rel="stylesheet" href="{href}">' for href in stylesheets)
    return html.replace("</head>", f"{START}{links}{ENDE}</head>", 1)


def patch(paket: Path) -> None:
    with zipfile.ZipFile(paket) as zin:
        namen = zin.namelist()
        stylesheets = stylesheets_aus_kurskopf(zin.read("README.md").decode("utf-8"))
        fehlend = [h for h in stylesheets if "://" not in h and h not in namen]
        if fehlend:
            raise SystemExit(f"Im Paket fehlen: {', '.join(fehlend)}")
        html = patch_html(zin.read("index.html").decode("utf-8"), stylesheets)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp_pfad = Path(tmp.name)
        with zipfile.ZipFile(tmp_pfad, "w", zipfile.ZIP_DEFLATED) as zout:
            for eintrag in zin.infolist():
                daten = (
                    html.encode("utf-8")
                    if eintrag.filename == "index.html"
                    else zin.read(eintrag.filename)
                )
                zout.writestr(eintrag, daten)
    # Die temporäre Datei hat nur Rechte 600; die des Originals übernehmen
    shutil.copymode(paket, tmp_pfad)
    shutil.move(tmp_pfad, paket)


if __name__ == "__main__":
    ziel = Path(sys.argv[1])
    patch(ziel)
    print(f"{ziel.name}: für ILIAS repariert")
