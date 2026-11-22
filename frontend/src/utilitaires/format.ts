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

const MAXIMUM_GRADUATIONS = 10
const PAS_EN_ANNEES = [1, 2, 5, 10, 20]

/** Graduations de l'axe du temps pour une série longue : une par mois de janvier,
 *  espacées d'un pas « rond » (1, 2, 5, 10 ou 20 ans) pour ne pas dépasser dix étiquettes.
 *  Chaque étiquette (l'année) est ainsi unique. Série courte : undefined, le graphique
 *  choisit lui-même (étiquettes « mois année », déjà uniques). */
export function choisirGraduationsDates(dates: string[]): string[] | undefined {
  if (dates.length <= 36) return undefined
  const janviers = dates.filter((date) => date.slice(5, 7) === '01')
  const pas = PAS_EN_ANNEES.find((valeur) => janviers.length / valeur <= MAXIMUM_GRADUATIONS) ?? 50
  if (pas === 1) return janviers
  return janviers.filter((date) => Number(date.slice(0, 4)) % pas === 0)
}

/** 2.4 -> "2,4 °C" (graduation de l'axe des valeurs). */
export function formaterGraduationValeur(valeur: number): string {
  return `${valeur.toLocaleString('fr-FR')} °C`
}

/** "2026-11-19T12:16:29Z" -> "19/11/2026" */
export function formaterDate(dateIso: string): string {
  return new Date(dateIso).toLocaleDateString('fr-FR')
}
