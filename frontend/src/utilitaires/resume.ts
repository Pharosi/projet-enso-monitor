// Résumé textuel d'une série : affiché à l'écran et lu par les lecteurs d'écran
// (alternative au graphique pour les personnes qui ne le voient pas).

import type { Observation } from '../types/api'
import { formaterAnomalie, libelleSaison } from './format'

export function resumerSerie(observations: Observation[]): string {
  if (observations.length === 0) return 'Aucune observation sur cette période.'

  const premiere = observations[0]
  const derniere = observations[observations.length - 1]
  const pic = observations.reduce((max, o) => (o.anomalie > max.anomalie ? o : max))
  const creux = observations.reduce((min, o) => (o.anomalie < min.anomalie ? o : min))

  return (
    `${observations.length} saisons, de ${libelleSaison(premiere)} à ${libelleSaison(derniere)}. ` +
    `Maximum ${formaterAnomalie(pic.anomalie)} (${libelleSaison(pic)}), ` +
    `minimum ${formaterAnomalie(creux.anomalie)} (${libelleSaison(creux)}).`
  )
}
