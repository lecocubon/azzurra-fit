"""Genera el icono de Azzurra Fit en todos sus tamanos a partir del logo.

Uso: python scripts/iconos.py   (necesita Pillow)

Parte de scripts/logo-azzurra.webp, el logo redondo del equipo con el fondo
transparente (ocupa el 90 % de la imagen). Escribe el logo y el favicon de la
web, los PNG de la PWA y los iconos y pantallas de carga de Android: la
medalla va sobre el azul marino de la app y, donde el sistema recorta en
circulo o en forma libre (iconos adaptables, maskable), se achica para que
quede entera dentro de la zona segura.
"""
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "android/app/src/main/res"
LOGO = Image.open(RAIZ / "scripts/logo-azzurra.webp").convert("RGBA")
# Azul marino de la app: el fondo detras de la medalla.
FONDO = "#002D84"


def logo(lado: int, escala: float = 1.0, fondo: str | None = FONDO) -> Image.Image:
    """El logo de `lado` px, achicado a `escala` y centrado sobre el fondo (o transparente)."""
    lienzo = Image.new("RGBA", (lado, lado), fondo if fondo else (0, 0, 0, 0))
    medida = round(lado * escala)
    pieza = LOGO.resize((medida, medida), Image.LANCZOS)
    lienzo.paste(pieza, ((lado - medida) // 2, (lado - medida) // 2), pieza)
    return lienzo


def recortar(imagen: Image.Image, radio: float | None) -> Image.Image:
    """Esquinas redondeadas (radio en fraccion del lado) o circulo si radio es None."""
    lado = imagen.width
    mascara = Image.new("L", (lado * 4, lado * 4), 0)
    dibujo = ImageDraw.Draw(mascara)
    if radio is None:
        dibujo.ellipse((0, 0, lado * 4 - 1, lado * 4 - 1), fill=255)
    else:
        dibujo.rounded_rectangle((0, 0, lado * 4 - 1, lado * 4 - 1), radius=round(lado * 4 * radio), fill=255)
    salida = imagen.copy()
    salida.putalpha(mascara.resize((lado, lado), Image.LANCZOS))
    return salida


def guardar(imagen: Image.Image, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    imagen.save(ruta)


def pantalla_de_carga(ancho: int, alto: int) -> Image.Image:
    lienzo = Image.new("RGB", (ancho, alto), FONDO)
    lado = round(min(ancho, alto) * 0.55)
    marca = logo(lado)
    lienzo.paste(marca, ((ancho - lado) // 2, (alto - lado) // 2), marca)
    return lienzo


def main() -> None:
    publico = RAIZ / "public"
    guardar(logo(512, fondo=None), publico / "logo.png")
    guardar(logo(64, fondo=None), publico / "favicon.png")
    guardar(recortar(logo(192, 0.92), 0.22), publico / "pwa-192.png")
    guardar(recortar(logo(512, 0.92), 0.22), publico / "pwa-512.png")
    # Maskable: zona segura de 80 %.
    guardar(logo(512, 0.86), publico / "pwa-maskable-512.png")
    guardar(logo(180, 0.9).convert("RGB"), publico / "apple-touch-icon.png")

    # Android: icono clasico, redondo y la capa de adelante del adaptable
    # (108 dp con 66 dp visibles: la medalla tiene que caber en ese circulo).
    densidades = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
    for nombre, factor in densidades.items():
        carpeta = RES / f"mipmap-{nombre}"
        lado = round(48 * factor)
        guardar(recortar(logo(lado, 0.92), 0.18), carpeta / "ic_launcher.png")
        guardar(recortar(logo(lado, 0.92), None), carpeta / "ic_launcher_round.png")
        guardar(logo(round(108 * factor), 0.7, fondo=None), carpeta / "ic_launcher_foreground.png")

    for ruta in RES.glob("drawable*/splash.png"):
        actual = Image.open(ruta)
        guardar(pantalla_de_carga(*actual.size), ruta)

    color = RES / "values/ic_launcher_background.xml"
    color.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        f'    <color name="ic_launcher_background">{FONDO}</color>\n</resources>\n',
        encoding="utf8",
    )
    print("iconos generados")


if __name__ == "__main__":
    main()
