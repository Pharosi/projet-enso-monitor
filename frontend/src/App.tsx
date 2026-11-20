// Composant racine : la structure de la page (en-tête, contenu, pied de page).

import styles from './App.module.css'
import { SectionComparaison } from './composants/SectionComparaison'
import { SectionSerie } from './composants/SectionSerie'

export default function App() {
  return (
    <div className={styles.page}>
      <a className={styles.lienEvitement} href="#contenu">
        Aller au contenu
      </a>

      <header className={styles.entete}>
        <h1>ENSO Monitor</h1>
        <p>Explorer l'indice ONI de la NOAA et comparer des épisodes El Niño et La Niña.</p>
        <nav aria-label="Sections de la page" className={styles.navigation}>
          <a href="#titre-serie">Évolution de l'ONI</a>
          <a href="#titre-comparaison">Comparer deux épisodes</a>
        </nav>
      </header>

      <main id="contenu" className={styles.contenu}>
        <SectionSerie />
        <SectionComparaison />
      </main>

      <footer className={styles.pied}>
        <p>
          Données : NOAA Climate Prediction Center — indice ONI v6. Aucune prévision climatique
          n'est fournie.
        </p>
      </footer>
    </div>
  )
}
