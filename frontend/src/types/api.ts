// Types des réponses de l'API ENSO Monitor (/api/v1).
// Ils reproduisent les schémas Pydantic du backend (backend/enso/api/v1/schemas.py) :
// si l'API change, TypeScript signale chaque endroit du frontend à adapter.

export interface Observation {
  saison: string
  annee: number
  date_periode: string // date ISO, ex. "1998-01-01"
  anomalie: number // valeur de l'ONI en °C
  temperature_totale: number
}

export interface Indice {
  code: string
  nom: string
  unite: string
  version: string
}

export interface Source {
  nom: string
  url: string
  derniere_extraction: string | null
}

export interface SerieObservations {
  indice: Indice
  source: Source
  debut: string | null
  fin: string | null
  nombre: number
  observations: Observation[]
}

export interface Periode {
  debut: string
  fin: string
}

export interface EpisodeDeReference extends Periode {
  identifiant: string
  libelle: string
  en_cours: boolean
}

export interface AnalysePeriode extends Periode {
  nombre_de_saisons: number
  pic: Observation
  creux: Observation
  anomalie_moyenne: number
  saisons_el_nino_consecutives: number
  saisons_la_nina_consecutives: number
  episode_el_nino: boolean
  episode_la_nina: boolean
  intensite_du_pic: string | null
  observations: Observation[]
}

export interface Regles {
  indice: string
  seuil_el_nino: number
  seuil_la_nina: number
  duree_minimale_saisons: number
  categories_intensite: Record<string, number>
}

export interface Comparaison {
  periode_a: AnalysePeriode
  periode_b: AnalysePeriode
  regles: Regles
  interpretation: string[]
  limites: string[]
}

// Format d'erreur unique renvoyé par l'API (backend/enso/api/erreurs.py).
export interface ReponseErreur {
  erreur: {
    code: number
    message: string
    details: { champ: string; message: string }[]
  }
}
