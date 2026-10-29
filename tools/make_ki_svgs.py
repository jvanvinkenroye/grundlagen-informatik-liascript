"""Erzeugt die Erklärgrafiken zu Transformer und Diffusionsmodell für Kapitel 3.4."""

import random
import sys
from pathlib import Path

ROT = "#147375"
ORANGE = "#2A9D8F"
VIOLETT = "#264653"
FONT = 'font-family="Arial, Helvetica, sans-serif"'


def transformer_svg() -> str:
    woerter = ["Die", "Klientin", "holt", "den", "Bescheid", "ab,", "weil", "sie"]
    # Beispielwerte zur Veranschaulichung, keine Messwerte eines echten Modells
    gewichte = {
        "Klientin": 0.62,
        "Bescheid": 0.18,
        "holt": 0.08,
        "Die": 0.04,
        "den": 0.03,
        "ab,": 0.02,
        "weil": 0.03,
    }
    breiten = [len(w) * 11 + 24 for w in woerter]
    x, pos = 30, []
    for b in breiten:
        pos.append((x, b))
        x += b + 10
    y_box = 170
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 485" {FONT}>',
        '<rect width="760" height="485" fill="#fff"/>',
        (
            '<text x="30" y="34" font-size="19" font-weight="bold" fill="#1a1a1a">'
            "1. Aufmerksamkeit: Worauf bezieht sich „sie“?</text>"
        ),
    ]
    sie_x = pos[-1][0] + pos[-1][1] / 2
    for (bx, bw), w in zip(pos[:-1], woerter[:-1]):
        g = gewichte[w]
        cx = bx + bw / 2
        hoehe = 20 + (sie_x - cx) * 0.14
        farbe = ROT if g >= 0.15 else "#999"
        out.append(
            f'<path d="M{sie_x:.0f},{y_box} C{sie_x:.0f},{y_box - hoehe:.0f} '
            f'{cx:.0f},{y_box - hoehe:.0f} {cx:.0f},{y_box}" fill="none" '
            f'stroke="{farbe}" stroke-width="{1 + g * 14:.1f}" '
            f'stroke-opacity="0.85"/>'
        )
        out.append(
            f'<text x="{cx:.0f}" y="{y_box + 58}" text-anchor="middle" '
            f'font-size="13" fill="{farbe}" font-weight="bold">{g:.0%}</text>'
        )
    for (bx, bw), w in zip(pos, woerter):
        aktiv = w == "sie"
        out.append(
            f'<rect x="{bx}" y="{y_box}" width="{bw}" height="34" rx="4" '
            f'fill="{ROT if aktiv else "#e8e8e8"}"/>'
        )
        out.append(
            f'<text x="{bx + bw / 2:.0f}" y="{y_box + 23}" text-anchor="middle" '
            f'font-size="17" fill="{"#fff" if aktiv else "#1a1a1a"}">{w}</text>'
        )
    out.append(
        f'<text x="30" y="{y_box + 84}" font-size="13" fill="#666">'
        "Linienstärke = wie stark das Modell ein Wort beachtet (Beispielwerte)</text>"
    )

    # Teil 2: Vorhersage des nächsten Wortes
    y2 = 305
    out.append(
        f'<text x="30" y="{y2}" font-size="19" font-weight="bold" fill="#1a1a1a">'
        "2. Vorhersage: Welches Wort kommt als Nächstes?</text>"
    )
    out.append(
        f'<text x="30" y="{y2 + 30}" font-size="15" fill="#333">'
        "„Die Klientin holt den Bescheid ab, weil sie …“</text>"
    )
    kandidaten = [
        ("ihn", 0.46),
        ("ihren", 0.21),
        ("einen", 0.14),
        ("den", 0.09),
        ("es", 0.05),
    ]
    for i, (w, p) in enumerate(kandidaten):
        yy = y2 + 50 + i * 26
        out.append(
            f'<text x="100" y="{yy + 15}" text-anchor="end" font-size="15" '
            f'fill="#1a1a1a">{w}</text>'
        )
        out.append(
            f'<rect x="110" y="{yy}" width="{p * 900:.0f}" height="19" '
            f'fill="{ROT if i == 0 else "#b3b3b3"}"/>'
        )
        out.append(
            f'<text x="{118 + p * 900:.0f}" y="{yy + 15}" font-size="14" '
            f'fill="#333">{p:.0%}</text>'
        )
    out.append(
        f'<text x="600" y="{y2 + 90}" font-size="14" fill="#333">'
        '<tspan x="600">Ein Wort wird gewählt,</tspan>'
        '<tspan x="600" dy="19">angehängt – und alles</tspan>'
        '<tspan x="600" dy="19">beginnt von vorn.</tspan></text>'
    )
    out.append(
        f'<path d="M590,{y2 + 112} q-30,0 -30,-30 q0,-24 20,-28" fill="none" '
        f'stroke="{ORANGE}" stroke-width="3"/>'
    )
    out.append(
        f'<polygon points="580,{y2 + 46} 592,{y2 + 56} 577,{y2 + 61}" fill="{ORANGE}"/>'
    )
    out.append("</svg>")
    return "\n".join(out)


