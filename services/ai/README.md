# services/ai

Entraînement et inférence des modèles de reconnaissance d'aliments.

Les images et les poids des modèles ne sont jamais versionnés dans Git (voir `.gitignore`).

```bash
uv sync
uv run ruff check .
uv run pytest
```

`datasets/` contient des scripts autonomes (téléchargement, export), pas un paquet importable : un paquet nommé `datasets` masquerait la bibliothèque Hugging Face du même nom.
