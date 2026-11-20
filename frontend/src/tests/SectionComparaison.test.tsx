// Tests de la section de comparaison (API simulée).

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { SectionComparaison } from '../composants/SectionComparaison'
import { comparerPeriodes, recupererEpisodesDeReference } from '../services/api'
import type { AnalysePeriode, Comparaison, EpisodeDeReference, Observation } from '../types/api'
import { fusionnerSeries } from '../utilitaires/comparaison'

vi.mock('../services/api')

function episode(identifiant: string, libelle: string, debut: string, fin: string) {
  return { identifiant, libelle, debut, fin, en_cours: false } satisfies EpisodeDeReference
}

const EPISODES = [
  episode('el-nino-1982-1983', 'El Niño 1982-1983', '1982-01-01', '1983-06-01'),
  episode('el-nino-1997-1998', 'El Niño 1997-1998', '1997-01-01', '1998-06-01'),
  episode('el-nino-2015-2016', 'El Niño 2015-2016', '2015-01-01', '2016-06-01'),
]

function obs(saison: string, annee: number, anomalie: number): Observation {
  return { saison, annee, date_periode: `${annee}-01-01`, anomalie, temperature_totale: 28 }
}

function analyse(pic: Observation, saisonsElNino: number): AnalysePeriode {
  return {
    debut: '',
    fin: '',
    nombre_de_saisons: 18,
    pic,
    creux: obs('DJF', pic.annee, -0.4),
    anomalie_moyenne: 1.1,
    saisons_el_nino_consecutives: saisonsElNino,
    saisons_la_nina_consecutives: 0,
    episode_el_nino: true,
    episode_la_nina: false,
    intensite_du_pic: 'très forte',
    observations: [pic],
  }
}

function comparaison(picA: Observation, picB: Observation, phrase: string): Comparaison {
  return {
    periode_a: analyse(picA, 12),
    periode_b: analyse(picB, 17),
    regles: {
      indice: 'ONI v6 (ERSST.v6)',
      seuil_el_nino: 0.5,
      seuil_la_nina: -0.5,
      duree_minimale_saisons: 5,
      categories_intensite: {},
    },
    interpretation: [phrase],
    limites: ['Aucune prévision n’est réalisée.'],
  }
}

describe('SectionComparaison', () => {
  beforeEach(() => {
    vi.mocked(recupererEpisodesDeReference).mockResolvedValue(EPISODES)
    vi.mocked(comparerPeriodes).mockReset()
  })

  it('compare 1997-1998 et 2015-2016 à l’ouverture, avec interprétation et limites', async () => {
    vi.mocked(comparerPeriodes).mockResolvedValue(
      comparaison(obs('NDJ', 1997, 2.37), obs('NDJ', 2015, 2.59), 'Le pic de B dépasse A.'),
    )
    render(<SectionComparaison />)

    expect(await screen.findByText('Le pic de B dépasse A.')).toBeInTheDocument()
    expect(comparerPeriodes).toHaveBeenCalledWith(
      { debut: '1997-01-01', fin: '1998-06-01' },
      { debut: '2015-01-01', fin: '2016-06-01' },
    )
    const lignePic = screen.getByRole('row', { name: /Pic \(maximum\)/ })
    expect(within(lignePic).getByText('+2,37 °C — NDJ 1997')).toBeInTheDocument()
    expect(within(lignePic).getByText('+2,59 °C — NDJ 2015')).toBeInTheDocument()
    expect(screen.getByText('Aucune prévision n’est réalisée.')).toBeInTheDocument()
    expect(screen.getByText(/au moins 5 saisons consécutives/)).toBeInTheDocument()
  })

  it('relance la comparaison avec les épisodes choisis', async () => {
    const utilisateur = userEvent.setup()
    vi.mocked(comparerPeriodes)
      .mockResolvedValueOnce(
        comparaison(obs('NDJ', 1997, 2.37), obs('NDJ', 2015, 2.59), 'Initiale'),
      )
      .mockResolvedValueOnce(
        comparaison(obs('NDJ', 1982, 2.12), obs('NDJ', 2015, 2.59), 'Nouvelle'),
      )
    render(<SectionComparaison />)
    await screen.findByText('Initiale')

    await utilisateur.selectOptions(screen.getByLabelText('Épisode A'), 'El Niño 1982-1983')
    await utilisateur.click(screen.getByRole('button', { name: 'Comparer' }))

    expect(await screen.findByText('Nouvelle')).toBeInTheDocument()
    expect(comparerPeriodes).toHaveBeenLastCalledWith(
      { debut: '1982-01-01', fin: '1983-06-01' },
      { debut: '2015-01-01', fin: '2016-06-01' },
    )
  })

  it('refuse de comparer un épisode avec lui-même', async () => {
    const utilisateur = userEvent.setup()
    vi.mocked(comparerPeriodes).mockResolvedValue(
      comparaison(obs('NDJ', 1997, 2.37), obs('NDJ', 2015, 2.59), 'Initiale'),
    )
    render(<SectionComparaison />)
    await screen.findByText('Initiale')

    await utilisateur.selectOptions(screen.getByLabelText('Épisode B'), 'El Niño 1997-1998')
    await utilisateur.click(screen.getByRole('button', { name: 'Comparer' }))

    expect(screen.getByRole('alert')).toHaveTextContent('deux épisodes différents')
    expect(comparerPeriodes).toHaveBeenCalledTimes(1)
  })
})

describe('fusionnerSeries', () => {
  it('aligne les saisons par rang et complète la série la plus courte par null', () => {
    const points = fusionnerSeries(
      [obs('DJF', 1997, -0.41), obs('JFM', 1997, -0.26)],
      [obs('DJF', 2015, 0.73)],
    )

    expect(points).toEqual([
      { rang: 1, anomalieA: -0.41, anomalieB: 0.73, saisonA: 'DJF 1997', saisonB: 'DJF 2015' },
      { rang: 2, anomalieA: -0.26, anomalieB: null, saisonA: 'JFM 1997', saisonB: null },
    ])
  })
})
