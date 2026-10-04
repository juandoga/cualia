"""Imágenes de vista previa (1200×630) para cuando se comparte un enlace de Cualia
en WhatsApp, LinkedIn, X, etc. Las usa tools/build_pages.py; no hace falta tocarlo."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
MORADO, MORADO_OSC, AMARILLO, BLANCO = (91, 63, 217), (61, 38, 168), (255, 201, 74), (255, 255, 255)
SUAVE = (226, 220, 255)


def _titular(size, peso=800):
    f = ImageFont.truetype(os.path.join(FONTS, "BricolageGrotesque-VF.ttf"), size)
    try:
        f.set_variation_by_axes([96, peso, 100])  # opsz, wght, wdth
    except Exception:
        pass
    return f


def _texto(size, negrita=False):
    nombre = "AtkinsonHyperlegible-Bold.ttf" if negrita else "AtkinsonHyperlegible-Regular.ttf"
    return ImageFont.truetype(os.path.join(FONTS, nombre), size)


def _partir(d, txt, fuente, ancho, max_lineas):
    palabras, lineas, actual = txt.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=fuente) <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        while d.textlength(lineas[-1] + "…", font=fuente) > ancho and " " in lineas[-1]:
            lineas[-1] = lineas[-1].rsplit(" ", 1)[0]
        lineas[-1] += "…"
    return lineas


def _ajustar_titulo(d, txt, ancho, tamanos=(92, 80, 68, 58), max_lineas=2):
    for t in tamanos:
        f = _titular(t)
        lineas = _partir(d, txt, f, ancho, 99)
        if len(lineas) <= max_lineas:
            return f, lineas, t
    f = _titular(tamanos[-1])
    return f, _partir(d, txt, f, ancho, max_lineas), tamanos[-1]


def _logo(d, x, y, s=64):
    r = s * 0.24
    d.rounded_rectangle([x, y, x + s, y + s], radius=r, fill=BLANCO)
    c, rad, grosor = (x + s / 2, y + s / 2), s * 0.25, max(4, int(s * 0.13))
    d.arc([c[0] - rad, c[1] - rad, c[0] + rad, c[1] + rad], start=-45 + 90, end=-45 + 90 + 270, fill=MORADO, width=grosor)
    pr = s * 0.08
    px, py = x + s * 0.677, y + s * 0.323
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=AMARILLO)
    f = _titular(46)
    d.text((x + s + 16, y + s / 2), "Cual", font=f, fill=BLANCO, anchor="lm")
    d.text((x + s + 16 + d.textlength("Cual", font=f), y + s / 2), "ia", font=f, fill=AMARILLO, anchor="lm")


def _pastilla(d, x, y, txt, fondo=BLANCO, tinta=MORADO_OSC):
    f = _texto(30, True)
    w = d.textlength(txt, font=f) + 44
    d.rounded_rectangle([x, y, x + w, y + 56], radius=28, fill=fondo)
    d.text((x + 22, y + 28), txt, font=f, fill=tinta, anchor="lm")
    return x + w + 14


def tarjeta(destino, etiqueta, titulo, pastillas=(), pie="¿Qué IA uso para esto?", dominio="juandoga.github.io/cualia"):
    img = Image.new("RGB", (W, H), MORADO)
    d = ImageDraw.Draw(img)
    # Decoración: el anillo del logo, grande y recortado a la derecha
    d.arc([930, -230, 1430, 270], start=135, end=405, fill=MORADO_OSC, width=60)
    d.ellipse([1124, 52, 1184, 112], fill=AMARILLO)

    _logo(d, 72, 64)
    y = 200
    if etiqueta:
        d.text((72, y), etiqueta.upper(), font=_texto(28, True), fill=SUAVE)
        y += 52
    f, lineas, t = _ajustar_titulo(d, titulo, 900, tamanos=(88, 76, 66, 58))
    for ln in lineas:
        d.text((72, y), ln, font=f, fill=BLANCO)
        y += int(t * 1.08)
    x, yp = 72, max(y + 26, 440)
    for p in pastillas:
        if p:
            if x + d.textlength(p, font=_texto(30, True)) + 44 > W - 72:
                break
            x = _pastilla(d, x, yp, p)
    d.text((72, H - 52), pie, font=_texto(28), fill=SUAVE, anchor="lm")
    d.text((W - 72, H - 52), dominio, font=_texto(28, True), fill=BLANCO, anchor="rm")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    img.save(destino, "PNG", optimize=True)
