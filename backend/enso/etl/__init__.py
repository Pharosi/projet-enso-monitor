"""ETL de l'indice ONI : Extraction (NOAA) -> Transformation (Pandas) -> Chargement (PostgreSQL).

L'ETL est un point d'entrée indépendant de l'API : il s'exécute à la demande
(python -m enso.etl) ou de façon planifiée, sans ralentir les requêtes des utilisateurs.
"""
