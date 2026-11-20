// Tests du service d'accès à l'API : construction des URL et lecture des erreurs.

import { afterEach, describe, expect, it, vi } from 'vitest'
import { ErreurApi, recupererObservations } from '../services/api'

function simulerReponse(statut: number, corps: unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(new Response(JSON.stringify(corps), { status: statut })),
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('recupererObservations', () => {
  it("n'envoie que les bornes renseignées", async () => {
    simulerReponse(200, { observations: [] })

    await recupererObservations({ debut: '1997-01-01', fin: '' })

    expect(fetch).toHaveBeenCalledWith('/api/v1/observations?debut=1997-01-01')
  })

  it("transforme le format d'erreur de l'API en message lisible", async () => {
    simulerReponse(422, {
      erreur: {
        code: 422,
        message: 'Paramètres de requête invalides.',
        details: [{ champ: 'debut', message: 'Date invalide.' }],
      },
    })

    const promesse = recupererObservations({ debut: 'x', fin: '' })

    await expect(promesse).rejects.toThrow(ErreurApi)
    await expect(promesse).rejects.toThrow('Paramètres de requête invalides. Date invalide.')
  })

  it('signale une API injoignable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    await expect(recupererObservations({ debut: '', fin: '' })).rejects.toThrow(
      "Impossible de joindre l'API",
    )
  })
})
