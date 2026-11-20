// Test de non-régression de l'anomalie #36 : contraste des couleurs de l'interface.
//
// Les couleurs sont lues directement dans index.css (variables --couleur-…) : si
// quelqu'un change une couleur et passe sous le seuil WCAG, ce test échoue.
// Formule officielle WCAG 2.2 : https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio

/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

// Lecture du fichier sur le disque (un import CSS est vidé par Vitest pendant les tests).
// Chemin relatif au dossier frontend/, d'où les tests sont lancés (npm test).
const feuilleDeStyle = readFileSync('src/index.css', 'utf8')

/** Lit toutes les variables de couleur hexadécimales : { "couleur-texte": "#1b2631", … } */
function lireCouleurs(css: string): Record<string, string> {
  const couleurs: Record<string, string> = {}
  for (const [, nom, valeur] of css.matchAll(/--(couleur-[\w-]+):\s*(#[0-9a-fA-F]{6})/g)) {
    couleurs[nom] = valeur
  }
  return couleurs
}

/** Luminance relative d'une couleur (0 = noir, 1 = blanc), selon la définition WCAG. */
function luminance(couleurHex: string): number {
  const [rouge, vert, bleu] = [1, 3, 5].map((debut) => {
    const canal = parseInt(couleurHex.slice(debut, debut + 2), 16) / 255
    return canal <= 0.04045 ? canal / 12.92 : ((canal + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * rouge + 0.7152 * vert + 0.0722 * bleu
}

/** Rapport de contraste entre deux couleurs : de 1 (aucun contraste) à 21 (noir sur blanc). */
function contraste(couleurA: string, couleurB: string): number {
  const [claire, foncee] = [luminance(couleurA), luminance(couleurB)].sort((a, b) => b - a)
  return (claire + 0.05) / (foncee + 0.05)
}

const COULEURS = lireCouleurs(feuilleDeStyle)
const FONDS = ['couleur-fond', 'couleur-surface']

describe('Calcul du contraste', () => {
  it('donne 21:1 pour du noir sur du blanc (valeur de référence WCAG)', () => {
    expect(contraste('#000000', '#ffffff')).toBeCloseTo(21)
  })

  it('lit bien les couleurs de index.css (sinon les autres tests ne prouveraient rien)', () => {
    expect(Object.keys(COULEURS).length).toBeGreaterThanOrEqual(10)
    expect(COULEURS['couleur-focus']).toMatch(/^#[0-9a-fA-F]{6}$/)
  })
})

describe('Contrastes des couleurs de index.css', () => {
  // Anomalie #36 : le contour de focus mesurait 2,07:1 (WCAG 1.4.11 exige 3:1).
  it.each(FONDS)('le contour de focus est visible sur %s (≥ 3:1)', (fond) => {
    expect(contraste(COULEURS['couleur-focus'], COULEURS[fond])).toBeGreaterThanOrEqual(3)
  })

  it.each(
    ['couleur-texte', 'couleur-texte-secondaire', 'couleur-principale'].flatMap((texte) =>
      FONDS.map((fond) => [texte, fond]),
    ),
  )('le texte %s est lisible sur %s (≥ 4,5:1, WCAG 1.4.3)', (texte, fond) => {
    expect(contraste(COULEURS[texte], COULEURS[fond])).toBeGreaterThanOrEqual(4.5)
  })

  it('le message d’erreur est lisible sur son fond (≥ 4,5:1)', () => {
    const rapport = contraste(COULEURS['couleur-erreur-texte'], COULEURS['couleur-erreur-fond'])
    expect(rapport).toBeGreaterThanOrEqual(4.5)
  })

  it.each(['couleur-el-nino', 'couleur-la-nina', 'couleur-seuil'])(
    'les traits du graphique %s se distinguent du fond (≥ 3:1)',
    (trait) => {
      expect(contraste(COULEURS[trait], COULEURS['couleur-surface'])).toBeGreaterThanOrEqual(3)
    },
  )
})
