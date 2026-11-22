// Anomalie #46 : sur une période courte, l'axe du temps répétait la même année.
// Chaque graduation doit porter une étiquette unique, quelle que soit la période.

import { describe, expect, it } from 'vitest'
import { choisirGraduationsDates, formaterGraduationDate } from '../utilitaires/format'

/** Dates de période mensuelles consécutives : ('1985-01', 3) -> 1985-01-01, 1985-02-01, 1985-03-01 */
function moisConsecutifs(debut: string, nombre: number): string[] {
  const [annee, mois] = debut.split('-').map(Number)
  return Array.from({ length: nombre }, (_, i) => {
    const total = annee * 12 + (mois - 1) + i
    const m = String((total % 12) + 1).padStart(2, '0')
    return `${Math.floor(total / 12)}-${m}-01`
  })
}

function etiquettes(dates: string[], graduations: string[]): string[] {
  return graduations.map((date) => formaterGraduationDate(date, dates.length))
}

describe('choisirGraduationsDates', () => {
  it('place une graduation par année sur une période de quatre ans, sans répétition', () => {
    const dates = moisConsecutifs('1985-01', 48)
    const graduations = choisirGraduationsDates(dates)

    expect(graduations).toEqual(['1985-01-01', '1986-01-01', '1987-01-01', '1988-01-01'])
    expect(etiquettes(dates, graduations ?? [])).toEqual(['1985', '1986', '1987', '1988'])
  })

  it('espace les graduations de dix ans sur la série complète 1950-2026', () => {
    const dates = moisConsecutifs('1950-01', 921)
    const graduations = choisirGraduationsDates(dates) ?? []

    expect(etiquettes(dates, graduations)).toEqual([
      '1950',
      '1960',
      '1970',
      '1980',
      '1990',
      '2000',
      '2010',
      '2020',
    ])
  })

  it('laisse le graphique choisir sur une période courte (étiquettes mois et année)', () => {
    const dates = moisConsecutifs('1997-01', 24)

    expect(choisirGraduationsDates(dates)).toBeUndefined()
  })
})
