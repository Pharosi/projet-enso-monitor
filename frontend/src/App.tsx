// Composant racine : la structure de la page (en-tête, contenu, pied de page).
// Les sections (courbe ONI, comparaison) sont ajoutées dans les étapes suivantes.

import styles from './App.module.css'

export default function App() {
  return (
    <div className={styles.page}>
      <a className={styles.lienEvitement} href="#contenu">
        Aller au contenu
      </a>

      <header className={styles.entete}>
        <h1>ENSO Monitor</h1>
        <p>Explorer l'indice ONI de la NOAA et comparer des épisodes El Niño et La Niña.</p>
      </header>

      <main id="contenu" className={styles.contenu}>
        <p>Application en cours de construction.</p>
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
