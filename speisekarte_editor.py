# -*- coding: utf-8 -*-
"""
Speisekarte bearbeiten für Eiscafé Nico (PySide6, dunkles Design)
----------------------------------------------------------------------------
Mit diesem Programm bearbeitest du "speisekarte-config.js" ganz ohne Code:

  - Preise, Namen und Beschreibungen von bestehenden Positionen ändern
  - NEUE Eisbecher, Getränke, Cocktails usw. zu einer Kategorie hinzufügen
    (nicht nur bestehende Zeilen austauschen)
  - Positionen wieder entfernen
  - Bei Bedarf eine ganz neue Kategorie anlegen (eigener Reiter)
  - Kuchen-Kacheln bearbeiten (inkl. "kein fester Preis", z.B. "siehe Auslage")

Kugel-Preis nur an EINER Stelle pflegen:
  In der Original-Datei musste der Kugel-Preis von Hand an zwei Stellen
  gleich gehalten werden (Badge oben UND der Hinweistext bei den
  Eisbechern). Das übernimmt dieses Programm jetzt automatisch: du trägst
  den Kugel-Preis nur noch im Reiter "Preise & Kugeleis" ein, der
  Hinweistext bei den Eisbechern wird beim Speichern daraus von selbst
  neu zusammengesetzt.

Speichern schreibt direkt "speisekarte-config.js" im selben Ordner neu
(eine Sicherheitskopie der alten Version landet automatisch in
"speisekarte-config.backup.js"). Nach dem Speichern muss die Datei nur
noch ganz normal - wie "bilder-config.js" - über die Zentrale bei der
Webseiten-Kachel ("Zum Hochladen öffnen") per Drag & Drop hochgeladen
werden.

Benötigt: PySide6
    pip install PySide6

Start: Doppelklick auf diese Datei, oder im Terminal:
    python speisekarte_editor.py
"""

import json
import os
import re
import shutil
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QScrollArea, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog,
)

ORDNER = os.path.dirname(os.path.abspath(__file__))
CONFIG_DATEI = os.path.join(ORDNER, "speisekarte-config.js")
BACKUP_DATEI = os.path.join(ORDNER, "speisekarte-config.backup.js")

LOGO_PNG = os.path.join(ORDNER, "logo.png")
LOGO_ICO = os.path.join(ORDNER, "logo.ico")

# Spalten der Positions-Tabelle: (Schlüssel, Überschrift, Breite oder None=dehnt sich)
SPALTEN = [
    ("name", "Name", None),
    ("preis", "Preis", 130),
    ("desc", "Beschreibung", None),
    ("gruppe", "Gruppe (optional)", 150),
]


# =================================================================
# Ganz kleiner Parser für JS-Objekt-Literale (Teilmenge von JSON,
# aber mit unquotierten Schlüsseln und // bzw. /* */ Kommentaren) -
# genau das, was in "speisekarte-config.js" verwendet wird.
# =================================================================
class JSParseFehler(Exception):
    pass


