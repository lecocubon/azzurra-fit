"""Genera el icono de Azzurra Fit en todos sus tamanos a partir de un SVG.

Uso: python scripts/iconos.py   (necesita pymupdf y Pillow)

Escudo azul marino con borde dorado y franja tricolor, como el del colegio,
con una A y una F a los lados. Escribe public/favicon.svg, los PNG de la PWA
y los iconos y pantallas de carga de Android.
"""
import io
from pathlib import Path

import pymupdf
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "android/app/src/main/res"

FONDO = "#1d4fa0"
MARINO = "#0e2a5a"
DORADO = "#e0b034"
VERDE = "#009246"
ROJO = "#ce2b37"
BLANCO = "#ffffff"

# Todo en una caja de 100 x 100, centrado en (50, 51).
ESCUDO = f"""
  <path d="M50 12 L82 21 L82 57 L50 90 L18 57 L18 21 Z" fill="{MARINO}" stroke="{DORADO}" stroke-width="4.5" stroke-linejoin="round"/>
  <rect x="44.5" y="27" width="3.7" height="47" fill="{VERDE}"/>
  <rect x="48.2" y="27" width="3.6" height="47" fill="{BLANCO}"/>
  <rect x="51.8" y="27" width="3.7" height="47" fill="{ROJO}"/>
  <path fill-rule="evenodd" fill="{BLANCO}" d="M25 62 L32 33 L36 33 L43 62 L38.6 62 L37.2 56 L30.8 56 L29.4 62 Z M31.8 51.6 L36.2 51.6 L34 42 Z"/>
  <path fill="{BLANCO}" d="M58 33 H73 V37.8 H62.8 V45.2 H71 V50 H62.8 V62 H58 Z"/>
"""


def svg(contenido: str, fondo: str | None = None, radio: float = 0) -> str:
    capa = f'<rect width="100" height="100" rx="{radio}" fill="{fondo}"/>' if fondo else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{capa}{contenido}</svg>'


def escudo_escalado(escala: float) -> str:
    """El escudo achicado al centro: zona segura de iconos adaptables y maskable."""
    d = 50 * (1 - escala)
    return f'<g transform="translate({d:.2f} {d:.2f}) scale({escala})">{ESCUDO}</g>'


def png(codigo: str, lado: int) -> Image.Image:
    doc = pymupdf.open(stream=codigo.encode("utf8"), filetype="svg")
    pagina = doc[0]
    zoom = lado / pagina.rect.width
    pix = pagina.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=True)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA").resize((lado, lado), Image.LANCZOS)


def guardar(imagen: Image.Image, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    imagen.save(ruta)


def pantalla_de_carga(ancho: int, alto: int) -> Image.Image:
    lienzo = Image.new("RGB", (ancho, alto), MARINO)
    lado = round(min(ancho, alto) * 0.42)
    marca = png(svg(ESCUDO), lado)
    lienzo.paste(marca, ((ancho - lado) // 2, (alto - lado) // 2), marca)
    return lienzo


def main() -> None:
    completo = svg(ESCUDO, FONDO, radio=22)
    (RAIZ / "public/favicon.svg").write_text(completo + "\n", encoding="utf8")
    guardar(png(completo, 192), RAIZ / "public/pwa-192.png")
    guardar(png(completo, 512), RAIZ / "public/pwa-512.png")
    guardar(png(svg(escudo_escalado(0.72), FONDO), 512), RAIZ / "public/pwa-maskable-512.png")
    guardar(png(svg(ESCUDO, FONDO), 180).convert("RGB"), RAIZ / "public/apple-touch-icon.png")

    # Android: icono clasico, redondo y la capa de adelante del adaptable (108 dp, zona segura de 66).
    densidades = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
    redondo = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="{FONDO}"/>{escudo_escalado(0.86)}</svg>'
    for nombre, factor in densidades.items():
        carpeta = RES / f"mipmap-{nombre}"
        guardar(png(svg(ESCUDO, FONDO, radio=18), round(48 * factor)), carpeta / "ic_launcher.png")
        guardar(png(redondo, round(48 * factor)), carpeta / "ic_launcher_round.png")
        guardar(png(svg(escudo_escalado(0.6)), round(108 * factor)), carpeta / "ic_launcher_foreground.png")

    for ruta in RES.glob("drawable*/splash.png"):
        actual = Image.open(ruta)
        guardar(pantalla_de_carga(*actual.size), ruta)

    color = RES / "values/ic_launcher_background.xml"
    color.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        f'    <color name="ic_launcher_background">{FONDO.upper()}</color>\n</resources>\n',
        encoding="utf8",
    )
    print("iconos generados")


if __name__ == "__main__":
    main()
