"""Descarga las fotos de free-exercise-db (dominio publico) para la biblioteca.

Uso: python scripts/imagenes.py
Lee src/data/biblioteca.json y escribe en public/ejercicios dos fotos por
ejercicio: <id>.webp (posicion inicial) y <id>-fin.webp (posicion final).

Una fuente "wger:123" o "wger:123,124" baja de wger.de (CC BY-SA: el ejercicio
lleva su `credito`); con un solo numero hay una sola foto.
"""
import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises"
WGER = "https://wger.de/api/v2/exerciseimage"
ANCHO = 360
CALIDAD = 58
# Numero de foto en la base -> sufijo del archivo.
CUADROS = {0: "", 1: "-fin"}


def url_de(fuente: str, cuadro: int) -> str | None:
    """Direccion de la foto `cuadro` de esa fuente, o None si no la tiene."""
    if not fuente.startswith("wger:"):
        return f"{BASE}/{fuente}/{cuadro}.jpg"
    ids = fuente[5:].split(",")
    if cuadro >= len(ids):
        return None
    with urllib.request.urlopen(f"{WGER}/{ids[cuadro]}/", timeout=30) as r:
        return json.load(r)["image"]


def bajar(fuente: str, cuadro: int, salida: Path) -> bool:
    """Descarga y comprime una foto. False si esa foto no existe en la base."""
    url = url_de(fuente, cuadro)
    if url is None:
        return False
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            original = Image.open(io.BytesIO(r.read())).convert("RGBA")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise
    # Las de wger suelen ser PNG transparentes: van sobre blanco.
    img = Image.new("RGB", original.size, "white")
    img.paste(original, mask=original.getchannel("A"))
    alto = round(img.height * ANCHO / img.width)
    img.resize((ANCHO, alto), Image.LANCZOS).save(salida, "WEBP", quality=CALIDAD, method=6)
    return True


def main() -> int:
    biblioteca = json.loads((RAIZ / "src/data/biblioteca.json").read_text(encoding="utf-8"))
    destino = RAIZ / "public/ejercicios"
    destino.mkdir(parents=True, exist_ok=True)
    total = 0
    for ejercicio in biblioteca:
        fuente = ejercicio.get("fuenteImagen")
        if not fuente:
            continue
        for cuadro, sufijo in CUADROS.items():
            salida = destino / f"{ejercicio['id']}{sufijo}.webp"
            if not salida.exists() and not bajar(fuente, cuadro, salida):
                print(f"{ejercicio['id']}{sufijo}: la base no tiene la foto {cuadro}")
                continue
            total += salida.stat().st_size
    print(f"Total: {total / 1024 / 1024:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
