// Provenance des données : indice, version, unité, source et date d'extraction.
// Exigence du sujet : « unités et source visibles ».

import type { Indice, Source } from '../types/api'
import { formaterDate } from '../utilitaires/format'
import styles from './SourceDonnees.module.css'

interface Proprietes {
  indice: Indice
  source: Source
}

export function SourceDonnees({ indice, source }: Proprietes) {
  return (
    <p className={styles.source}>
      {indice.nom} — {indice.version}, unité : {indice.unite}. Source :{' '}
      <a href={source.url} target="_blank" rel="noreferrer">
        {source.nom}
      </a>
      {source.derniere_extraction &&
        ` — données extraites le ${formaterDate(source.derniere_extraction)}`}
      .
    </p>
  )
}
