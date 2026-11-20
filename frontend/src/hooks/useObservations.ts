// Hook : la série ONI de la période choisie (chargement, erreur ou données).

import { recupererObservations } from '../services/api'
import type { Periode, SerieObservations } from '../types/api'
import { useDonneesApi, type EtatChargement } from './useDonneesApi'

export function useObservations(periode: Periode): EtatChargement<SerieObservations> {
  return useDonneesApi(periode, recupererObservations)
}
