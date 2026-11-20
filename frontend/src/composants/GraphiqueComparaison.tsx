// Superposition des deux épisodes, alignés saison par saison (rang 1, 2, 3…).
// Les deux courbes se distinguent par la couleur ET par le trait (plein / pointillé),
// pour rester lisibles sans percevoir les couleurs.

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { PointCompare } from '../utilitaires/comparaison'
import { formaterAnomalie, formaterGraduationValeur } from '../utilitaires/format'
import styles from './GraphiqueOni.module.css'

interface Proprietes {
  points: PointCompare[]
  libelleA: string
  libelleB: string
  idDescription: string
}

export function GraphiqueComparaison({ points, libelleA, libelleB, idDescription }: Proprietes) {
  return (
    <figure
      className={styles.figure}
      aria-labelledby="titre-graphique-comparaison"
      aria-describedby={idDescription}
    >
      <figcaption id="titre-graphique-comparaison" className={styles.legende}>
        Anomalie ONI (°C) saison par saison depuis le début de chaque période
      </figcaption>

      <div className={styles.zone}>
        {/* Taille utilisée avant la première mesure : évite un graphique vide au chargement. */}
        <ResponsiveContainer
          width="100%"
          height="100%"
          initialDimension={{ width: 800, height: 350 }}
        >
          <LineChart
            data={points}
            margin={{ top: 8, right: 16, bottom: 8, left: 0 }}
            title="Courbes superposées des deux épisodes : flèches gauche et droite pour parcourir"
          >
            <CartesianGrid strokeDasharray="3 3" stroke="var(--couleur-bordure)" />
            <XAxis dataKey="rang" tickFormatter={(rang: number) => `S${rang}`} />
            <YAxis tickFormatter={formaterGraduationValeur} width={70} domain={['auto', 'auto']} />
            <Tooltip
              labelFormatter={(rang) => `Saison n°${rang}`}
              formatter={(valeur, _nom, element) => {
                const point = element.payload as PointCompare
                const estA = element.dataKey === 'anomalieA'
                const saison = estA ? point.saisonA : point.saisonB
                return [
                  formaterAnomalie(Number(valeur)),
                  `${estA ? libelleA : libelleB} (${saison})`,
                ]
              }}
            />
            <ReferenceLine y={0.5} stroke="var(--couleur-seuil)" strokeDasharray="3 3" />
            <ReferenceLine y={-0.5} stroke="var(--couleur-seuil)" strokeDasharray="3 3" />
            <Line
              dataKey="anomalieA"
              name={libelleA}
              stroke="var(--couleur-principale)"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              dataKey="anomalieB"
              name={libelleB}
              stroke="var(--couleur-el-nino)"
              strokeWidth={2}
              strokeDasharray="8 4"
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <ul className={styles.legendeSymboles}>
        <li>
          <span className={styles.symboleCourbe} aria-hidden="true" /> A : {libelleA}
        </li>
        <li>
          <span className={styles.symboleCourbeB} aria-hidden="true" /> B : {libelleB}
        </li>
        <li>
          <span className={styles.symboleSeuils} aria-hidden="true" /> Seuils ±0,5 °C
        </li>
      </ul>
    </figure>
  )
}
