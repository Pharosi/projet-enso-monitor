// Interprétation prudente rédigée par l'API, avec ses règles et ses limites.
// Exigence du sujet : expliquer les résultats ET leurs limites, indiquer seuils,
// durée et indice retenu.

import type { Comparaison } from '../types/api'
import styles from './Interpretation.module.css'

export function Interpretation({ comparaison }: { comparaison: Comparaison }) {
  const { regles } = comparaison
  return (
    <div className={styles.interpretation}>
      <h3>Interprétation</h3>
      <ul id="interpretation-comparaison">
        {comparaison.interpretation.map((phrase) => (
          <li key={phrase}>{phrase}</li>
        ))}
      </ul>

      <p className={styles.regles}>
        Règles appliquées : indice {regles.indice} ; épisode El Niño si l'ONI reste ≥ +
        {regles.seuil_el_nino.toLocaleString('fr-FR')} °C (La Niña : ≤{' '}
        {regles.seuil_la_nina.toLocaleString('fr-FR')} °C) pendant au moins{' '}
        {regles.duree_minimale_saisons} saisons consécutives (définition de la NOAA).
      </p>

      <h3>Limites de cette comparaison</h3>
      <ul className={styles.limites}>
        {comparaison.limites.map((limite) => (
          <li key={limite}>{limite}</li>
        ))}
      </ul>
    </div>
  )
}
