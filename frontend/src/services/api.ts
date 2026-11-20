// Accès à l'API : le seul fichier du frontend qui connaît les URL et fetch.
// Les composants appellent ces fonctions et reçoivent des données typées.

import type {
  Comparaison,
  EpisodeDeReference,
  Periode,
  ReponseErreur,
  SerieObservations,
} from '../types/api'

// Vide par défaut : les appels partent vers la même origine (/api/…), relayés par
// Vite en développement et par Caddy en production. Modifiable via VITE_URL_API.
const URL_API = import.meta.env.VITE_URL_API ?? ''

/** Erreur lisible par l'interface : message en français + code HTTP. */
export class ErreurApi extends Error {
  readonly code: number

  constructor(message: string, code: number) {
    super(message)
    this.name = 'ErreurApi'
    this.code = code
  }
}

async function lireJson<T>(chemin: string, parametres: Record<string, string>): Promise<T> {
  const chaineDeRequete = new URLSearchParams(parametres).toString()
  const requete = `${URL_API}/api/v1${chemin}${chaineDeRequete ? `?${chaineDeRequete}` : ''}`

  let reponse: Response
  try {
    reponse = await fetch(requete)
  } catch {
    throw new ErreurApi("Impossible de joindre l'API. Vérifiez qu'elle est démarrée.", 0)
  }

  if (!reponse.ok) {
    throw await versErreurApi(reponse)
  }
  return (await reponse.json()) as T
}

async function versErreurApi(reponse: Response): Promise<ErreurApi> {
  try {
    const corps = (await reponse.json()) as ReponseErreur
    const detail = corps.erreur.details[0]?.message
    const message = detail ? `${corps.erreur.message} ${detail}` : corps.erreur.message
    return new ErreurApi(message, reponse.status)
  } catch {
    return new ErreurApi(`Erreur inattendue (code ${reponse.status}).`, reponse.status)
  }
}

/** Retire les paramètres vides : ?debut=&fin= devient ?fin=… ou rien. */
function sansValeursVides(parametres: Record<string, string>): Record<string, string> {
  return Object.fromEntries(Object.entries(parametres).filter(([, valeur]) => valeur !== ''))
}

export function recupererObservations(periode: Periode): Promise<SerieObservations> {
  return lireJson('/observations', sansValeursVides({ ...periode }))
}

export function recupererEpisodesDeReference(): Promise<EpisodeDeReference[]> {
  return lireJson('/episodes/references', {})
}

export function comparerPeriodes(periodeA: Periode, periodeB: Periode): Promise<Comparaison> {
  return lireJson('/episodes/comparaison', {
    debut_a: periodeA.debut,
    fin_a: periodeA.fin,
    debut_b: periodeB.debut,
    fin_b: periodeB.fin,
  })
}
