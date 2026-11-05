"""Routeur de la version 1 de l'API, monté sous `/api/v1`.

Chaque ressource a son fichier dans `routes/` et s'enregistre ici.
"""

from fastapi import APIRouter

API_V1_PREFIX = "/api/v1"

api_router = APIRouter(prefix=API_V1_PREFIX)