class _JSParser:
    def __init__(self, text):
        self.t = text
        self.i = 0
        self.n = len(text)

    def skip_ws(self):
        while self.i < self.n:
            c = self.t[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif c == "/" and self.i + 1 < self.n and self.t[self.i + 1] == "/":
                while self.i < self.n and self.t[self.i] != "\n":
                    self.i += 1
            elif c == "/" and self.i + 1 < self.n and self.t[self.i + 1] == "*":
                self.i += 2
                while self.i + 1 < self.n and not (self.t[self.i] == "*" and self.t[self.i + 1] == "/"):
                    self.i += 1
                self.i += 2
            else:
                break

    def peek(self):
        return self.t[self.i] if self.i < self.n else ""

    def erwarte(self, ch):
        self.skip_ws()
        if self.peek() != ch:
            raise JSParseFehler(f"Erwartet '{ch}' an Position {self.i}")
        self.i += 1

    def parse_wert(self):
        self.skip_ws()
        c = self.peek()
        if c == "{":
            return self.parse_objekt()
        if c == "[":
            return self.parse_array()
        if c in "\"'":
            return self.parse_string()
        if c.isdigit() or c == "-":
            return self.parse_zahl()
        if self.t[self.i:self.i + 4] == "true":
            self.i += 4
            return True
        if self.t[self.i:self.i + 5] == "false":
            self.i += 5
            return False
        if self.t[self.i:self.i + 4] == "null":
            self.i += 4
            return None
        raise JSParseFehler(f"Unerwartetes Zeichen an Position {self.i}")

    def parse_objekt(self):
        self.erwarte("{")
        ergebnis = {}
        self.skip_ws()
        while self.peek() != "}":
            schluessel = self.parse_schluessel()
            self.skip_ws()
            self.erwarte(":")
            ergebnis[schluessel] = self.parse_wert()
            self.skip_ws()
            if self.peek() == ",":
                self.i += 1
                self.skip_ws()
        self.erwarte("}")
        return ergebnis

    def parse_array(self):
        self.erwarte("[")
        ergebnis = []
        self.skip_ws()
        while self.peek() != "]":
            ergebnis.append(self.parse_wert())
            self.skip_ws()
            if self.peek() == ",":
                self.i += 1
                self.skip_ws()
        self.erwarte("]")
        return ergebnis

    def parse_schluessel(self):
        self.skip_ws()
        if self.peek() in "\"'":
            return self.parse_string()
        start = self.i
        while self.i < self.n and (self.t[self.i].isalnum() or self.t[self.i] == "_"):
            self.i += 1
        return self.t[start:self.i]

    def parse_string(self):
        quote = self.peek()
        self.i += 1
        out = []
        while self.i < self.n and self.t[self.i] != quote:
            if self.t[self.i] == "\\" and self.i + 1 < self.n:
                out.append(self.t[self.i:self.i + 2])
                self.i += 2
            else:
                out.append(self.t[self.i])
                self.i += 1
        self.i += 1
        roh = "".join(out)
        try:
            if quote == '"':
                return json.loads('"' + roh + '"')
            return json.loads('"' + roh.replace('"', '\\"') + '"')
        except Exception:
            return roh

    def parse_zahl(self):
        start = self.i
        if self.peek() == "-":
            self.i += 1
        while self.i < self.n and (self.t[self.i].isdigit() or self.t[self.i] == "."):
            self.i += 1
        stueck = self.t[start:self.i]
        return float(stueck) if "." in stueck else int(stueck)


def js_objekt_extrahieren(js_text, variablen_name="SPEISEKARTE"):
    treffer = re.search(r"const\s+" + variablen_name + r"\s*=\s*", js_text)
    if not treffer:
        raise JSParseFehler(f"Variable {variablen_name} wurde in der Datei nicht gefunden.")
    p = _JSParser(js_text)
    p.i = treffer.end()
    return p.parse_objekt()


def _text_zwischen(text, label):
    """Holt aus einem Hinweistext wie '... · Portion Sahne 1,50 € · Sauce ...'
    den Wert direkt hinter 'label', bis zum nächsten '·' oder Textende."""
    treffer = re.search(re.escape(label) + r"\s*(.+?)(?:\s*·|\s*$)", text)
    return treffer.group(1).strip() if treffer else ""


# =================================================================
# Laden: rohe JS-Datei -> normalisierte Python-Struktur fürs Programm
# =================================================================
STANDARD_DATEN = {
    "kugelPreis": "1,00 €",
    "eismobil": {"preis": "1,50 €", "einheit": "pro Kugel Eis"},
    "kategorien": {
        "eis": {
            "label": "Eisbecher",
            "hinweis_praefix": "Alle Eisbecher auch zum Mitnehmen (außer Haus).",
            "sahne_preis": "1,50 €",
            "sauce_preis": "0,80 €",
            "streusel_preis": "0,80 €",
            "items": [],
        }
    },
    "kuchen": [],
}


def daten_laden():
    if not os.path.exists(CONFIG_DATEI):
        return json.loads(json.dumps(STANDARD_DATEN))
    with open(CONFIG_DATEI, "r", encoding="utf-8") as f:
        text = f.read()
    roh = js_objekt_extrahieren(text)

    daten = {
        "kugelPreis": roh.get("kugelPreis", STANDARD_DATEN["kugelPreis"]),
        "eismobil": roh.get("eismobil", dict(STANDARD_DATEN["eismobil"])),
        "kategorien": {},
        "kuchen": roh.get("kuchen", []),
    }

    for schluessel, kat in roh.get("kategorien", {}).items():
        eintrag = {"label": kat.get("label", schluessel), "items": kat.get("items", [])}
        if schluessel == "eis":
            hinweis = kat.get("hinweis", "")
            praefix_treffer = re.match(r"^(.*?)\s*·\s*Kugel Eis", hinweis)
            eintrag["hinweis_praefix"] = (
                praefix_treffer.group(1).strip() if praefix_treffer
                else STANDARD_DATEN["kategorien"]["eis"]["hinweis_praefix"]
            )
            eintrag["sahne_preis"] = _text_zwischen(hinweis, "Portion Sahne") or "1,50 €"
            eintrag["sauce_preis"] = _text_zwischen(hinweis, "Sauce extra") or "0,80 €"
            eintrag["streusel_preis"] = _text_zwischen(hinweis, "Streusel extra") or "0,80 €"
        daten["kategorien"][schluessel] = eintrag

    return daten


# =================================================================
# Speichern: normalisierte Struktur -> JS-Datei neu erzeugen
# =================================================================
def _js_string(wert):
    return json.dumps(wert if wert is not None else "", ensure_ascii=False)


def _item_zeile_bauen(item, mit_gruppe):
    teile = [f'name: {_js_string(item.get("name", ""))}', f'preis: {_js_string(item.get("preis", ""))}']
    if item.get("desc"):
        teile.append(f'desc: {_js_string(item.get("desc"))}')
    if mit_gruppe and item.get("gruppe"):
        teile.append(f'gruppe: {_js_string(item.get("gruppe"))}')
    return "{ " + ", ".join(teile) + " }"


def speisekarte_js_erzeugen(daten):
    zeilen = []
    zeilen.append("// Diese Datei enthält ALLE Preise der Speisekarte.")
    zeilen.append("// Erzeugt/bearbeitet mit speisekarte_editor.py - einfach speichern und")
    zeilen.append("// wie gewohnt über die Zentrale hochladen.")
    zeilen.append("")
    zeilen.append("const SPEISEKARTE = {")
    zeilen.append("")
    zeilen.append(f'  kugelPreis: {_js_string(daten["kugelPreis"])},')
    zeilen.append("")
    zeilen.append("  eismobil: {")
    zeilen.append(f'    preis: {_js_string(daten["eismobil"].get("preis", ""))},')
    zeilen.append(f'    einheit: {_js_string(daten["eismobil"].get("einheit", ""))}')
    zeilen.append("  },")
    zeilen.append("")
    zeilen.append("  kategorien: {")
    zeilen.append("")

    kategorien_liste = list(daten["kategorien"].items())
    for idx, (schluessel, kat) in enumerate(kategorien_liste):
        label = kat.get("label", schluessel)
        zeilen.append(f"    // ── {label.upper()} ──")
        zeilen.append(f"    {schluessel}: {{")
        zeilen.append(f'      label: {_js_string(label)},')

        if schluessel == "eis":
            kugel = daten["kugelPreis"]
            sahne = kat.get("sahne_preis", "1,50 €")
            sauce = kat.get("sauce_preis", "0,80 €")
            streusel = kat.get("streusel_preis", "0,80 €")
            extras = f"Kugel Eis {kugel} · Portion Sahne {sahne} · Sauce extra {sauce} · Streusel extra {streusel}"
            praefix = kat.get("hinweis_praefix", "").strip()
            hinweis = f"{praefix} · {extras}" if praefix else extras
            zeilen.append(f'      hinweis: {_js_string(hinweis)},')
            zeilen.append(f'      extras: {_js_string(extras)},')

        mit_gruppe = any(item.get("gruppe") for item in kat.get("items", []))
        zeilen.append("      items: [")
        items = kat.get("items", [])
        for i, item in enumerate(items):
            komma = "," if i < len(items) - 1 else ""
            zeilen.append(f"        {_item_zeile_bauen(item, mit_gruppe)}{komma}")
        zeilen.append("      ]")
        schluss_komma = "," if idx < len(kategorien_liste) - 1 else ""
        zeilen.append(f"    }}{schluss_komma}")
        zeilen.append("")

    zeilen.append("  },")
    zeilen.append("")
    zeilen.append("  kuchen: [")
    kuchen = daten.get("kuchen", [])
    for i, k in enumerate(kuchen):
        komma = "," if i < len(kuchen) - 1 else ""
        preis_wert = "null" if not k.get("preis") else _js_string(k.get("preis"))
        zeilen.append(
            "    { emoji: %s, titel: %s, desc: %s, preis: %s }%s"
            % (_js_string(k.get("emoji", "")), _js_string(k.get("titel", "")),
               _js_string(k.get("desc", "")), preis_wert, komma)
        )
    zeilen.append("  ]")
    zeilen.append("")
    zeilen.append("};")
    zeilen.append("")
    return "\n".join(zeilen)


def daten_speichern(daten):
    if os.path.exists(CONFIG_DATEI):
        try:
            shutil.copyfile(CONFIG_DATEI, BACKUP_DATEI)
        except Exception:
            pass
    text = speisekarte_js_erzeugen(daten)
    with open(CONFIG_DATEI, "w", encoding="utf-8") as f:
        f.write(text)


def kategorie_schluessel_erzeugen(label, bestehende):
    ersatz = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
    text = label
    for a, b in ersatz.items():
        text = text.replace(a, b)
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    if not text:
        text = "kategorie"
    basis, n = text, 1
    while text in bestehende:
        n += 1
        text = f"{basis}_{n}"
    return text


# ---------------------------------------------------------------
# Optik: gleiche ruhige, dunkle Optik wie in der Zentrale
# ---------------------------------------------------------------
STYLE = """
QMainWindow { background-color: #1C1C1C; }
QWidget { color: #EDEDED; font-family: 'Segoe UI', sans-serif; font-size: 13px; }

QLabel#haupttitel { font-size: 22px; font-weight: 800; color: #FFFFFF; }
QLabel#untertitel { color: #A8A8A8; font-size: 12px; }
QLabel#hinweis { color: #A0A0A0; font-size: 12px; }

QGroupBox {
    background-color: #262626; border: 1px solid #3A3A3A; border-radius: 14px;
    margin-top: 20px; padding: 16px; font-size: 15px; font-weight: 800; color: #FFFFFF;
}
QGroupBox::title {
    subcontrol-origin: margin; left: 14px; top: -4px; padding: 2px 10px;
    color: #2DD4BF; background-color: #1C1C1C; border-radius: 6px;
}

QLineEdit {
    background-color: #313131; border: 1px solid #454545; border-radius: 8px;
    padding: 8px 10px; color: #FAFAFA; font-size: 13px;
    selection-background-color: #3B6BEF;
}

QPushButton {
    background-color: #3A3A3A; border: none; border-radius: 9px;
    padding: 9px 16px; color: #EDEDED; font-weight: 700; font-size: 12px;
}
QPushButton:hover { background-color: #464646; }
QPushButton:pressed { background-color: #2E2E2E; }
QPushButton#primary { background-color: #2DD4BF; color: #063B35; }
QPushButton#primary:hover { background-color: #48E0CC; }
QPushButton#gefahr { background-color: #7A2222; color: #FFD9D9; }
QPushButton#gefahr:hover { background-color: #922828; }

QTabWidget::pane { border: none; margin-top: 8px; }
QTabBar::tab {
    background: #2C2C2C; color: #C9C9C9; padding: 11px 20px;
    border-top-left-radius: 10px; border-top-right-radius: 10px;
    margin-right: 3px; font-size: 14px; font-weight: 700;
}
QTabBar::tab:selected { background: #3B6BEF; color: #FFFFFF; }

QTableWidget {
    background-color: #232323; border: 1px solid #3A3A3A; border-radius: 10px;
    gridline-color: #3A3A3A; selection-background-color: #2DD4BF33;
}
QHeaderView::section {
    background-color: #2C2C2C; color: #C9C9C9; padding: 8px; border: none;
    font-weight: 700; font-size: 12px;
}
QScrollArea { border: none; background: transparent; }
"""


# ---------------------------------------------------------------
# Ein Reiter für genau EINE Kategorie (Label + optionale Eis-Extras + Tabelle)
# ---------------------------------------------------------------
class KategorieReiter(QWidget):
    def __init__(self, schluessel, kategorie_daten, kugelpreis_getter):
        super().__init__()
        self.schluessel = schluessel
        self.kat = kategorie_daten
        self.kugelpreis_getter = kugelpreis_getter

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        kopf = QHBoxLayout()
        kopf.addWidget(QLabel("Anzeigename dieser Kategorie:"))
        self.label_feld = QLineEdit(self.kat.get("label", schluessel))
        kopf.addWidget(self.label_feld, stretch=1)
        layout.addLayout(kopf)

        if schluessel == "eis":
            eis_gruppe = QGroupBox("🍨  Hinweistext für Eisbecher (wird automatisch zusammengesetzt)")
            eis_layout = QGridLayout(eis_gruppe)
            eis_layout.addWidget(QLabel("Einleitungssatz:"), 0, 0)
            self.praefix_feld = QLineEdit(self.kat.get("hinweis_praefix", ""))
            eis_layout.addWidget(self.praefix_feld, 0, 1, 1, 3)

            eis_layout.addWidget(QLabel("Portion Sahne:"), 1, 0)
            self.sahne_feld = QLineEdit(self.kat.get("sahne_preis", ""))
            eis_layout.addWidget(self.sahne_feld, 1, 1)

            eis_layout.addWidget(QLabel("Sauce extra:"), 1, 2)
            self.sauce_feld = QLineEdit(self.kat.get("sauce_preis", ""))
            eis_layout.addWidget(self.sauce_feld, 1, 3)

            eis_layout.addWidget(QLabel("Streusel extra:"), 2, 0)
            self.streusel_feld = QLineEdit(self.kat.get("streusel_preis", ""))
            eis_layout.addWidget(self.streusel_feld, 2, 1)

            hinweis_info = QLabel(
                "Der Kugel-Preis kommt automatisch aus dem Reiter „Preise & Kugeleis“ - "
                "hier musst du ihn nicht noch einmal eintragen."
            )
            hinweis_info.setObjectName("hinweis")
            hinweis_info.setWordWrap(True)
            eis_layout.addWidget(hinweis_info, 3, 0, 1, 4)
            layout.addWidget(eis_gruppe)
        else:
            self.praefix_feld = self.sahne_feld = self.sauce_feld = self.streusel_feld = None

        self.tabelle = QTableWidget(0, len(SPALTEN))
        self.tabelle.setHorizontalHeaderLabels([s[1] for s in SPALTEN])
        self.tabelle.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabelle.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        for spalten_index, (_, _, breite) in enumerate(SPALTEN):
            if breite:
                self.tabelle.setColumnWidth(spalten_index, breite)
        self.tabelle.verticalHeader().setVisible(False)
        for item in self.kat.get("items", []):
            self._zeile_hinzufuegen(item)
        layout.addWidget(self.tabelle, stretch=1)

        knopf_zeile = QHBoxLayout()
        hinzufuegen_btn = QPushButton("➕  Position hinzufügen")
        hinzufuegen_btn.setObjectName("primary")
        hinzufuegen_btn.clicked.connect(lambda: self._zeile_hinzufuegen())
        entfernen_btn = QPushButton("🗑  Ausgewählte Position(en) entfernen")
        entfernen_btn.setObjectName("gefahr")
        entfernen_btn.clicked.connect(self._ausgewaehlte_entfernen)
        hoch_btn = QPushButton("⬆")
        hoch_btn.clicked.connect(lambda: self._verschieben(-1))
        runter_btn = QPushButton("⬇")
        runter_btn.clicked.connect(lambda: self._verschieben(1))
        knopf_zeile.addWidget(hinzufuegen_btn)
        knopf_zeile.addWidget(entfernen_btn)
        knopf_zeile.addStretch()
        knopf_zeile.addWidget(QLabel("Reihenfolge:"))
        knopf_zeile.addWidget(hoch_btn)
        knopf_zeile.addWidget(runter_btn)
        layout.addLayout(knopf_zeile)

    def _zeile_hinzufuegen(self, item=None):
        item = item or {}
        zeile = self.tabelle.rowCount()
        self.tabelle.insertRow(zeile)
        for spalte, (schluessel, _, _) in enumerate(SPALTEN):
            self.tabelle.setItem(zeile, spalte, QTableWidgetItem(str(item.get(schluessel, ""))))
        self.tabelle.scrollToBottom()

    def _ausgewaehlte_entfernen(self):
        zeilen = sorted({idx.row() for idx in self.tabelle.selectedIndexes()}, reverse=True)
        if not zeilen:
            QMessageBox.information(self, "Nichts ausgewählt", "Bitte zuerst eine oder mehrere Zeilen anklicken.")
            return
        for zeile in zeilen:
            self.tabelle.removeRow(zeile)

    def _verschieben(self, richtung):
        zeile = self.tabelle.currentRow()
        ziel = zeile + richtung
        if zeile < 0 or ziel < 0 or ziel >= self.tabelle.rowCount():
            return
        for spalte in range(self.tabelle.columnCount()):
            a = self.tabelle.takeItem(zeile, spalte)
            b = self.tabelle.takeItem(ziel, spalte)
            self.tabelle.setItem(zeile, spalte, b)
            self.tabelle.setItem(ziel, spalte, a)
        self.tabelle.setCurrentCell(ziel, 0)

    def daten_auslesen(self):
        items = []
        for zeile in range(self.tabelle.rowCount()):
            eintrag = {}
            for spalte, (schluessel, _, _) in enumerate(SPALTEN):
                zelle = self.tabelle.item(zeile, spalte)
                wert = zelle.text().strip() if zelle else ""
                if wert:
                    eintrag[schluessel] = wert
            if eintrag.get("name"):
                items.append(eintrag)
        ergebnis = {"label": self.label_feld.text().strip() or self.schluessel, "items": items}
        if self.schluessel == "eis":
            ergebnis["hinweis_praefix"] = self.praefix_feld.text().strip()
            ergebnis["sahne_preis"] = self.sahne_feld.text().strip()
            ergebnis["sauce_preis"] = self.sauce_feld.text().strip()
            ergebnis["streusel_preis"] = self.streusel_feld.text().strip()
        return ergebnis


# ---------------------------------------------------------------
# Reiter für die Kuchen-Kacheln (eigenes, einfacheres Layout)
# ---------------------------------------------------------------
KUCHEN_SPALTEN = [
    ("emoji", "Emoji", 70),
    ("titel", "Titel", None),
    ("desc", "Beschreibung", None),
    ("preis", "Preis (leer = kein fester Preis)", 220),
]


class KuchenReiter(QWidget):
    def __init__(self, kuchen_liste):
        super().__init__()
        layout = QVBoxLayout(self)
        info = QLabel(
            "Preis-Feld leer lassen, wenn es keinen festen Preis gibt (z.B. „siehe Auslage“ "
            "beim Tortenangebot)."
        )
        info.setObjectName("hinweis")
        layout.addWidget(info)

        self.tabelle = QTableWidget(0, len(KUCHEN_SPALTEN))
        self.tabelle.setHorizontalHeaderLabels([s[1] for s in KUCHEN_SPALTEN])
        self.tabelle.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabelle.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        for spalten_index, (_, _, breite) in enumerate(KUCHEN_SPALTEN):
            if breite:
                self.tabelle.setColumnWidth(spalten_index, breite)
        self.tabelle.verticalHeader().setVisible(False)
        for k in kuchen_liste:
            self._zeile_hinzufuegen(k)
        layout.addWidget(self.tabelle, stretch=1)

        knopf_zeile = QHBoxLayout()
        hinzufuegen_btn = QPushButton("➕  Kuchen-Kachel hinzufügen")
        hinzufuegen_btn.setObjectName("primary")
        hinzufuegen_btn.clicked.connect(lambda: self._zeile_hinzufuegen())
        entfernen_btn = QPushButton("🗑  Ausgewählte Kachel(n) entfernen")
        entfernen_btn.setObjectName("gefahr")
        entfernen_btn.clicked.connect(self._ausgewaehlte_entfernen)
        knopf_zeile.addWidget(hinzufuegen_btn)
        knopf_zeile.addWidget(entfernen_btn)
        knopf_zeile.addStretch()
        layout.addLayout(knopf_zeile)

    def _zeile_hinzufuegen(self, item=None):
        item = item or {}
        zeile = self.tabelle.rowCount()
        self.tabelle.insertRow(zeile)
        for spalte, (schluessel, _, _) in enumerate(KUCHEN_SPALTEN):
            wert = item.get(schluessel, "")
            self.tabelle.setItem(zeile, spalte, QTableWidgetItem("" if wert is None else str(wert)))

    def _ausgewaehlte_entfernen(self):
        zeilen = sorted({idx.row() for idx in self.tabelle.selectedIndexes()}, reverse=True)
        for zeile in zeilen:
            self.tabelle.removeRow(zeile)

    def daten_auslesen(self):
        ergebnis = []
        for zeile in range(self.tabelle.rowCount()):
            eintrag = {}
            for spalte, (schluessel, _, _) in enumerate(KUCHEN_SPALTEN):
                zelle = self.tabelle.item(zeile, spalte)
                eintrag[schluessel] = zelle.text().strip() if zelle else ""
            if eintrag.get("titel"):
                ergebnis.append(eintrag)
        return ergebnis


class HauptFenster(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speisekarte bearbeiten - Eiscafé Nico")
        self.resize(1200, 820)
        if os.path.exists(LOGO_ICO):
            self.setWindowIcon(QIcon(LOGO_ICO))
        elif os.path.exists(LOGO_PNG):
            self.setWindowIcon(QIcon(LOGO_PNG))

        self.daten = daten_laden()
        self.kategorie_reiter = {}

        zentral = QWidget()
        self.setCentralWidget(zentral)
        haupt = QVBoxLayout(zentral)
        haupt.setContentsMargins(22, 20, 22, 20)
        haupt.setSpacing(14)

        titel_zeile = QHBoxLayout()
        titel_block = QVBoxLayout()
        titel = QLabel("Speisekarte bearbeiten")
        titel.setObjectName("haupttitel")
        untertitel = QLabel("Preise, Namen & Positionen der Speisekarte - direkt in speisekarte-config.js")
        untertitel.setObjectName("untertitel")
        titel_block.addWidget(titel)
        titel_block.addWidget(untertitel)
        titel_zeile.addLayout(titel_block)
        titel_zeile.addStretch()
        speichern_btn = QPushButton("💾  Speichern")
        speichern_btn.setObjectName("primary")
        speichern_btn.setMinimumHeight(40)
        speichern_btn.clicked.connect(self.speichern)
        titel_zeile.addWidget(speichern_btn)
        haupt.addLayout(titel_zeile)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._preise_tab_bauen(), "💶  Preise & Kugeleis")
        self.tabs.addTab(self._kategorien_tab_bauen(), "🍽  Kategorien & Positionen")
        self.kuchen_reiter = KuchenReiter(self.daten.get("kuchen", []))
        self.tabs.addTab(self.kuchen_reiter, "🎂  Kuchen & Süßes")
        haupt.addWidget(self.tabs, stretch=1)

    # -------------------------------------------------------------
    def _preise_tab_bauen(self):
        seite = QWidget()
        layout = QVBoxLayout(seite)
        layout.setSpacing(14)

        gruppe = QGroupBox("💶  Zentrale Preise")
        grid = QGridLayout(gruppe)
        grid.addWidget(QLabel("Preis pro Kugel Eis (Badges + Hinweistext):"), 0, 0)
        self.kugelpreis_feld = QLineEdit(self.daten.get("kugelPreis", ""))
        grid.addWidget(self.kugelpreis_feld, 0, 1)

        grid.addWidget(QLabel("Eismobil - Preis:"), 1, 0)
        self.eismobil_preis_feld = QLineEdit(self.daten.get("eismobil", {}).get("preis", ""))
        grid.addWidget(self.eismobil_preis_feld, 1, 1)

        grid.addWidget(QLabel("Eismobil - Einheit:"), 2, 0)
        self.eismobil_einheit_feld = QLineEdit(self.daten.get("eismobil", {}).get("einheit", ""))
        grid.addWidget(self.eismobil_einheit_feld, 2, 1)

        layout.addWidget(gruppe)
        info = QLabel(
            "Der Kugel-Preis wird beim Speichern automatisch überall übernommen, wo er "
            "gebraucht wird (Werbe-Badges auf der Webseite UND der Hinweistext bei den "
            "Eisbechern) - du musst ihn nirgendwo sonst mehr eintragen."
        )
        info.setObjectName("hinweis")
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()
        return seite

    # -------------------------------------------------------------
    def _kategorien_tab_bauen(self):
        seite = QWidget()
        layout = QVBoxLayout(seite)
        layout.setSpacing(10)

        self.kategorien_tabs = QTabWidget()
        for schluessel, kat in self.daten.get("kategorien", {}).items():
            reiter = KategorieReiter(schluessel, kat, lambda: self.kugelpreis_feld.text())
            self.kategorie_reiter[schluessel] = reiter
            self.kategorien_tabs.addTab(reiter, kat.get("label", schluessel))
        layout.addWidget(self.kategorien_tabs, stretch=1)

        knopf_zeile = QHBoxLayout()
        neue_kategorie_btn = QPushButton("➕  Neue Kategorie hinzufügen")
        neue_kategorie_btn.setObjectName("primary")
        neue_kategorie_btn.clicked.connect(self._neue_kategorie)
        knopf_zeile.addWidget(neue_kategorie_btn)
        knopf_zeile.addStretch()
        layout.addLayout(knopf_zeile)
        return seite

    def _neue_kategorie(self):
        label, ok = QInputDialog.getText(self, "Neue Kategorie", "Name der neuen Kategorie (z.B. „Softeis“):")
        if not ok or not label.strip():
            return
        schluessel = kategorie_schluessel_erzeugen(label.strip(), self.kategorie_reiter.keys())
        reiter = KategorieReiter(schluessel, {"label": label.strip(), "items": []}, lambda: self.kugelpreis_feld.text())
        self.kategorie_reiter[schluessel] = reiter
        self.kategorien_tabs.addTab(reiter, label.strip())
        self.kategorien_tabs.setCurrentWidget(reiter)

    # -------------------------------------------------------------
    def speichern(self):
        neue_daten = {
            "kugelPreis": self.kugelpreis_feld.text().strip(),
            "eismobil": {
                "preis": self.eismobil_preis_feld.text().strip(),
                "einheit": self.eismobil_einheit_feld.text().strip(),
            },
            "kategorien": {schluessel: reiter.daten_auslesen() for schluessel, reiter in self.kategorie_reiter.items()},
            "kuchen": self.kuchen_reiter.daten_auslesen(),
        }
        try:
            daten_speichern(neue_daten)
        except Exception as e:
            QMessageBox.critical(self, "Fehler beim Speichern", str(e))
            return
        self.daten = neue_daten
        QMessageBox.information(
            self, "Gespeichert",
            "Die Speisekarte wurde in „speisekarte-config.js“ gespeichert.\n\n"
            "Jetzt nur noch wie gewohnt über die Zentrale bei der Webseiten-Kachel "
            "auf „Zum Hochladen öffnen“ klicken und die Datei per Drag & Drop hochladen."
        )


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Segoe UI", 10))
    if os.path.exists(LOGO_ICO):
        app.setWindowIcon(QIcon(LOGO_ICO))
    elif os.path.exists(LOGO_PNG):
        app.setWindowIcon(QIcon(LOGO_PNG))

    fenster = HauptFenster()
    bildschirm = app.primaryScreen().availableGeometry()
    breite, hoehe = fenster.width(), fenster.height()
    x = bildschirm.left() + max((bildschirm.width() - breite) // 2, 0)
    y = bildschirm.top() + max((bildschirm.height() - hoehe) // 2, 0)
    fenster.move(x, y)
    fenster.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
