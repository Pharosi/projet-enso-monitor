// Section « Évolution de l'ONI » : relie le filtre, le chargement et l'affichage.
// C'est le seul composant de la section qui détient un état (la période choisie) ;
// les autres reçoivent leurs données en propriétés et se contentent d'afficher.

import { useState } from 'react'
import { useObservations } from '../hooks/useObservations'
import type { Periode } from '../types/api'
import { resumerSerie } from '../utilitaires/resume'
import { FiltrePeriode } from './FiltrePeriode'
import { GraphiqueOni } from './GraphiqueOni'
import { MessageErreur } from './MessageErreur'
import { SourceDonnees } from './SourceDonnees'
import { TableauObservations } from './TableauObservations'
import styles from './Section.module.css'

const TOUTE_LA_SERIE: Periode = { debut: '', fin: '' }

export function SectionSerie() {
  const [periode, setPeriode] = useState<Periode>(TOUTE_LA_SERIE)
  const { donnees, chargement, erreur } = useObservations(periode)

  return (
    <section className={styles.section} aria-labelledby="titre-serie">
      <h2 id="titre-serie">Évolution de l'indice ONI</h2>
      <FiltrePeriode onValider={setPeriode} />

      {/* aria-live : les lecteurs d'écran annoncent le nouveau résumé après chaque filtre. */}
      <div aria-live="polite" aria-busy={chargement}>
        {chargement && <p>Chargement des observations…</p>}
        {erreur && <MessageErreur message={erreur} />}
        {donnees && !chargement && (
          <p id="resume-serie" className={styles.resume}>
            {resumerSerie(donnees.observations)}
          </p>
        )}
      </div>

      {donnees && donnees.observations.length > 0 && (
        <>
          <GraphiqueOni
            observations={donnees.observations}
            unite={donnees.indice.unite}
            idDescription="resume-serie"
          />
          <TableauObservations
            observations={donnees.observations}
            titre={`Valeurs de l'indice ${donnees.indice.code} (${donnees.indice.unite})`}
          />
          <SourceDonnees indice={donnees.indice} source={donnees.source} />
        </>
      )}
    </section>
  )
}
