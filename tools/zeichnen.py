"""Kleines Zeichen-Framework auf Basis von drawsvg.

Sorgt dafür, dass alle Abbildungen des Kurses dieselben Farben, Schriften,
Kästen, Pfeile und Gerätesymbole verwenden. Koordinaten: Ursprung oben links,
y wächst nach unten.
"""

from __future__ import annotations

import drawsvg as dw

# Farbpalette, abgestimmt auf das Standarddesign von LiaScript (Petrol)
AKZENT = "#147375"
AKZENT_HELL = "#2A9D8F"
AKZENT_DUNKEL = "#264653"
AKZENT_FLAECHE = "#E3F1F0"
TEXT = "#1A1A1A"
TEXT_LEISE = "#555555"
LINIE = "#666666"
GRAU = "#B3B3B3"
GRAU_FLAECHE = "#F0F0F0"
WEISS = "#FFFFFF"

SCHRIFT = "Arial, Helvetica, sans-serif"
MONO = "Menlo, Consolas, monospace"


def zeichnung(breite: int, hoehe: int) -> dw.Drawing:
    d = dw.Drawing(breite, hoehe)
    d.append(dw.Rectangle(0, 0, breite, hoehe, fill=WEISS))
    return d


def text(
    d: dw.Drawing,
    zeilen: str | list[str],
    x: float,
    y: float,
    groesse: float = 14,
    *,
    anker: str = "middle",
    fett: bool = False,
    farbe: str = TEXT,
    schrift: str = SCHRIFT,
    zeilenabstand: float = 1.25,
    mittig: bool = False,
) -> None:
    """Schreibt einen ein- oder mehrzeiligen Text.

    Mit mittig=True ist y die vertikale Mitte des Textblocks, sonst die
    Grundlinie der ersten Zeile.
    """
    if isinstance(zeilen, str):
        zeilen = zeilen.split("\n")
    schritt = groesse * zeilenabstand
    if mittig:
        # Grundlinie der ersten Zeile so wählen, dass der Block zentriert ist
        y = y - (len(zeilen) - 1) * schritt / 2 + groesse * 0.35
    for i, zeile in enumerate(zeilen):
        d.append(
            dw.Text(
                zeile,
                groesse,
                x,
                y + i * schritt,
                text_anchor=anker,
                font_family=schrift,
                font_weight="bold" if fett else "normal",
                fill=farbe,
            )
        )


def kasten(
    d: dw.Drawing,
    x: float,
    y: float,
    b: float,
    h: float,
    beschriftung: str | list[str] = "",
    *,
    fuellung: str = AKZENT_FLAECHE,
    rand: str = AKZENT,
    textfarbe: str = TEXT,
    groesse: float = 14,
    fett: bool = False,
    radius: float = 6,
    gestrichelt: bool = False,
) -> None:
    d.append(
        dw.Rectangle(
            x,
            y,
            b,
            h,
            rx=radius,
            fill=fuellung,
            stroke=rand,
            stroke_width=1.5,
            stroke_dasharray="6 4" if gestrichelt else None,
        )
    )
    if beschriftung:
        text(
            d,
            beschriftung,
            x + b / 2,
            y + h / 2,
            groesse,
            fett=fett,
            farbe=textfarbe,
            mittig=True,
        )


def _pfeilspitze(farbe: str) -> dw.Marker:
    spitze = dw.Marker(-0.1, -0.5, 0.9, 0.5, scale=4, orient="auto")
    spitze.append(dw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill=farbe, close=True))
    return spitze


def pfeil(
    d: dw.Drawing,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    farbe: str = LINIE,
    breite: float = 2,
    beidseitig: bool = False,
    gestrichelt: bool = False,
) -> None:
    spitze = _pfeilspitze(farbe)
    d.append(
        dw.Line(
            x1,
            y1,
            x2,
            y2,
            stroke=farbe,
            stroke_width=breite,
            stroke_dasharray="6 4" if gestrichelt else None,
            marker_end=spitze,
            marker_start=spitze if beidseitig else None,
        )
    )


def linie(
    d: dw.Drawing,
    *punkte: float,
    farbe: str = LINIE,
    breite: float = 2,
    gestrichelt: bool = False,
) -> None:
    d.append(
        dw.Lines(
            *punkte,
            fill="none",
            stroke=farbe,
            stroke_width=breite,
            stroke_dasharray="6 4" if gestrichelt else None,
        )
    )


# --- Gerätesymbole ---------------------------------------------------------
# Jedes Symbol ist um (x, y) zentriert; s skaliert die Grundgröße.


