// Section « Comparer deux épisodes ».
// Deux composants, deux responsabilités :
// - SectionComparaison charge la liste des épisodes proposés ;
// - ComparaisonEpisodes, affiché une fois la liste disponible, gère le choix et le résultat.

import { useState } from 'react'
import { useComparaison, type DeuxPeriodes } from '../hooks/useComparaison'
import { useEpisodesDeReference } from '../hooks/useEpisodesDeReference'
import type { EpisodeDeReference } from '../types/api'
import { fusionnerSeries } from '../utilitaires/comparaison'
import { FormulaireComparaison } from './FormulaireComparaison'
import { GraphiqueComparaison } from './GraphiqueComparaison'
import { Interpretation } from './Interpretation'
import { MessageErreur } from './MessageErreur'
import { TableauComparaison } from './TableauComparaison'
import styles from './Section.module.css'

// Comparaison affichée à l'ouverture : les deux El Niño les plus intenses de la série.
const IDENTIFIANT_A_INITIAL = 'el-nino-1997-1998'
const IDENTIFIANT_B_INITIAL = 'el-nino-2015-2016'

export function SectionComparaison() {
  const { donnees: episodes, chargement, erreur } = useEpisodesDeReference()

  return (
    <section className={styles.section} aria-labelledby="titre-comparaison">
      <h2 id="titre-comparaison">Comparer deux épisodes</h2>
      {chargement && <p>Chargement des épisodes…</p>}
      {erreur && <MessageErreur message={erreur} />}
      {episodes && episodes.length >= 2 && <ComparaisonEpisodes episodes={episodes} />}
    </section>
  )
}

interface ChoixEpisodes {
  a: EpisodeDeReference
  b: EpisodeDeReference
  periodes: DeuxPeriodes // objet stable : ne change qu'à la validation du formulaire
}

function choisir(a: EpisodeDeReference, b: EpisodeDeReference): ChoixEpisodes {
  return {
    a,
    b,
    periodes: { a: { debut: a.debut, fin: a.fin }, b: { debut: b.debut, fin: b.fin } },
  }
}

function choixInitial(episodes: EpisodeDeReference[]): ChoixEpisodes {
  const trouver = (identifiant: string) => episodes.find((e) => e.identifiant === identifiant)
  return choisir(
    trouver(IDENTIFIANT_A_INITIAL) ?? episodes[0],
    trouver(IDENTIFIANT_B_INITIAL) ?? episodes[1],
  )
}

function ComparaisonEpisodes({ episodes }: { episodes: EpisodeDeReference[] }) {
  // Fonction d'initialisation : calculée une seule fois, au premier affichage.
  const [choix, setChoix] = useState(() => choixInitial(episodes))
  const { donnees: comparaison, chargement, erreur } = useComparaison(choix.periodes)

  return (
    <>
      <FormulaireComparaison
        episodes={episodes}
        identifiantAInitial={choix.a.identifiant}
        identifiantBInitial={choix.b.identifiant}
        onValider={(a, b) => setChoix(choisir(a, b))}
      />

      <div aria-live="polite" aria-busy={chargement}>
        {chargement && <p>Calcul de la comparaison…</p>}
        {erreur && <MessageErreur message={erreur} />}
        {comparaison && !chargement && (
          <p className={styles.resume}>
            Comparaison de {choix.a.libelle} (A) et de {choix.b.libelle} (B).
          </p>
        )}
      </div>

      {comparaison && (
        <>
          <GraphiqueComparaison
            points={fusionnerSeries(
              comparaison.periode_a.observations,
              comparaison.periode_b.observations,
            )}
            libelleA={choix.a.libelle}
            libelleB={choix.b.libelle}
            idDescription="interpretation-comparaison"
          />
          <TableauComparaison
            analyseA={comparaison.periode_a}
            analyseB={comparaison.periode_b}
            libelleA={choix.a.libelle}
            libelleB={choix.b.libelle}
          />
          <Interpretation comparaison={comparaison} />
        </>
      )}
    </>
  )
}
