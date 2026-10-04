#!/usr/bin/env python3
"""Valida data/brujula.json y data/historial.json antes de cada commit.

Uso: python3 tools/validar.py
Compara el historial con el de la última versión subida (git HEAD) para
comprobar que solo ha crecido. Sale con código 1 si hay errores.
"""
import json, re, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CATS = ["chat", "imagen", "video", "musica", "voz", "codigo", "estudio", "trabajo"]
CAMPOS = ("id slug nombre empresa precio precioTxt precioMes nivel desc para ejemplos novedad web "
          "afiliado dominio verificado actualizado gratisTipo gratisTxt consumo consumoTxt "
          "plataformas mejorEn pros contras notas nota").split()
FECHA = re.compile(r"\d{4}-\d{2}-\d{2}$")

errores, avisos = [], []
d = json.loads((RAIZ / "data/brujula.json").read_text(encoding="utf-8"))
H = json.loads((RAIZ / "data/historial.json").read_text(encoding="utf-8"))

# Categorías y fichas
if sorted(c["id"] for c in d["cats"]) != sorted(CATS):
    errores.append("Las categorías no son las 8 esperadas")
nombres, slugs, ids = set(), set(), set()
for c in d["cats"]:
    if len(c["herramientas"]) != 30:
        errores.append(f"{c['id']}: tiene {len(c['herramientas'])} fichas (deben ser 30)")
    if not FECHA.match(c.get("actualizado", "")):
        errores.append(f"{c['id']}: 'actualizado' no válido")
    for h in c["herramientas"]:
        hid = h.get("id", "?")
        falta = [k for k in CAMPOS if k not in h]
        if falta:
            errores.append(f"{hid}: faltan campos {falta}")
            continue
        if h["precio"] not in ("gratis", "freemium", "pago"): errores.append(f"{hid}: precio")
        if h["gratisTipo"] not in ("libre", "util", "limitado", "prueba", "no"): errores.append(f"{hid}: gratisTipo")
        if h["consumo"] not in ("gratis", "fijo", "creditos", "uso"): errores.append(f"{hid}: consumo")
        if h["mejorEn"] not in ("ordenador", "movil", "ambos"): errores.append(f"{hid}: mejorEn")
        if not h["plataformas"] or not set(h["plataformas"]) <= {"web", "movil", "escritorio"}: errores.append(f"{hid}: plataformas")
        if h["nivel"] not in (1, 2, 3): errores.append(f"{hid}: nivel")
        if not (h["precioMes"] is None or isinstance(h["precioMes"], (int, float))): errores.append(f"{hid}: precioMes")
        if not isinstance(h["verificado"], bool): errores.append(f"{hid}: verificado")
        if not FECHA.match(h["actualizado"]): errores.append(f"{hid}: actualizado")
        for k in ("nombre", "precioTxt", "gratisTxt", "consumoTxt", "desc", "para", "dominio", "web"):
            if not h[k]: errores.append(f"{hid}: '{k}' vacío")
        if not 2 <= len(h["pros"]) <= 3: errores.append(f"{hid}: pros")
        if not 2 <= len(h["contras"]) <= 3: errores.append(f"{hid}: contras")
        if len(h["ejemplos"]) != 3: avisos.append(f"{hid}: {len(h['ejemplos'])} ejemplos (deben ser 3)")
        n = h["notas"]
        if any(not isinstance(n.get(k), int) or not 0 <= n[k] <= 10 for k in ("calidad", "versatilidad", "facilidad", "precio")):
            errores.append(f"{hid}: notas parciales")
        elif h["nota"] != round(n["calidad"] * 4 + n["versatilidad"] * 2 + n["facilidad"] * 2 + n["precio"] * 2):
            errores.append(f"{hid}: 'nota' no coincide con la fórmula")
        if h["slug"] in slugs: errores.append(f"{hid}: slug repetido {h['slug']}")
        if hid in ids: errores.append(f"{hid}: id repetido")
        if h["nombre"] in nombres: errores.append(f"{hid}: nombre repetido {h['nombre']}")
        slugs.add(h["slug"]); ids.add(hid); nombres.add(h["nombre"])
        for t in h.get("tambienEn", []):
            if t.get("cat") not in CATS or t.get("cat") == c["id"]: errores.append(f"{hid}: tambienEn con cat no válida")

# Nombres usados en otros sitios
for c in d["cats"]:
    for nombre, _ in c["empieza"]["picks"]:
        if nombre not in nombres: errores.append(f"empieza de {c['id']}: '{nombre}' no existe")
for p in d["packs"]:
    for s in p["pasos"]:
        if s["ia"] not in nombres: errores.append(f"pack {p['id']}: '{s['ia']}' no existe")
    if p["total"] != sum(s["precio"] for s in p["pasos"]): errores.append(f"pack {p['id']}: total no cuadra")

html = (RAIZ / "index.html").read_text(encoding="utf-8")
def bloque(nombre):
    i = html.index("const " + nombre)
    return html[i:html.index("];", i)]
for lista in ("STARTER", "ASIST", "INTENTS"):
    for nombre in re.findall(r'\[\s*"([^"]+)"\s*,', bloque(lista)):
        if nombre not in nombres: errores.append(f"index.html {lista}: '{nombre}' no existe")

# Meta y novedades
m = d["meta"]
if m["totalFichas"] != len(ids): errores.append("meta.totalFichas no coincide")
for k in ("ultimaRevision", "proximaRevision"):
    if not FECHA.match(m.get(k, "")): errores.append(f"meta.{k} no válido")
nov = d["novedades"]
if len(nov) > 60: errores.append("Más de 60 novedades")
if [x["fecha"] for x in nov] != sorted((x["fecha"] for x in nov), reverse=True): errores.append("Novedades no ordenadas")
for x in nov:
    if x["ia"] != "Cualia" and x["ia"] not in nombres: avisos.append(f"novedad de '{x['ia']}': no es una ficha actual")

# Historial: solo puede crecer
try:
    viejo = json.loads(subprocess.run(["git", "show", "HEAD:data/historial.json"], cwd=RAIZ,
                                      capture_output=True, text=True, check=True).stdout)
    if H["desde"] != viejo["desde"]: errores.append("historial: 'desde' ha cambiado")
    for k, L in viejo["ias"].items():
        if H["ias"].get(k, [])[:len(L)] != L: errores.append(f"historial: entradas antiguas cambiadas en {k}")
except subprocess.CalledProcessError:
    avisos.append("No se pudo leer el historial de git HEAD para compararlo")
for k in ids:
    if not H["ias"].get(k): errores.append(f"historial: falta la lista de {k}")

for a in avisos[:15]: print("AVISO:", a)
if len(avisos) > 15: print(f"AVISO: ... y {len(avisos) - 15} avisos más")
for e in errores: print("ERROR:", e)
print(f"{len(errores)} errores, {len(avisos)} avisos")
sys.exit(1 if errores else 0)
