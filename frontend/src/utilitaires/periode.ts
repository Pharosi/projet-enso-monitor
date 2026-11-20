// Choix de la période : mois et années proposés, conversion en date pour l'API.

export const MOIS = [
  'janvier',
  'février',
  'mars',
  'avril',
  'mai',
  'juin',
  'juillet',
  'août',
  'septembre',
  'octobre',
  'novembre',
  'décembre',
].map((libelle, index) => ({ libelle, valeur: String(index + 1).padStart(2, '0') }))

// La série ONI commence en 1950 ; on propose jusqu'à l'année en cours.
const PREMIERE_ANNEE = 1950
export const ANNEES_DISPONIBLES = Array.from(
  { length: new Date().getFullYear() - PREMIERE_ANNEE + 1 },
  (_, index) => String(PREMIERE_ANNEE + index),
)

/** Mois + année → date de période attendue par l'API.
 *  ("01", "1998") → "1998-01-01" ; ("", "") → "" (pas de limite) ; un seul des deux → null (incomplet). */
export function versDatePeriode(mois: string, annee: string): string | null {
  if (mois === '' && annee === '') return ''
  if (mois === '' || annee === '') return null
  return `${annee}-${mois}-01`
}
