#!/usr/bin/env bash
# Exportiert den Kurs als SCORM-Paket, z. B. für ILIAS oder Moodle.
#
# ILIAS kann SCORM 1.2 und SCORM 2004 importieren. SCORM 1.2 ist der
# Standard, weil es in ILIAS am zuverlässigsten funktioniert.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly script_dir

usage() {
    echo "Verwendung: $(basename "$0") [-f format] [-m punkte] [-o organisation] [-i]"
    echo "  -f format        scorm1.2 (Standard) oder scorm2004"
    echo "  -m punkte        Bestehensgrenze in Prozent der Quizpunkte (Standard: 0)"
    echo "  -o organisation  Name der Organisation im Paket (Standard: LiaScript)"
    echo "  -i               Startseite des Exporters mit iframe (--scorm-iframe)"
    echo "                   statt Nachbearbeitung mit tools/patch_scorm.py"
}

format="scorm1.2"
mastery=0
organisation="LiaScript"
iframe=false
while getopts "f:m:o:ih" opt; do
    case "$opt" in
        f) format="$OPTARG" ;;
        m) mastery="$OPTARG" ;;
        o) organisation="$OPTARG" ;;
        i) iframe=true ;;
        h) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
done

case "$format" in
    scorm1.2|scorm2004) ;;
    *) echo "Unbekanntes Format: $format" >&2; usage; exit 1 ;;
esac

# Eigener Dateiname für die iframe-Variante, damit sich beide Pakete in
# ILIAS nebeneinander vergleichen lassen
variante=""
extra_args=()
if [[ "$iframe" == true ]]; then
    variante="-iframe"
    extra_args+=(--scorm-iframe)
fi
readonly ausgabe="${script_dir}/export/grundlagen-informatik-${format}${variante}"

# Der Exporter packt den ganzen Ordner ins Paket. Deshalb nur Kurstext und
# Bilder in einen sauberen Bauordner kopieren, ohne Werkzeuge, Doku und
# versteckte Dateien.
readonly bau_dir="${script_dir}/export/.bau"
rm -rf "$bau_dir"
mkdir -p "$bau_dir"
cp "${script_dir}/README.md" "$bau_dir/"
rsync -a --exclude '.*' "${script_dir}/img" "$bau_dir/"
# Eigene Stylesheets aus "link:"-Zeilen im Kurskopf mitnehmen
for css in "${script_dir}"/*.css; do
    [[ -e "$css" ]] && cp "$css" "$bau_dir/"
done

echo "Exportiere als ${format}${variante} ..."
cd "$bau_dir"
npx -y @liascript/exporter \
    --input README.md \
    --format "$format" \
    --output "$ausgabe" \
    --scorm-organization "$organisation" \
    --scorm-masteryScore "$mastery" \
    ${extra_args[@]+"${extra_args[@]}"}

rm -rf "$bau_dir"

if [[ ! -f "${ausgabe}.zip" ]]; then
    echo "Fehler: ${ausgabe}.zip wurde nicht erzeugt." >&2
    exit 1
fi

# Ohne diese Nachbearbeitung zeigt ILIAS nur die leere LiaScript-Startseite
# und findet keine Bilder (Details in tools/patch_scorm.py). Die
# iframe-Variante setzt die Kursadresse in start.html selbst; die Weiterleitung
# des Patches würde sie dort nur durch eine andere Schreibweise ersetzen.
if [[ "$iframe" == false ]]; then
    python3 -I "${script_dir}/tools/patch_scorm.py" "${ausgabe}.zip"
elif grep -q '^link:' "${script_dir}/README.md"; then
    echo "Hinweis: Mit -i werden die link:-Stylesheets nicht eingebunden." >&2
fi

echo
echo "Fertig: ${ausgabe}.zip"
