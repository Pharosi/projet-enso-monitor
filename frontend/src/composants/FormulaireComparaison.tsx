// Choix des deux épisodes à comparer, parmi les épisodes de référence de l'API.

import { useState, type FormEvent } from 'react'
import type { EpisodeDeReference } from '../types/api'
import styles from './FiltrePeriode.module.css'

interface Proprietes {
  episodes: EpisodeDeReference[]
  identifiantAInitial: string
  identifiantBInitial: string
  onValider: (episodeA: EpisodeDeReference, episodeB: EpisodeDeReference) => void
}

export function FormulaireComparaison({
  episodes,
  identifiantAInitial,
  identifiantBInitial,
  onValider,
}: Proprietes) {
  const [identifiantA, setIdentifiantA] = useState(identifiantAInitial)
  const [identifiantB, setIdentifiantB] = useState(identifiantBInitial)
  const [erreur, setErreur] = useState<string | null>(null)

  function valider(evenement: FormEvent<HTMLFormElement>) {
    evenement.preventDefault()
    if (identifiantA === identifiantB) {
      setErreur('Choisissez deux épisodes différents.')
      return
    }
    const episodeA = episodes.find((episode) => episode.identifiant === identifiantA)
    const episodeB = episodes.find((episode) => episode.identifiant === identifiantB)
    if (!episodeA || !episodeB) return

    setErreur(null)
    onValider(episodeA, episodeB)
  }

  return (
    <form className={styles.filtre} onSubmit={valider}>
      <ChoixEpisode
        libelle="Épisode A"
        episodes={episodes}
        valeur={identifiantA}
        onChange={setIdentifiantA}
      />
      <ChoixEpisode
        libelle="Épisode B"
        episodes={episodes}
        valeur={identifiantB}
        onChange={setIdentifiantB}
      />
      <div className={styles.boutons}>
        <button type="submit">Comparer</button>
      </div>
      {erreur && (
        <p role="alert" className={styles.erreur}>
          {erreur}
        </p>
      )}
    </form>
  )
}

interface ProprietesChoix {
  libelle: string
  episodes: EpisodeDeReference[]
  valeur: string
  onChange: (identifiant: string) => void
}

function ChoixEpisode({ libelle, episodes, valeur, onChange }: ProprietesChoix) {
  return (
    <label>
      {libelle}
      <select value={valeur} onChange={(evenement) => onChange(evenement.target.value)}>
        {episodes.map((episode) => (
          <option key={episode.identifiant} value={episode.identifiant}>
            {episode.libelle}
          </option>
        ))}
      </select>
    </label>
  )
}
