// Tableau des indicateurs calculés par l'API pour chaque période.

import type { AnalysePeriode } from '../types/api'
import { formaterAnomalie, libelleSaison } from '../utilitaires/format'
import styles from './TableauObservations.module.css'

interface Proprietes {
  analyseA: AnalysePeriode
  analyseB: AnalysePeriode
  libelleA: string
  libelleB: string
}

function ouiNon(valeur: boolean): string {
  return valeur ? 'Oui' : 'Non'
}

// Chaque ligne : un intitulé et la façon de lire la valeur dans une analyse.
const LIGNES: { intitule: string; valeur: (analyse: AnalysePeriode) => string }[] = [
  { intitule: 'Saisons analysées', valeur: (a) => String(a.nombre_de_saisons) },
  {
    intitule: 'Pic (maximum)',
    valeur: (a) => `${formaterAnomalie(a.pic.anomalie)} — ${libelleSaison(a.pic)}`,
  },
  {
    intitule: 'Creux (minimum)',
    valeur: (a) => `${formaterAnomalie(a.creux.anomalie)} — ${libelleSaison(a.creux)}`,
  },
  { intitule: 'Anomalie moyenne', valeur: (a) => formaterAnomalie(a.anomalie_moyenne) },
  {
    intitule: 'Saisons consécutives ≥ +0,5 °C',
    valeur: (a) => String(a.saisons_el_nino_consecutives),
  },
  { intitule: 'Épisode El Niño (règle NOAA)', valeur: (a) => ouiNon(a.episode_el_nino) },
  { intitule: 'Intensité du pic (convention)', valeur: (a) => a.intensite_du_pic ?? '—' },
  {
    intitule: 'Saisons consécutives ≤ −0,5 °C',
    valeur: (a) => String(a.saisons_la_nina_consecutives),
  },
  { intitule: 'Épisode La Niña (règle NOAA)', valeur: (a) => ouiNon(a.episode_la_nina) },
]

export function TableauComparaison({ analyseA, analyseB, libelleA, libelleB }: Proprietes) {
  return (
    <div className={styles.defilement}>
      <table className={styles.tableau}>
        <caption>Indicateurs calculés sur l'indice ONI pour chaque période</caption>
        <thead>
          <tr>
            <th scope="col">Indicateur</th>
            <th scope="col">A : {libelleA}</th>
            <th scope="col">B : {libelleB}</th>
          </tr>
        </thead>
        <tbody>
          {LIGNES.map((ligne) => (
            <tr key={ligne.intitule}>
              <th scope="row">{ligne.intitule}</th>
              <td>{ligne.valeur(analyseA)}</td>
              <td>{ligne.valeur(analyseB)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
