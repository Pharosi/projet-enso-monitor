// Exécuté avant chaque fichier de test.
// Ajoute les vérifications DOM (toBeInTheDocument, toHaveTextContent…) à expect.
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Démonte les composants entre deux tests : chaque test part d'une page vide.
afterEach(() => {
  cleanup()
})

// jsdom ne fournit pas ResizeObserver, utilisé par ResponsiveContainer (Recharts).
// Ce substitut minimal suffit : les tests vérifient les valeurs, pas le dessin.
class ResizeObserverDeTest {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver ??= ResizeObserverDeTest as unknown as typeof ResizeObserver

// jsdom ne calcule pas la mise en page : tous les éléments mesurent 0 × 0 pixel et
// Recharts ne dessinerait rien. On leur donne une taille fictive pour que les
// graphiques soient rendus et que leur accessibilité puisse être testée.
HTMLElement.prototype.getBoundingClientRect = () =>
  ({ width: 800, height: 350, top: 0, left: 0, right: 800, bottom: 350, x: 0, y: 0 }) as DOMRect
