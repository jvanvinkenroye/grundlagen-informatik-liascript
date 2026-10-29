"""Erzeugt die Ablaufgrafik "Aufruf einer Webseite" für Kapitel 4.5."""

import sys
from pathlib import Path

ROT = "#147375"
ORANGE = "#2A9D8F"
VIOLETT = "#264653"
GRAU = "#666"
FONT = 'font-family="Arial, Helvetica, sans-serif"'

# x-Positionen der drei Beteiligten (Lebenslinien)
BROWSER, DNS, SERVER = 150, 420, 660


def pfeil(y: int, von: int, nach: int, text: str, farbe: str, gestrichelt=False) -> str:
    links = von < nach
    x1, x2 = (von + 8, nach - 8) if links else (von - 8, nach + 8)
    spitze = (
        f"{x2},{y} {x2 - 10},{y - 6} {x2 - 10},{y + 6}"
        if links
        else f"{x2},{y} {x2 + 10},{y - 6} {x2 + 10},{y + 6}"
    )
    strich = ' stroke-dasharray="6 4"' if gestrichelt else ""
    mitte = (von + nach) / 2
    return (
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{farbe}" '
        f'stroke-width="2.5"{strich}/>'
        f'<polygon points="{spitze}" fill="{farbe}"/>'
        f'<text x="{mitte:.0f}" y="{y - 8}" text-anchor="middle" font-size="13" '
        f'fill="#1a1a1a" stroke="#fff" stroke-width="5" paint-order="stroke">'
        f"{text}</text>"
    )


def klammer(y1: int, y2: int, text: str, farbe: str) -> str:
    return (
        f'<rect x="12" y="{y1}" width="6" height="{y2 - y1}" fill="{farbe}"/>'
        f'<text x="26" y="{(y1 + y2) / 2 + 5:.0f}" font-size="14" font-weight="bold" '
        f'fill="{farbe}">{text}</text>'
    )


def web_svg() -> str:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 560" {FONT}>',
        '<rect width="760" height="560" fill="#fff"/>',
    ]
    # Köpfe der Beteiligten
    for x, titel, unter in [
        (BROWSER, "Browser", "Laptop in der Beratungsstelle"),
        (DNS, "DNS-Server", "„Telefonbuch“ des Internets"),
        (SERVER, "Webserver", "www.example.org"),
    ]:
        out.append(
            f'<rect x="{x - 75}" y="18" width="150" height="50" rx="6" '
            f'fill="#e8e8e8" stroke="{GRAU}"/>'
        )
        out.append(
            f'<text x="{x}" y="40" text-anchor="middle" font-size="16" '
            f'font-weight="bold" fill="#1a1a1a">{titel}</text>'
        )
        out.append(
            f'<text x="{x}" y="58" text-anchor="middle" font-size="11" '
            f'fill="#444">{unter}</text>'
        )
        out.append(
            f'<line x1="{x}" y1="68" x2="{x}" y2="490" stroke="#b3b3b3" '
            'stroke-width="2" stroke-dasharray="4 4"/>'
        )

    # 1. DNS
    out.append(klammer(95, 165, "DNS", ORANGE))
    out.append(
        pfeil(115, BROWSER, DNS, "① Welche IP-Adresse hat www.example.org?", ORANGE)
    )
    out.append(pfeil(155, DNS, BROWSER, "② 203.0.113.10", ORANGE, gestrichelt=True))

    # 2. TCP
    out.append(klammer(190, 285, "TCP", GRAU))
    out.append(
        pfeil(210, BROWSER, SERVER, "③ Verbindung aufbauen? (an Port 443)", GRAU)
    )
    out.append(pfeil(240, SERVER, BROWSER, "④ Ja, bereit!", GRAU, gestrichelt=True))
    out.append(pfeil(270, BROWSER, SERVER, "⑤ Verbindung steht.", GRAU))

    # 3. TLS
    out.append(klammer(310, 375, "TLS", VIOLETT))
    out.append(
        pfeil(
            330,
            SERVER,
            BROWSER,
            "⑥ Zertifikat: „Ich bin wirklich www.example.org“",
            VIOLETT,
            gestrichelt=True,
        )
    )
    out.append(
        pfeil(365, BROWSER, SERVER, "⑦ Gemeinsamen Schlüssel vereinbaren", VIOLETT)
    )

    # 4. HTTP
    out.append(klammer(400, 480, "HTTP", ROT))
    out.append(pfeil(420, BROWSER, SERVER, "⑧ GET /  – „Bitte die Startseite“", ROT))
    out.append(
        pfeil(460, SERVER, BROWSER, "⑨ 200 OK + HTML-Seite", ROT, gestrichelt=True)
    )

    # Schloss-Symbol für verschlüsselten Bereich
    out.append(f'<rect x="28" y="463" width="14" height="11" rx="2" fill="{VIOLETT}"/>')
    out.append(
        f'<path d="M31,463 v-4 a4,4 0 0 1 8,0 v4" fill="none" '
        f'stroke="{VIOLETT}" stroke-width="2"/>'
    )
    out.append(
        f'<text x="47" y="473" font-size="11" fill="{VIOLETT}">verschlüsselt</text>'
    )

    out.append(
        '<text x="380" y="512" text-anchor="middle" font-size="13" fill="#444">'
        'Alle Nachrichten reisen als <tspan font-weight="bold">IP-Pakete</tspan> '
        "mit Absender- und Empfängeradresse durchs Internet.</text>"
    )
    out.append(
        '<text x="380" y="532" text-anchor="middle" font-size="12" fill="#666">'
        "Vereinfachte Darstellung; Beispiel-IP-Adresse</text>"
    )
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    Path(sys.argv[1], "web-aufruf.svg").write_text(web_svg(), encoding="utf-8")
