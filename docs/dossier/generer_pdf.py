"""Génère le PDF du dossier de conception à partir de dossier.html.

Chrome (mode headless) imprime la page HTML en PDF A4 : la mise en page, la pagination
et les diagrammes Mermaid sont gérés par le navigateur.

Deux passes, car le navigateur ne sait pas écrire les numéros de page dans un sommaire :
  1. impression d'une première version ;
  2. recherche de la page de chaque titre de section (pypdf), insertion des numéros
     dans le sommaire, puis impression définitive.

Usage (depuis la racine du dépôt) :
    python3 -m venv docs/dossier/.venv && docs/dossier/.venv/bin/pip install pypdf
    docs/dossier/.venv/bin/python docs/dossier/generer_pdf.py
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

DOSSIER = Path(__file__).resolve().parent
SOURCE_HTML = DOSSIER / "dossier.html"
PDF_FINAL = DOSSIER / "PAES RODRIGUES DA SILVA - Raphael - BC03 - Dossier de conception.pdf"
CHROME = os.environ.get(
    "CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)
PAGES_MAXIMUM = 15


def imprimer(html: Path, pdf: Path) -> None:
    """Imprime le HTML en PDF ; le délai laisse à Mermaid le temps de dessiner les diagrammes."""
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=30000",
            f"--print-to-pdf={pdf}",
            html.as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def normaliser(texte: str) -> str:
    return re.sub(r"\s+", " ", texte).strip().lower()


def trouver_pages(pdf: Path, titres: list[str]) -> dict[str, int]:
    """Numéro de la première page (après le sommaire) où apparaît chaque titre."""
    pages = [normaliser(page.extract_text() or "") for page in PdfReader(pdf).pages]
    resultat = {}
    for titre in titres:
        cible = normaliser(titre)
        # Les pages 1 (couverture) et 2 (sommaire) sont ignorées : le sommaire cite tous les titres.
        numero = next((i + 1 for i, texte in enumerate(pages) if i >= 2 and cible in texte), None)
        if numero is None:
            sys.exit(f"Titre introuvable dans le PDF : « {titre} »")
        resultat[titre] = numero
    return resultat


def inserer_numeros(html: str, pages: dict[str, int]) -> str:
    """Remplace chaque <span class="num" data-titre="…"></span> par son numéro de page."""

    def remplacer(correspondance: re.Match) -> str:
        titre = correspondance.group(1)
        return f'<span class="num" data-titre="{titre}">{pages[titre]}</span>'

    return re.sub(r'<span class="num" data-titre="([^"]+)"></span>', remplacer, html)


def ajouter_metadonnees(pdf: Path) -> None:
    lecteur = PdfReader(pdf)
    ecrivain = PdfWriter(clone_from=lecteur)
    ecrivain.add_metadata(
        {
            "/Title": "ENSO Monitor — Dossier de conception",
            "/Author": "Raphael PAES RODRIGUES DA SILVA",
            "/Subject": "RNCP 36146 — BC03 — Sujet de rattrapage HETIC WEB3",
        }
    )
    with pdf.open("wb") as fichier:
        ecrivain.write(fichier)


def main() -> None:
    html = SOURCE_HTML.read_text(encoding="utf-8")
    titres = re.findall(r'<span class="num" data-titre="([^"]+)"></span>', html)

    with tempfile.TemporaryDirectory() as temporaire:
        brouillon = Path(temporaire) / "brouillon.pdf"
        imprimer(SOURCE_HTML, brouillon)
        pages = trouver_pages(brouillon, titres)

    # La version numérotée est écrite à côté de la source (les chemins relatifs restent valides).
    html_numerote = DOSSIER / ".dossier-numerote.html"
    html_numerote.write_text(inserer_numeros(html, pages), encoding="utf-8")
    try:
        imprimer(html_numerote, PDF_FINAL)
    finally:
        html_numerote.unlink()
    ajouter_metadonnees(PDF_FINAL)

    nombre = len(PdfReader(PDF_FINAL).pages)
    for titre, page in pages.items():
        print(f"  p. {page:>2}  {titre}")
    print(f"PDF : {PDF_FINAL.name} — {nombre} pages (maximum {PAGES_MAXIMUM})")
    if nombre > PAGES_MAXIMUM:
        sys.exit("Le dossier dépasse la limite de pages du sujet.")


if __name__ == "__main__":
    main()
