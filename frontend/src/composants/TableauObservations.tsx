// Alternative textuelle au graphique : le tableau des valeurs, replié par défaut.
// Indispensable pour les lecteurs d'écran et pour vérifier une valeur précise.

import type { Observation } from '../types/api'
import { formaterAnomalie, libelleSaison } from '../utilitaires/format'
import styles from './TableauObservations.module.css'

interface Proprietes {
  observations: Observation[]
  titre: string
}

export function TableauObservations({ observations, titre }: Proprietes) {
  return (
    <details className={styles.details}>
      <summary>Afficher les données sous forme de tableau ({observations.length} lignes)</summary>
      <div className={styles.defilement}>
        <table className={styles.tableau}>
          <caption>{titre}</caption>
          <thead>
            <tr>
              <th scope="col">Saison</th>
              <th scope="col">Anomalie ONI</th>
              <th scope="col">Température moyenne</th>
            </tr>
          </thead>
          <tbody>
            {observations.map((observation) => (
              <tr key={observation.date_periode}>
                <th scope="row">{libelleSaison(observation)}</th>
                <td>{formaterAnomalie(observation.anomalie)}</td>
                <td>{observation.temperature_totale.toLocaleString('fr-FR')} °C</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  )
}
