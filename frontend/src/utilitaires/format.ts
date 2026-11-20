// Fonctions de mise en forme à la française, partagées par tous les composants.

import type { Observation } from '../types/api'

const FORMAT_ANOMALIE = new Intl.NumberFormat('fr-FR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  signDisplay: 'exceptZero', // +2,37 / -1,47 / 0,00
})

/** 2.37 -> "+2,37 °C" */
export function formaterAnomalie(valeur: number): string {
  return `${FORMAT_ANOMALIE.format(valeur)} °C`
}

/** { saison: "NDJ", annee: 1997 } -> "NDJ 1997" */
export function libelleSaison(observation: Observation): string {
  return `${observation.saison} ${observation.annee}`
}

const FORMAT_MOIS = new Intl.DateTimeFormat('fr-FR', { month: 'short', year: 'numeric' })

/** Graduation de l'axe du temps : l'année pour une longue série, le mois pour une courte.
 *  "1997-07-01" -> "1997" (série longue) ou "juil. 1997" (série courte). */
export function formaterGraduationDate(dateIso: string, nombreDePoints: number): string {
  if (nombreDePoints > 36) return dateIso.slice(0, 4)
  return FORMAT_MOIS.format(new Date(`${dateIso}T00:00:00`))
}

/** 2.4 -> "2,4 °C" (graduation de l'axe des valeurs). */
export function formaterGraduationValeur(valeur: number): string {
  return `${valeur.toLocaleString('fr-FR')} °C`
}

/** "2026-11-19T12:16:29Z" -> "19/11/2026" */
export function formaterDate(dateIso: string): string {
  return new Date(dateIso).toLocaleDateString('fr-FR')
}

/** Valeur d'un champ <input type="month"> ("1998-01") -> date de période ("1998-01-01"). */
export function moisVersDate(mois: string): string {
  return mois === '' ? '' : `${mois}-01`
}
