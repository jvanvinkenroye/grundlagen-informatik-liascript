"""Erzeugt die statischen Abbildungen des Kurses als SVG.

Aufruf: uv run python tools/make_abbildungen.py img
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import drawsvg as dw

sys.path.insert(0, str(Path(__file__).parent))
from zeichnen import (
    AKZENT,
    AKZENT_DUNKEL,
    AKZENT_FLAECHE,
    AKZENT_HELL,
    GRAU,
    GRAU_FLAECHE,
    LINIE,
    MONO,
    TEXT,
    TEXT_LEISE,
    WEISS,
    kasten,
    linie,
    pfeil,
    symbol_laptop,
    symbol_pc,
    symbol_smartphone,
    symbol_tablet,
    text,
    wolke,
    zeichnung,
)

# --- 2.4 Digitalisierung ----------------------------------------------------


def _herz_umriss(cx: float, cy: float, s: float, n: int = 200) -> list[tuple]:
    """Klassische Herzkurve, skaliert und nach (cx, cy) verschoben."""
    punkte = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = (
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )
        punkte.append((cx + x * s, cy - y * s))
    return punkte


def _im_polygon(px: float, py: float, poly: list[tuple]) -> bool:
    innen = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            innen = not innen
        j = i
    return innen


def digitalisierung() -> dw.Drawing:
    d = zeichnung(760, 330)
    n, zelle = 12, 14
    seite = n * zelle
    oben = 60
    xs = [40, 296, 552]

    # 1. Original: glatte Kurve
    herz = _herz_umriss(xs[0] + seite / 2, oben + seite / 2 + 4, seite / 36)
    d.append(dw.Rectangle(xs[0], oben, seite, seite, fill=WEISS, stroke=GRAU))
    d.append(dw.Lines(*[c for p in herz for c in p], close=True, fill=AKZENT_DUNKEL))

    # 2. Raster: Zelle schwarz, wenn ihr Mittelpunkt im Herz liegt
    herz2 = _herz_umriss(xs[1] + seite / 2, oben + seite / 2 + 4, seite / 36)
    bits = []
    for r in range(n):
        zeile = ""
        for c in range(n):
            mx, my = xs[1] + (c + 0.5) * zelle, oben + (r + 0.5) * zelle
            an = _im_polygon(mx, my, herz2)
            zeile += "1" if an else "0"
            d.append(
                dw.Rectangle(
                    xs[1] + c * zelle,
                    oben + r * zelle,
                    zelle,
                    zelle,
                    fill=AKZENT_DUNKEL if an else WEISS,
                    stroke=GRAU,
                    stroke_width=0.6,
                )
            )
        bits.append(zeile)

    # 3. Bits: eine Textzeile pro Rasterzeile
    d.append(dw.Rectangle(xs[2], oben, seite, seite, fill=GRAU_FLAECHE, stroke=GRAU))
    for r, zeile in enumerate(bits):
        text(
            d,
            zeile,
            xs[2] + seite / 2,
            oben + 12 + r * zelle,
            11.5,
            schrift=MONO,
            farbe=TEXT,
        )

    for i, titel in enumerate(
        ["1. Original", "2. Raster auflegen", "3. Als Bits speichern"]
    ):
        text(d, titel, xs[i] + seite / 2, 40, 16, fett=True)
    unter = [
        "unendlich viele Punkte",
        f"{n} × {n} = {n * n} Bildpunkte",
        "1 = dunkel, 0 = hell",
    ]
    for i, t in enumerate(unter):
        text(d, t, xs[i] + seite / 2, oben + seite + 26, 13, farbe=TEXT_LEISE)
    for i in range(2):
        x1 = xs[i] + seite + 14
        pfeil(
            d,
            x1,
            oben + seite / 2,
            xs[i + 1] - 14,
            oben + seite / 2,
            farbe=AKZENT,
            breite=3,
        )
    text(
        d,
        "Feineres Raster = genaueres Abbild, aber mehr Bits.",
        380,
        312,
        14,
        farbe=AKZENT_DUNKEL,
        fett=True,
    )
    return d


# --- 3.4 Neuronales Netz ----------------------------------------------------


def _katze(d: dw.Drawing, x: float, y: float, s: float = 1) -> None:
    """Sehr einfache Katzen-Silhouette als Eingabebild."""
    d.append(
        dw.Rectangle(
            x - 34 * s,
            y - 34 * s,
            68 * s,
            68 * s,
            rx=4 * s,
            fill=GRAU_FLAECHE,
            stroke=GRAU,
        )
    )
    for dx in (-1, 1):
        d.append(
            dw.Lines(
                x + dx * 20 * s,
                y - 2 * s,
                x + dx * 22 * s,
                y - 26 * s,
                x + dx * 6 * s,
                y - 14 * s,
                close=True,
                fill=AKZENT_DUNKEL,
            )
        )
    d.append(dw.Circle(x, y + 4 * s, 20 * s, fill=AKZENT_DUNKEL))
    for dx in (-8, 8):
        d.append(dw.Circle(x + dx * s, y + 1 * s, 3.2 * s, fill=AKZENT_HELL))
    for dy in (8, 12):
        for dx in (-1, 1):
            d.append(
                dw.Line(
                    x + dx * 10 * s,
                    y + dy * s,
                    x + dx * 30 * s,
                    y + (dy - 3 + (dy - 8)) * s,
                    stroke=GRAU,
                    stroke_width=1.2 * s,
                )
            )


def neuronales_netz() -> dw.Drawing:
    d = zeichnung(760, 420)
    rng = random.Random(7)
    schichten = [4, 5, 5, 3]
    xs = [190, 320, 450, 580]
    oben, unten = 80, 330

    def ys(k: int) -> list[float]:
        schritt = (unten - oben) / (k + 1)
        return [oben + schritt * (i + 1) for i in range(k)]

    # Verbindungen mit zufälligen Gewichten: Dicke = Stärke, grau = hemmend
    for a in range(len(schichten) - 1):
        for y1 in ys(schichten[a]):
            for y2 in ys(schichten[a + 1]):
                w = rng.uniform(-1, 1)
                d.append(
                    dw.Line(
                        xs[a],
                        y1,
                        xs[a + 1],
                        y2,
                        stroke=AKZENT_HELL if w > 0 else GRAU,
                        stroke_width=0.5 + abs(w) * 3,
                        stroke_opacity=0.8,
                    )
                )
    for i, (x, k) in enumerate(zip(xs, schichten)):
        for y in ys(k):
            d.append(
                dw.Circle(
                    x,
                    y,
                    13,
                    fill=AKZENT if i in (0, 3) else WEISS,
                    stroke=AKZENT_DUNKEL,
                    stroke_width=2,
                )
            )

    _katze(d, 80, (oben + unten) / 2)
    pfeil(d, 120, (oben + unten) / 2, 168, (oben + unten) / 2, farbe=LINIE)
    text(
        d, ["Foto als", "Pixelwerte"], 80, (oben + unten) / 2 + 58, 12, farbe=TEXT_LEISE
    )

    # Ausgabe mit Wahrscheinlichkeiten
    ergebnisse = [("Katze", 0.91), ("Hund", 0.07), ("Vogel", 0.02)]
    for (name, p), y in zip(ergebnisse, ys(3)):
        text(d, name, 606, y + 5, 14, anker="start", fett=p > 0.5)
        d.append(
            dw.Rectangle(660, y - 8, 70 * p + 1, 16, fill=AKZENT if p > 0.5 else GRAU)
        )
        text(d, f"{p:.0%}", 664 + 70 * p, y + 5, 12, anker="start", farbe=TEXT_LEISE)

    for x, beschriftung in zip(
        [190, 385, 580], ["Eingabeschicht", "verdeckte Schichten", "Ausgabeschicht"]
    ):
        text(d, beschriftung, x, 364, 14, fett=True)
    text(d, ["Pixel", "hell/dunkel"], 190, 382, 11, farbe=TEXT_LEISE)
    text(d, ["Kanten, Formen,", "Ohren, Augen …"], 385, 382, 11, farbe=TEXT_LEISE)
    text(d, ["Wahrscheinlichkeit", "je Antwort"], 580, 382, 11, farbe=TEXT_LEISE)

    text(d, "Ist auf dem Foto eine Katze?", 380, 36, 18, fett=True)
    linie(d, 150, 54, 180, 54, farbe=AKZENT_HELL, breite=3.5)
    text(d, "starkes Gewicht", 186, 58, 12, anker="start", farbe=TEXT_LEISE)
    linie(d, 300, 54, 330, 54, farbe=AKZENT_HELL, breite=1)
    text(d, "schwaches Gewicht", 336, 58, 12, anker="start", farbe=TEXT_LEISE)
    linie(d, 460, 54, 490, 54, farbe=GRAU, breite=2.5)
    text(d, "hemmendes Gewicht", 496, 58, 12, anker="start", farbe=TEXT_LEISE)
    return d


# --- 4.6 Cloud-Ebenen -------------------------------------------------------


def cloud_ebenen() -> dw.Drawing:
    d = zeichnung(760, 470)
    wolke(d, 380, 255, 480, 300, fuellung=WEISS, rand=AKZENT)
    ebenen = [
        ("Anwendungen", "SaaS", ["E-Mail", "Office", "Fachsoftware", "Kalender"]),
        ("Plattform", "PaaS", ["Betriebssystem", "Datenbank", "Entwicklung"]),
        ("Infrastruktur", "IaaS", ["Rechenleistung", "Speicher", "Netzwerk"]),
    ]
    for i, (name, kurz, bausteine) in enumerate(ebenen):
        y = 150 + i * 72
        kasten(
            d,
            180,
            y,
            400,
            58,
            fuellung=[AKZENT_FLAECHE, "#CFE6E4", "#B5D9D6"][i],
            rand=AKZENT,
        )
        text(d, name, 192, y + 22, 14, anker="start", fett=True)
        text(d, kurz, 192, y + 42, 12, anker="start", farbe=AKZENT_DUNKEL)
        bx = 304
        for baustein in bausteine:
            breite = len(baustein) * 6.6 + 14
            kasten(
                d,
                bx,
                y + 16,
                breite,
                26,
                baustein,
                fuellung=WEISS,
                rand=AKZENT_HELL,
                groesse=11.5,
                radius=13,
            )
            bx += breite + 6

    geraete = [
        (symbol_pc, 52, 170, "PC"),
        (symbol_laptop, 52, 350, "Notebook"),
        (symbol_smartphone, 710, 170, "Smartphone"),
        (symbol_tablet, 710, 340, "Tablet"),
    ]
    for zeichne, x, y, name in geraete:
        zeichne(d, x, y, 1)
        text(d, name, x, y + 42, 12, farbe=TEXT_LEISE)
        ziel_x = 150 if x < 380 else 610
        linie(
            d,
            x + (32 if x < 380 else -24),
            y,
            ziel_x,
            y,
            farbe=AKZENT_HELL,
            gestrichelt=True,
        )
    text(
        d,
        "Über das Internet bereitgestellt: Zugriff von überall und mit jedem Gerät",
        380,
        455,
        13,
        farbe=TEXT_LEISE,
    )
    text(d, "Cloud Computing: drei Ebenen", 380, 34, 18, fett=True)
    return d


# --- 4.7 Servicemodelle -----------------------------------------------------


def cloud_servicemodelle() -> dw.Drawing:
    d = zeichnung(760, 440)
    spalten = ["Eigener Betrieb", "IaaS", "PaaS", "SaaS"]
    zeilen = [
        "Daten",
        "Anwendungen",
        "Datenbank, Laufzeit",
        "Betriebssystem",
        "Server (virtuell)",
        "Speicher und Netz",
        "Rechenzentrum",
    ]
    # Ab welcher Zeile (von oben) der Anbieter zuständig ist; Daten bleiben
    # in jedem Modell in der Verantwortung der Einrichtung
    anbieter_ab = [len(zeilen), 3, 2, 1]
    x0, y0, sb, zh = 200, 80, 132, 40
    for j, name in enumerate(spalten):
        text(d, name, x0 + j * sb + sb / 2, y0 - 14, 15, fett=True)
    for i, name in enumerate(zeilen):
        text(d, name, x0 - 12, y0 + i * zh + zh / 2 + 5, 13, anker="end")
        for j in range(len(spalten)):
            selbst = i < anbieter_ab[j]
            d.append(
                dw.Rectangle(
                    x0 + j * sb + 3,
                    y0 + i * zh + 3,
                    sb - 6,
                    zh - 6,
                    rx=4,
                    fill=AKZENT if selbst else GRAU_FLAECHE,
                    stroke=AKZENT_DUNKEL if selbst else GRAU,
                )
            )
            text(
                d,
                "Einrichtung" if selbst else "Anbieter",
                x0 + j * sb + sb / 2,
                y0 + i * zh + zh / 2 + 5,
                12,
                farbe=WEISS if selbst else TEXT_LEISE,
            )
    ly = y0 + len(zeilen) * zh + 28
    d.append(dw.Rectangle(200, ly - 12, 16, 16, rx=3, fill=AKZENT))
    text(d, "verwaltet die Einrichtung selbst", 224, ly + 1, 13, anker="start")
    d.append(dw.Rectangle(460, ly - 12, 16, 16, rx=3, fill=GRAU_FLAECHE, stroke=GRAU))
    text(d, "übernimmt der Cloud-Anbieter", 484, ly + 1, 13, anker="start")
    text(d, "Wer verwaltet was?", 380, 34, 18, fett=True)
    return d


# --- 5.2 und 5.3 Datenbanktabellen ------------------------------------------


KLIENTEN = [
    ("1", "Arslan", "Ahmet", "14.03.1961", "Nordstadt"),
    ("2", "Becker", "Bianca", "02.09.1978", "Südstadt"),
    ("3", "Costa", "Carlos", "21.11.1985", "Altstadt"),
    ("4", "Dietrich", "Dennis", "07.05.1949", "Weststadt"),
    ("5", "Engel", "Emma", "30.01.1993", "Südstadt"),
    ("6", "Fischer", "Felix", "18.07.1970", "Nordstadt"),
]


def _tabelle(
    d: dw.Drawing,
    x: float,
    y: float,
    titel: str,
    kopf: list[str],
    zeilen: list[tuple],
    breiten: list[float],
    *,
    zh: float = 30,
    markiert: dict[tuple[int, int], str] | None = None,
    zeile_markiert: int | None = None,
) -> None:
    """Zeichnet eine Tabelle; markiert: {(zeile, spalte): farbe}."""
    markiert = markiert or {}
    gesamt = sum(breiten)
    text(d, titel, x, y - 10, 15, anker="start", fett=True, farbe=AKZENT_DUNKEL)
    cx = x
    for b, k in zip(breiten, kopf):
        d.append(dw.Rectangle(cx, y, b, zh, fill=AKZENT, stroke=WEISS))
        text(d, k, cx + 8, y + zh / 2 + 5, 13, anker="start", fett=True, farbe=WEISS)
        cx += b
    for r, werte in enumerate(zeilen):
        cy = y + (r + 1) * zh
        cx = x
        for c, (b, w) in enumerate(zip(breiten, werte)):
            fuellung = markiert.get((r, c))
            if fuellung is None:
                fuellung = (
                    AKZENT_FLAECHE
                    if r == zeile_markiert
                    else (WEISS if r % 2 == 0 else GRAU_FLAECHE)
                )
            d.append(
                dw.Rectangle(
                    cx, cy, b, zh, fill=fuellung, stroke=GRAU, stroke_width=0.8
                )
            )
            text(d, w, cx + 8, cy + zh / 2 + 5, 13, anker="start")
            cx += b
    d.append(
        dw.Rectangle(
            x,
            y,
            gesamt,
            (len(zeilen) + 1) * zh,
            fill="none",
            stroke=AKZENT_DUNKEL,
            stroke_width=1.5,
        )
    )


def db_tabelle() -> dw.Drawing:
    d = zeichnung(760, 400)
    breiten = [44, 100, 90, 116, 104]
    x, y, zh = 130, 110, 30
    _tabelle(
        d,
        x,
        y,
        "Tabelle „Klienten“",
        ["ID", "Nachname", "Vorname", "Geburtsdatum", "Stadtteil"],
        KLIENTEN,
        breiten,
        zh=zh,
        markiert={(1, 4): "#9FD0CB"},
        zeile_markiert=1,
    )
    gesamt = sum(breiten)
    rechts = x + gesamt
    # Beschriftungen mit Hinweislinien
    spalte_x = x + breiten[0] + breiten[1] + breiten[2] / 2
    linie(d, spalte_x, y - 4, spalte_x, 70, farbe=AKZENT_DUNKEL, breite=1.5)
    text(d, "Spalte = Attribut (z. B. Vorname)", spalte_x, 62, 13, fett=True)
    zeile_y = y + 2 * zh + zh / 2
    linie(d, x - 4, zeile_y, 100, zeile_y, farbe=AKZENT_DUNKEL, breite=1.5)
    text(d, ["Zeile =", "Datensatz"], 92, zeile_y - 4, 13, anker="end", fett=True)
    feld_y = y + 2 * zh + zh / 2
    linie(d, rechts + 4, feld_y, 600, feld_y, farbe=AKZENT_DUNKEL, breite=1.5)
    text(
        d,
        ["Feld =", "ein einzelner Wert"],
        608,
        feld_y - 4,
        13,
        anker="start",
        fett=True,
    )
    id_y = y + 7 * zh
    linie(
        d,
        x + breiten[0] / 2,
        id_y + 4,
        x + breiten[0] / 2,
        id_y + 30,
        farbe=AKZENT_DUNKEL,
        breite=1.5,
    )
    text(
        d,
        "Schlüssel (ID): eindeutige Nummer für jeden Datensatz",
        x + breiten[0] / 2 - 10,
        id_y + 48,
        13,
        anker="start",
        fett=True,
    )
    text(d, "Aufbau einer Datenbanktabelle", 380, 32, 18, fett=True)
    return d


def db_verknuepfung() -> dw.Drawing:
    d = zeichnung(760, 395)
    betreuer = [
        ("1", "Schulz", "Jugend"),
        ("2", "Hoffmann", "Familie"),
        ("3", "König", "Senioren"),
    ]
    klienten = [
        ("1", "Arslan", "1"),
        ("2", "Becker", "2"),
        ("3", "Costa", "2"),
        ("4", "Dietrich", "3"),
        ("5", "Engel", "3"),
        ("6", "Fischer", "2"),
    ]
    zh = 30
    bx, by = [44, 100, 90], 90
    bb = sum(bx)
    kx_start = 440
    kb = [44, 100, 100]
    ky = 90
    _tabelle(
        d,
        60,
        by,
        "Tabelle „Betreuer“",
        ["ID", "Name", "Team"],
        betreuer,
        bx,
        zh=zh,
        markiert={(1, 0): "#9FD0CB"},
    )
    markiert = {(r, 2): "#9FD0CB" for r, k in enumerate(klienten) if k[2] == "2"}
    _tabelle(
        d,
        kx_start,
        ky,
        "Tabelle „Klienten“",
        ["ID", "Name", "Betreuer-ID"],
        klienten,
        kb,
        zh=zh,
        markiert=markiert,
    )
    # Pfeile von jeder Betreuer-ID zur passenden Zeile der Betreuer-Tabelle
    for r, (_, _, bid) in enumerate(klienten):
        y1 = ky + (r + 1) * zh + zh / 2
        y2 = by + int(bid) * zh + zh / 2
        hervor = bid == "2"
        pfeil(
            d,
            kx_start - 4,
            y1,
            60 + bb + 6,
            y2,
            farbe=AKZENT if hervor else GRAU,
            breite=2.2 if hervor else 1.4,
        )
    unten = ky + (len(klienten) + 1) * zh
    text(
        d,
        [
            "Die Spalte „Betreuer-ID“ verweist auf die ID in der anderen Tabelle.",
            "Hoffmann (ID 2) betreut drei Personen. Für einen Betreuungswechsel",
            "muss nur diese eine Zahl geändert werden.",
        ],
        380,
        unten + 32,
        13,
        farbe=TEXT_LEISE,
    )
    text(d, "Zwei Tabellen, verknüpft über die ID", 380, 32, 18, fett=True)
    return d


ABBILDUNGEN = {
    "digitalisierung": digitalisierung,
    "neuronales-netz": neuronales_netz,
    "cloud-ebenen": cloud_ebenen,
    "cloud-servicemodelle": cloud_servicemodelle,
    "db-tabelle": db_tabelle,
    "db-verknuepfung": db_verknuepfung,
}


if __name__ == "__main__":
    ziel = Path(sys.argv[1] if len(sys.argv) > 1 else "img")
    for name, erzeuge in ABBILDUNGEN.items():
        erzeuge().save_svg(str(ziel / f"{name}.svg"))
        print(f"{name}.svg")
