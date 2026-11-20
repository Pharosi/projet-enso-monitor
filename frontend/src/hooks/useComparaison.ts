// Hook : la comparaison des deux périodes choisies.

import { comparerPeriodes } from '../services/api'
import type { Comparaison, Periode } from '../types/api'
import { useDonneesApi, type EtatChargement } from './useDonneesApi'

export interface DeuxPeriodes {
  a: Periode
  b: Periode
}

function comparer({ a, b }: DeuxPeriodes): Promise<Comparaison> {
  return comparerPeriodes(a, b)
}

export function useComparaison(periodes: DeuxPeriodes): EtatChargement<Comparaison> {
  return useDonneesApi(periodes, comparer)
}
