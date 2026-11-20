// Formulaire de choix de la période : deux mois (début, fin), appliqués à la validation.
// Le filtre ne lance une requête qu'au clic sur « Afficher », pas à chaque frappe.

import { useState, type FormEvent } from 'react'
import type { Periode } from '../types/api'
import { moisVersDate } from '../utilitaires/format'
import styles from './FiltrePeriode.module.css'

interface Proprietes {
  onValider: (periode: Periode) => void
}

export function FiltrePeriode({ onValider }: Proprietes) {
  const [moisDebut, setMoisDebut] = useState('')
  const [moisFin, setMoisFin] = useState('')
  const [erreur, setErreur] = useState<string | null>(null)

  function valider(evenement: FormEvent<HTMLFormElement>) {
    evenement.preventDefault() // évite le rechargement de la page
    if (moisDebut !== '' && moisFin !== '' && moisDebut > moisFin) {
      setErreur('Le mois de début doit précéder le mois de fin.')
      return
    }
    setErreur(null)
    onValider({ debut: moisVersDate(moisDebut), fin: moisVersDate(moisFin) })
  }

  function reinitialiser() {
    setMoisDebut('')
    setMoisFin('')
    setErreur(null)
    onValider({ debut: '', fin: '' })
  }

  return (
    <form className={styles.filtre} onSubmit={valider}>
      <p id="aide-periode" className={styles.aide}>
        Laisser un champ vide pour ne pas limiter la période de ce côté.
      </p>
      <label>
        Début
        <input
          type="month"
          min="1950-01"
          aria-describedby="aide-periode"
          value={moisDebut}
          onChange={(evenement) => setMoisDebut(evenement.target.value)}
        />
      </label>
      <label>
        Fin
        <input
          type="month"
          min="1950-01"
          aria-describedby="aide-periode"
          value={moisFin}
          onChange={(evenement) => setMoisFin(evenement.target.value)}
        />
      </label>
      <div className={styles.boutons}>
        <button type="submit">Afficher</button>
        <button type="button" onClick={reinitialiser}>
          Toute la série
        </button>
      </div>
      {erreur && (
        <p role="alert" className={styles.erreur}>
          {erreur}
        </p>
      )}
    </form>
  )
}