SMILEY = [
    "00011111000",
    "00100000100",
    "01000000010",
    "10011011001",
    "10011011001",
    "10000000001",
    "10100000101",
    "10011111001",
    "01000000010",
    "00100000100",
    "00011111000",
]


def diffusion_svg() -> str:
    rng = random.Random(42)
    rauschen = [[rng.random() for _ in range(11)] for _ in range(11)]
    stufen = [0.0, 0.3, 0.55, 0.8, 1.0]
    zelle, panel, abstand, x0, y0 = 10, 110, 35, 30, 95
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 330" {FONT}>',
        '<rect width="760" height="330" fill="#fff"/>',
        (
            "<defs>"
            f'<marker id="spitze-grau" markerWidth="10" markerHeight="10" refX="8" refY="5" '
            f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#999"/></marker>'
            f'<marker id="spitze-akzent" markerWidth="10" markerHeight="10" refX="8" refY="5" '
            f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{ROT}"/></marker>'
            "</defs>"
        ),
    ]
    for i, t in enumerate(stufen):
        px = x0 + i * (panel + abstand)
        for r in range(11):
            for c in range(11):
                bild = 0.0 if SMILEY[r][c] == "1" else 1.0
                hell = (1 - t) * bild + t * rauschen[r][c]
                grau = round(hell * 255)
                out.append(
                    f'<rect x="{px + c * zelle}" y="{y0 + r * zelle}" '
                    f'width="{zelle}" height="{zelle}" '
                    f'fill="rgb({grau},{grau},{grau})"/>'
                )
        out.append(
            f'<rect x="{px}" y="{y0}" width="{panel}" height="{panel}" '
            'fill="none" stroke="#666"/>'
        )
        beschriftung = ["Bild", "", "", "", "reines Rauschen"][i]
        if beschriftung:
            out.append(
                f'<text x="{px + panel / 2:.0f}" y="{y0 + panel + 22}" '
                f'text-anchor="middle" font-size="14" fill="#333">'
                f"{beschriftung}</text>"
            )
    links, rechts = x0 + 20, x0 + 4 * (panel + abstand) + panel - 20
    out.append(
        f'<line x1="{links}" y1="62" x2="{rechts}" y2="62" stroke="#999" '
        'stroke-width="4" marker-end="url(#spitze-grau)"/>'
    )
    out.append(
        f'<text x="{(links + rechts) / 2:.0f}" y="44" text-anchor="middle" '
        'font-size="16" fill="#333"><tspan font-weight="bold">Training:</tspan> '
        "Schritt für Schritt Rauschen hinzufügen – das Netz lernt, das Rauschen "
        "zu erkennen</text>"
    )
    out.append(
        f'<line x1="{rechts}" y1="270" x2="{links}" y2="270" stroke="{ROT}" '
        'stroke-width="4" marker-end="url(#spitze-akzent)"/>'
    )
    out.append(
        f'<text x="{(links + rechts) / 2:.0f}" y="302" text-anchor="middle" '
        f'font-size="16" fill="{ROT}"><tspan font-weight="bold">Bilderzeugung:</tspan> '
        "mit Rauschen starten und es Schritt für Schritt entfernen</text>"
    )
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    ziel = Path(sys.argv[1])
    (ziel / "ki-transformer.svg").write_text(transformer_svg(), encoding="utf-8")
    (ziel / "ki-diffusion.svg").write_text(diffusion_svg(), encoding="utf-8")
