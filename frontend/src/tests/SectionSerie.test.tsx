// Test minimal n°3 du sujet : un changement de période actualise les valeurs affichées.
//
// L'API est simulée (vi.mock) : le test vérifie le comportement de l'interface,
// indépendamment du backend. Valeurs issues du fichier NOAA réel (ONI v6).

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { SectionSerie } from '../composants/SectionSerie'
import { recupererObservations } from '../services/api'
import type { Observation, SerieObservations } from '../types/api'

vi.mock('../services/api')

function observation(saison: string, annee: number, mois: string, anomalie: number): Observation {
  return { saison, annee, date_periode: `${annee}-${mois}-01`, anomalie, temperature_totale: 28 }
}

function serie(observations: Observation[]): SerieObservations {
  return {
    indice: { code: 'ONI', nom: 'Oceanic Niño Index', unite: '°C', version: 'ONI v6 (ERSST.v6)' },
    source: {
      nom: 'NOAA Climate Prediction Center',
      url: 'https://www.cpc.ncep.noaa.gov/',
      derniere_extraction: '2026-11-19T12:16:29Z',
    },
    debut: null,
    fin: null,
    nombre: observations.length,
    observations,
  }
}

const SERIE_COMPLETE = serie([
  observation('DJF', 1950, '01', -1.32),
  observation('NDJ', 2015, '12', 2.59),
  observation('ASO', 2026, '09', 2.46),
])
const ANNEE_1998 = serie([
  observation('DJF', 1998, '01', 2.22),
  observation('JJA', 1998, '07', -0.63),
  observation('NDJ', 1998, '12', -1.47),
])

/** Choisit un mois et une année dans les listes du filtre (même geste dans tous les navigateurs). */
async function choisir(
  utilisateur: ReturnType<typeof userEvent.setup>,
  borne: 'début' | 'fin',
  mois: string,
  annee: string,
) {
  await utilisateur.selectOptions(screen.getByLabelText(`Mois de ${borne}`), mois)
  await utilisateur.selectOptions(screen.getByLabelText(`Année de ${borne}`), annee)
}

describe('SectionSerie', () => {
  beforeEach(() => {
    vi.mocked(recupererObservations).mockReset()
  })

  it('actualise les valeurs affichées quand la période change', async () => {
    const utilisateur = userEvent.setup()
    vi.mocked(recupererObservations)
      .mockResolvedValueOnce(SERIE_COMPLETE)
      .mockResolvedValueOnce(ANNEE_1998)
    render(<SectionSerie />)

    // 1. Au chargement : toute la série, maximum de 2015.
    expect(await screen.findByText(/3 saisons, de DJF 1950 à ASO 2026/)).toBeInTheDocument()
    expect(screen.getByText(/Maximum \+2,59 °C \(NDJ 2015\)/)).toBeInTheDocument()

    // 2. L'utilisateur choisit janvier 1998 → décembre 1998 puis valide.
    await choisir(utilisateur, 'début', 'janvier', '1998')
    await choisir(utilisateur, 'fin', 'décembre', '1998')
    await utilisateur.click(screen.getByRole('button', { name: 'Afficher' }))

    // 3. La bonne période est demandée à l'API…
    expect(recupererObservations).toHaveBeenLastCalledWith({
      debut: '1998-01-01',
      fin: '1998-12-01',
    })
    // … et les valeurs affichées sont celles de 1998.
    expect(await screen.findByText(/3 saisons, de DJF 1998 à NDJ 1998/)).toBeInTheDocument()
    expect(screen.getByText(/Maximum \+2,22 °C \(DJF 1998\)/)).toBeInTheDocument()
    expect(screen.queryByText(/NDJ 2015/)).not.toBeInTheDocument()
  })

  it("refuse une période inversée sans appeler l'API", async () => {
    const utilisateur = userEvent.setup()
    vi.mocked(recupererObservations).mockResolvedValue(SERIE_COMPLETE)
    render(<SectionSerie />)
    await screen.findByText(/3 saisons/)

    await choisir(utilisateur, 'début', 'janvier', '1999')
    await choisir(utilisateur, 'fin', 'janvier', '1998')
    await utilisateur.click(screen.getByRole('button', { name: 'Afficher' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Le mois de début doit précéder')
    expect(recupererObservations).toHaveBeenCalledTimes(1) // seulement le chargement initial
  })

  // Non-régression de l'anomalie #44 : Safari affichait un champ texte libre.
  it('ne propose aucun champ de date à saisir librement', async () => {
    vi.mocked(recupererObservations).mockResolvedValue(SERIE_COMPLETE)
    const { container } = render(<SectionSerie />)
    await screen.findByText(/3 saisons/)

    const formulaire = container.querySelector('form') as HTMLFormElement
    expect(within(formulaire).queryAllByRole('textbox')).toHaveLength(0)
    expect(formulaire.querySelectorAll('input')).toHaveLength(0)
    expect(within(formulaire).getAllByRole('combobox')).toHaveLength(4) // mois et année × 2
  })

  it("refuse un mois choisi sans année, sans appeler l'API", async () => {
    const utilisateur = userEvent.setup()
    vi.mocked(recupererObservations).mockResolvedValue(SERIE_COMPLETE)
    render(<SectionSerie />)
    await screen.findByText(/3 saisons/)

    await utilisateur.selectOptions(screen.getByLabelText('Mois de début'), 'mars')
    await utilisateur.click(screen.getByRole('button', { name: 'Afficher' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Début : choisissez le mois et l’année')
    expect(recupererObservations).toHaveBeenCalledTimes(1)
  })

  it("affiche le message de l'API en cas d'erreur", async () => {
    vi.mocked(recupererObservations).mockRejectedValue(
      new Error("Aucune donnée pour l'indice ONI : lancer l'import (python -m enso.etl)."),
    )
    render(<SectionSerie />)

    expect(await screen.findByRole('alert')).toHaveTextContent("lancer l'import")
  })

  it('affiche la source, la version et la date d’extraction', async () => {
    vi.mocked(recupererObservations).mockResolvedValue(SERIE_COMPLETE)
    render(<SectionSerie />)

    expect(
      await screen.findByRole('link', { name: 'NOAA Climate Prediction Center' }),
    ).toBeInTheDocument()
    expect(screen.getByText(/ONI v6 \(ERSST\.v6\), unité : °C/)).toBeInTheDocument()
    expect(screen.getByText(/extraites le 19\/11\/2026/)).toBeInTheDocument()
  })
})
