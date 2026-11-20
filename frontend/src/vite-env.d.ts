/// <reference types="vite/client" />

// Variables d'environnement lues par le frontend (préfixe VITE_ obligatoire).
interface ImportMetaEnv {
  readonly VITE_URL_API?: string
}
