// Audit d'accessibilité automatisé de la page complète avec axe-core
// (moteur utilisé par les outils d'audit des navigateurs).
// Limite : jsdom ne calcule pas les couleurs affichées, la règle de contraste est donc
// vérifiée séparément (test des contrastes et mesure dans le navigateur).

import { render, screen } from '@testing-library/react'
import axe from 'axe-core'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../App'
import {
  comparerPeriodes,
  recupererEpisodesDeReference,
  recupererObservations,
} from '../services/api'
import type { Observation } from '../types/api'

vi.mock('../services/api')

const OBSERVATIONS: Observation[] = [
  {
    saison: 'DJF',
    annee: 1998,
    date_periode: '1998-01-01',
    anomalie: 2.22,
    temperature_totale: 28.85,
  },
  {
    saison: 'JFM',
    annee: 1998,
    date_periode: '1998-02-01',
    anomalie: 1.91,
    temperature_totale: 28.6,
  },
]

function analyse() {
  return {
    debut: '1997-01-01',
    fin: '1998-06-01',
    nombre_de_saisons: 2,
    pic: OBSERVATIONS[0],
    creux: OBSERVATIONS[1],
    anomalie_moyenne: 2.07,
    saisons_el_nino_consecutives: 2,
    saisons_la_nina_consecutives: 0,
    episode_el_nino: false,
    episode_la_nina: false,
    intensite_du_pic: null,
    observations: OBSERVATIONS,
  }
}

describe('Accessibilité de la page', () => {
  beforeEach(() => {
    vi.mocked(recupererObservations).mockResolvedValue({
      indice: { code: 'ONI', nom: 'Oceanic Niño Index', unite: '°C', version: 'ONI v6' },
      source: { nom: 'NOAA CPC', url: 'https://www.cpc.ncep.noaa.gov/', derniere_extraction: null },
      debut: null,
      fin: null,
      nombre: 2,
      observations: OBSERVATIONS,
    })
    vi.mocked(recupererEpisodesDeReference).mockResolvedValue([
      {
        identifiant: 'el-nino-1997-1998',
        libelle: 'El Niño 1997-1998',
        debut: '1997-01-01',
        fin: '1998-06-01',
        en_cours: false,
      },
      {
        identifiant: 'el-nino-2015-2016',
        libelle: 'El Niño 2015-2016',
        debut: '2015-01-01',
        fin: '2016-06-01',
        en_cours: false,
      },
    ])
    vi.mocked(comparerPeriodes).mockResolvedValue({
      periode_a: analyse(),
      periode_b: analyse(),
      regles: {
        indice: 'ONI v6',
        seuil_el_nino: 0.5,
        seuil_la_nina: -0.5,
        duree_minimale_saisons: 5,
        categories_intensite: {},
      },
      interpretation: ['Phrase.'],
      limites: ['Limite.'],
    })
  })

  it('ne présente aucune violation détectée par axe-core', async () => {
    const { container } = render(<App />)
    await screen.findByText('Phrase.') // attendre que toute la page soit chargée

    const resultat = await axe.run(container, { rules: { 'color-contrast': { enabled: false } } })

    const violations = resultat.violations.map((v) => `${v.id} : ${v.help}`)
    expect(violations).toEqual([])
  })

  it('propose une structure navigable : titres, navigation et lien d’évitement', async () => {
    render(<App />)
    await screen.findByText('Phrase.')

    expect(screen.getByRole('heading', { level: 1, name: 'ENSO Monitor' })).toBeInTheDocument()
    expect(screen.getAllByRole('heading', { level: 2 })).toHaveLength(2)
    expect(screen.getByRole('navigation', { name: 'Sections de la page' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Aller au contenu' })).toHaveAttribute(
      'href',
      '#contenu',
    )
  })

  it('donne un nom accessible à chaque graphique focalisable au clavier', async () => {
    render(<App />)
    await screen.findByText('Phrase.')

    // axe-core n'exige pas de nom pour role="application" : on le vérifie nous-mêmes.
    const graphiques = screen.getAllByRole('application')
    expect(graphiques).toHaveLength(2)
    expect(graphiques[0]).toHaveAccessibleName(/Courbe de l'indice ONI/)
    expect(graphiques[1]).toHaveAccessibleName(/Courbes superposées des deux épisodes/)
  })
})
