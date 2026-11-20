// Hook : la liste des épisodes proposés dans le formulaire de comparaison.

import { recupererEpisodesDeReference } from '../services/api'
import type { EpisodeDeReference } from '../types/api'
import { useDonneesApi, type EtatChargement } from './useDonneesApi'

// Objet constant : la liste n'est chargée qu'une fois (les paramètres ne changent jamais).
const SANS_PARAMETRES = {}

export function useEpisodesDeReference(): EtatChargement<EpisodeDeReference[]> {
  return useDonneesApi(SANS_PARAMETRES, recupererEpisodesDeReference)
}
