// Formulaire de choix de la période : un mois et une année pour le début et pour la fin.
// Des listes déroulantes plutôt qu'un champ <input type="month"> : ce dernier n'existe pas
// dans Safari (macOS), qui affiche alors un champ texte libre sans format (anomalie #44).
// Le filtre ne lance une requête qu'au clic sur « Afficher ».

import { useState, type FormEvent } from 'react'
import type { Periode } from '../types/api'
import { ANNEES_DISPONIBLES, MOIS, versDatePeriode } from '../utilitaires/periode'
import styles from './FiltrePeriode.module.css'

interface Proprietes {
  onValider: (periode: Periode) => void
}

interface MoisAnnee {
  mois: string // "01" à "12", ou "" si non choisi
  annee: string // "1997", ou "" si non choisie
}

const NON_CHOISI: MoisAnnee = { mois: '', annee: '' }

export function FiltrePeriode({ onValider }: Proprietes) {
  const [debut, setDebut] = useState<MoisAnnee>(NON_CHOISI)
  const [fin, setFin] = useState<MoisAnnee>(NON_CHOISI)
  const [erreur, setErreur] = useState<string | null>(null)

  function valider(evenement: FormEvent<HTMLFormElement>) {
    evenement.preventDefault() // évite le rechargement de la page
    const dateDebut = versDatePeriode(debut.mois, debut.annee)
    const dateFin = versDatePeriode(fin.mois, fin.annee)

    if (dateDebut === null || dateFin === null) {
      const borne = dateDebut === null ? 'Début' : 'Fin'
      setErreur(`${borne} : choisissez le mois et l’année (ou aucun des deux).`)
      return
    }
    if (dateDebut !== '' && dateFin !== '' && dateDebut > dateFin) {
      setErreur('Le mois de début doit précéder le mois de fin.')
      return
    }
    setErreur(null)
    onValider({ debut: dateDebut, fin: dateFin })
  }

  function reinitialiser() {
    setDebut(NON_CHOISI)
    setFin(NON_CHOISI)
    setErreur(null)
    onValider({ debut: '', fin: '' })
  }

  return (
    <form className={styles.filtre} onSubmit={valider}>
      <p id="aide-periode" className={styles.aide}>
        Choisissez un mois et une année. Laissez « — » pour ne pas limiter la période de ce côté.
      </p>
      <ChoixMoisAnnee borne="début" valeur={debut} onChange={setDebut} />
      <ChoixMoisAnnee borne="fin" valeur={fin} onChange={setFin} />
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

interface ProprietesChoix {
  borne: 'début' | 'fin'
  valeur: MoisAnnee
  onChange: (valeur: MoisAnnee) => void
}

/** Un groupe « Début » ou « Fin » : liste des mois + liste des années. */
function ChoixMoisAnnee({ borne, valeur, onChange }: ProprietesChoix) {
  return (
    <fieldset className={styles.groupe} aria-describedby="aide-periode">
      <legend>{borne === 'début' ? 'Début' : 'Fin'}</legend>
      <label>
        {/* Nom accessible complet (« Mois de début ») : « Mois » seul serait ambigu. */}
        Mois<span className="visuellement-cache"> de {borne}</span>
        <select
          value={valeur.mois}
          onChange={(evenement) => onChange({ ...valeur, mois: evenement.target.value })}
        >
          <option value="">—</option>
          {MOIS.map((mois) => (
            <option key={mois.valeur} value={mois.valeur}>
              {mois.libelle}
            </option>
          ))}
        </select>
      </label>
      <label>
        Année<span className="visuellement-cache"> de {borne}</span>
        <select
          value={valeur.annee}
          onChange={(evenement) => onChange({ ...valeur, annee: evenement.target.value })}
        >
          <option value="">—</option>
          {ANNEES_DISPONIBLES.map((annee) => (
            <option key={annee} value={annee}>
              {annee}
            </option>
          ))}
        </select>
      </label>
    </fieldset>
  )
}
