// Préparation des données pour superposer deux épisodes sur un même graphique.

import type { Observation } from '../types/api'

export interface PointCompare {
  rang: number // 1 = première saison de chaque période
  anomalieA: number | null
  anomalieB: number | null
  saisonA: string | null
  saisonB: string | null
}

/** Aligne les deux séries saison par saison : rang 1 avec rang 1, etc.
 *  Si une période est plus courte, ses valeurs manquantes valent null (ligne interrompue). */
export function fusionnerSeries(serieA: Observation[], serieB: Observation[]): PointCompare[] {
  const longueur = Math.max(serieA.length, serieB.length)
  return Array.from({ length: longueur }, (_, index) => ({
    rang: index + 1,
    anomalieA: serieA[index]?.anomalie ?? null,
    anomalieB: serieB[index]?.anomalie ?? null,
    saisonA: serieA[index] ? `${serieA[index].saison} ${serieA[index].annee}` : null,
    saisonB: serieB[index] ? `${serieB[index].saison} ${serieB[index].annee}` : null,
  }))
}
