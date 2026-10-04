# Cualia

Guía en español para elegir inteligencia artificial: qué IA usar para cada cosa.

- `index.html`: la web.
- `data/brujula.json`: todas las fichas, novedades y fecha de revisión. La revisión semanal solo modifica este archivo.
- `tools/validar.py`: comprueba los datos antes de cada commit de la revisión semanal (`python3 tools/validar.py`).
- `tools/build_pages.py`: al publicar genera una página por IA (`/ia/`), por pack (`/pack/`) y por tema (`/mejores/`), las imágenes de vista previa para compartir (`/og/`), el sitemap y robots.txt.
- `tools/og_images.py` y `tools/fonts/`: dibujan esas imágenes (fuentes con licencia OFL).
