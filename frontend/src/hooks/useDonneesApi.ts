// Hook générique : charge des données de l'API chaque fois que les paramètres changent.
// Utilisé par useObservations et useComparaison (un seul modèle pour tout le frontend).
// (Le préfixe « use » est imposé par React pour tout hook.)

import { useEffect, useState } from 'react'

export interface EtatChargement<T> {
  donnees: T | null
  chargement: boolean
  erreur: string | null
}

interface Resultat<P, T> {
  parametres: P // pour quels paramètres ce résultat a été obtenu
  donnees: T | null
  erreur: string | null
}

export function useDonneesApi<P, T>(
  parametres: P,
  charger: (parametres: P) => Promise<T>,
): EtatChargement<T> {
  const [resultat, setResultat] = useState<Resultat<P, T> | null>(null)

  useEffect(() => {
    // Si les paramètres changent avant la fin de la requête, l'ancienne réponse est
    // ignorée : l'écran correspond toujours à la DERNIÈRE demande de l'utilisateur.
    let reponseObsolete = false

    charger(parametres)
      .then((donnees) => {
        if (!reponseObsolete) setResultat({ parametres, donnees, erreur: null })
      })
      .catch((erreur: Error) => {
        if (!reponseObsolete) setResultat({ parametres, donnees: null, erreur: erreur.message })
      })

    return () => {
      reponseObsolete = true
    }
  }, [parametres, charger])

  // L'état de chargement est DÉDUIT : tant que le résultat ne correspond pas aux
  // paramètres demandés, on charge. Les anciennes données restent affichées en attendant.
  const chargement = resultat === null || resultat.parametres !== parametres
  return {
    donnees: resultat?.donnees ?? null,
    chargement,
    erreur: chargement ? null : (resultat?.erreur ?? null),
  }
}
