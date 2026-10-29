#!/usr/bin/env bash
# Startet den LiaScript-Devserver für diesen Kurs.
#
# Workaround: @liascript/devserver sucht die LiaScript-Oberfläche unter
# <devserver>/node_modules/@liascript/editor, npx installiert sie aber eine
# Ebene höher. Ohne --node_modules liefert der Server daher
# "index.html not found or could not be read".
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly script_dir

usage() {
    echo "Verwendung: $(basename "$0") [-p port] [-l]"
    echo "  -p port   Port (Standard: 3000)"
    echo "  -l        Live-Reload bei Änderungen"
}

port=3000
live=""
while getopts "p:lh" opt; do
    case "$opt" in
        p) port="$OPTARG" ;;
        l) live="--live" ;;
        h) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
done

find_npx_root() {
    local devserver
    devserver="$(find "${HOME}/.npm/_npx" -maxdepth 4 -type d \
        -path '*/node_modules/@liascript/devserver' 2>/dev/null | head -n 1)"
    [[ -n "$devserver" ]] && dirname "$(dirname "$(dirname "$devserver")")"
}

npx_root="$(find_npx_root || true)"
if [[ -z "$npx_root" ]]; then
    # Erster Lauf: Paket in den npx-Cache laden
    npx -y @liascript/devserver --help > /dev/null
    npx_root="$(find_npx_root)"
fi

echo "Kurs: http://localhost:${port}/liascript/index.html?http://localhost:${port}/README.md"
cd "$script_dir"
exec node "${npx_root}/node_modules/@liascript/devserver/dist/index.js" \
    --input README.md --port "$port" --node_modules "$npx_root" $live