def symbol_monitor(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    b, h = 46 * s, 32 * s
    d.append(
        dw.Rectangle(x - b / 2, y - h / 2 - 6 * s, b, h, rx=3 * s, fill=AKZENT_DUNKEL)
    )
    d.append(
        dw.Rectangle(
            x - b / 2 + 3 * s,
            y - h / 2 - 3 * s,
            b - 6 * s,
            h - 6 * s,
            fill=AKZENT_FLAECHE,
        )
    )
    d.append(
        dw.Rectangle(x - 3 * s, y + h / 2 - 6 * s, 6 * s, 8 * s, fill=AKZENT_DUNKEL)
    )
    d.append(
        dw.Rectangle(
            x - 13 * s, y + h / 2 + 2 * s, 26 * s, 3 * s, rx=1.5 * s, fill=AKZENT_DUNKEL
        )
    )


def symbol_thin_client(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    symbol_monitor(d, x, y, s * 0.85)
    # kleines Kästchen neben dem Bildschirm statt eines PC-Gehäuses
    d.append(
        dw.Rectangle(x + 22 * s, y + 4 * s, 7 * s, 10 * s, rx=1.5 * s, fill=AKZENT_HELL)
    )


def symbol_pc(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    symbol_monitor(d, x - 6 * s, y, s)
    d.append(
        dw.Rectangle(
            x + 20 * s, y - 20 * s, 14 * s, 38 * s, rx=2 * s, fill=AKZENT_DUNKEL
        )
    )
    for i in range(3):
        d.append(
            dw.Rectangle(
                x + 23 * s, y - 15 * s + i * 6 * s, 8 * s, 2 * s, fill=AKZENT_FLAECHE
            )
        )


def symbol_laptop(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    b, h = 44 * s, 28 * s
    d.append(dw.Rectangle(x - b / 2, y - h, b, h, rx=3 * s, fill=AKZENT_DUNKEL))
    d.append(
        dw.Rectangle(
            x - b / 2 + 3 * s, y - h + 3 * s, b - 6 * s, h - 6 * s, fill=AKZENT_FLAECHE
        )
    )
    d.append(
        dw.Lines(
            x - b / 2 - 6 * s,
            y + 6 * s,
            x + b / 2 + 6 * s,
            y + 6 * s,
            x + b / 2,
            y,
            x - b / 2,
            y,
            close=True,
            fill=AKZENT_DUNKEL,
        )
    )


def symbol_smartphone(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    b, h = 18 * s, 32 * s
    d.append(dw.Rectangle(x - b / 2, y - h / 2, b, h, rx=3 * s, fill=AKZENT_DUNKEL))
    d.append(
        dw.Rectangle(
            x - b / 2 + 2 * s,
            y - h / 2 + 4 * s,
            b - 4 * s,
            h - 9 * s,
            fill=AKZENT_FLAECHE,
        )
    )


def symbol_tablet(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    b, h = 30 * s, 38 * s
    d.append(dw.Rectangle(x - b / 2, y - h / 2, b, h, rx=3 * s, fill=AKZENT_DUNKEL))
    d.append(
        dw.Rectangle(
            x - b / 2 + 3 * s,
            y - h / 2 + 3 * s,
            b - 6 * s,
            h - 8 * s,
            fill=AKZENT_FLAECHE,
        )
    )


def symbol_server(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    b = 40 * s
    for i in range(3):
        oy = y - 24 * s + i * 16 * s
        d.append(dw.Rectangle(x - b / 2, oy, b, 13 * s, rx=2 * s, fill=AKZENT_DUNKEL))
        d.append(dw.Circle(x + b / 2 - 6 * s, oy + 6.5 * s, 2 * s, fill=AKZENT_HELL))
        d.append(
            dw.Rectangle(
                x - b / 2 + 5 * s, oy + 5.5 * s, 18 * s, 2 * s, fill=AKZENT_FLAECHE
            )
        )


def symbol_router(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    b, h = 52 * s, 16 * s
    for dx in (-14, 14):
        d.append(
            dw.Line(
                x + dx * s,
                y - h / 2,
                x + dx * s * 1.3,
                y - h / 2 - 14 * s,
                stroke=AKZENT_DUNKEL,
                stroke_width=3 * s,
            )
        )
    d.append(dw.Rectangle(x - b / 2, y - h / 2, b, h, rx=3 * s, fill=AKZENT_DUNKEL))
    for i in range(5):
        d.append(dw.Circle(x - 16 * s + i * 8 * s, y, 2 * s, fill=AKZENT_HELL))


def symbol_funk(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    """Accesspoint: Sockel mit Funkwellen."""
    d.append(dw.Rectangle(x - 16 * s, y, 32 * s, 9 * s, rx=3 * s, fill=AKZENT_DUNKEL))
    for r in (8, 14, 20):
        d.append(
            dw.Arc(
                x,
                y,
                r * s,
                30,
                150,
                cw=False,
                fill="none",
                stroke=AKZENT_HELL,
                stroke_width=2.5 * s,
            )
        )


def wolke(
    d: dw.Drawing,
    x: float,
    y: float,
    b: float,
    h: float,
    *,
    fuellung: str = WEISS,
    rand: str = AKZENT,
    randbreite: float = 2,
) -> None:
    """Wolke aus überlappenden Kreisen; (x, y) ist die Mitte."""
    kreise = [
        (-0.30, 0.12, 0.26),
        (-0.05, -0.12, 0.34),
        (0.27, 0.02, 0.28),
        (0.05, 0.18, 0.28),
        (-0.38, 0.22, 0.17),
        (0.40, 0.22, 0.17),
    ]
    teile = [(x + dx * b, y + dy * h, r * min(b, h * 1.6)) for dx, dy, r in kreise]
    # erst die Kreise mit dickem Rand zeichnen, dann innen übermalen:
    # so bleibt nur die äußere Umrisslinie sichtbar
    for cx, cy, r in teile:
        d.append(
            dw.Circle(cx, cy, r, fill=rand, stroke=rand, stroke_width=randbreite * 2)
        )
    for cx, cy, r in teile:
        d.append(dw.Circle(cx, cy, r, fill=fuellung))
