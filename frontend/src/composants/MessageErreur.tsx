// Message d'erreur annoncé immédiatement par les lecteurs d'écran (role="alert").

import styles from './MessageErreur.module.css'

export function MessageErreur({ message }: { message: string }) {
  return (
    <p role="alert" className={styles.erreur}>
      {message}
    </p>
  )
}
