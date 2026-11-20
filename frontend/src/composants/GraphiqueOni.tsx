// Courbe temporelle de l'ONI (Recharts), avec les seuils El Niño / La Niña.
// Accessibilité : la figure a un titre et pointe vers le résumé textuel affiché au-dessus
// (aria-describedby, sans dupliquer le texte) ; Recharts active
// la navigation au clavier dans le graphique (flèches gauche/droite) ; un tableau
// de données équivalent est proposé à côté (TableauObservations).

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
import type { Observation } from '../types/api'
import {
  formaterAnomalie,
  formaterGraduationDate,
  formaterGraduationValeur,
  libelleSaison,
} from '../utilitaires/format'
import styles from './GraphiqueOni.module.css'

interface Proprietes {
  observations: Observation[]
  unite: string
  idDescription: string // id de l'élément qui résume la courbe en texte
}

const SEUIL_EL_NINO = 0.5
const SEUIL_LA_NINA = -0.5

export function GraphiqueOni({ observations, unite, idDescription }: Proprietes) {
  return (
    <figure
      className={styles.figure}
      aria-labelledby="titre-graphique"
      aria-describedby={idDescription}
    >
      <figcaption id="titre-graphique" className={styles.legende}>
        Indice ONI ({unite}) par saison glissante de trois mois
      </figcaption>

      <div className={styles.zone}>
        {/* Taille utilisée avant la première mesure : évite un graphique vide au chargement. */}
        <ResponsiveContainer
          width="100%"
          height="100%"
          initialDimension={{ width: 800, height: 350 }}
        >
          <LineChart
            data={observations}
            margin={{ top: 8, right: 16, bottom: 8, left: 0 }}
            title="Courbe de l'indice ONI : flèches gauche et droite pour parcourir les valeurs"
          >
            <CartesianGrid strokeDasharray="3 3" stroke="var(--couleur-bordure)" />
            <XAxis
              dataKey="date_periode"
              tickFormatter={(date: string) => formaterGraduationDate(date, observations.length)}
              minTickGap={24}
            />
            <YAxis tickFormatter={formaterGraduationValeur} width={70} domain={['auto', 'auto']} />
            <Tooltip
              labelFormatter={(_, elements) =>
                elements[0] ? libelleSaison(elements[0].payload as Observation) : ''
              }
              formatter={(valeur) => [formaterAnomalie(Number(valeur)), 'ONI']}
            />
            <ReferenceLine
              y={SEUIL_EL_NINO}
              stroke="var(--couleur-el-nino)"
              strokeDasharray="6 4"
            />
            <ReferenceLine
              y={SEUIL_LA_NINA}
              stroke="var(--couleur-la-nina)"
              strokeDasharray="6 4"
            />
            <Line
              type="monotone"
              dataKey="anomalie"
              name="Anomalie ONI"
              stroke="var(--couleur-principale)"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Légende en HTML : lisible sur mobile et lue par les lecteurs d'écran. */}
      <ul className={styles.legendeSymboles}>
        <li>
          <span className={styles.symboleCourbe} aria-hidden="true" /> Anomalie ONI
        </li>
        <li>
          <span className={styles.symboleElNino} aria-hidden="true" /> Seuil El Niño (+0,5 °C)
        </li>
        <li>
          <span className={styles.symboleLaNina} aria-hidden="true" /> Seuil La Niña (−0,5 °C)
        </li>
      </ul>
    </figure>
  )
}
