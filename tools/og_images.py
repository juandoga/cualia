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


def _destello(cx, cy, r, pasos=12):
    """Estrella de cuatro puntas con lados curvos (el destello del logo)."""
    pts = []
    puntas = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    for i in range(4):
        a, b = puntas[i], puntas[(i + 1) % 4]
        for k in range(pasos):
            t = k / pasos
            # curva cuadrática con control cerca del centro
            px = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * cx + t ** 2 * b[0]
            py = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * cy + t ** 2 * b[1]
            pts.append((px, py))
    return pts


def _logo(d, x, y, s=64):
    k = s / 100
    d.rounded_rectangle([x, y, x + s, y + s], radius=s * 0.24, fill=BLANCO)
    # Bocadillo morado con destello blanco y destello amarillo arriba a la derecha
    d.rounded_rectangle([x + 16 * k, y + 26 * k, x + 78 * k, y + 72 * k], radius=14 * k, fill=MORADO)
    d.polygon([(x + 26 * k, y + 64 * k), (x + 26 * k, y + 84 * k), (x + 44 * k, y + 70 * k)], fill=MORADO)
    d.polygon(_destello(x + 47 * k, y + 45 * k, 14 * k), fill=BLANCO)
    d.polygon(_destello(x + 80 * k, y + 17 * k, 11 * k), fill=AMARILLO)
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
    # Decoración: los destellos del logo, grandes y recortados a la derecha
    d.polygon(_destello(1130, 40, 230), fill=MORADO_OSC)
    d.polygon(_destello(1100, 330, 34), fill=AMARILLO)

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
