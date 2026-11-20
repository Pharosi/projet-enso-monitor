// Exécuté avant chaque fichier de test.
// Ajoute les vérifications DOM (toBeInTheDocument, toHaveTextContent…) à expect.
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Démonte les composants entre deux tests : chaque test part d'une page vide.
afterEach(() => {
  cleanup()
})
