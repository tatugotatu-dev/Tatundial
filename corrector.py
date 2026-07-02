#!/usr/bin/env python3
"""
CORRECTOR — Hackathon C++ Champions League
Evaluacion automatica de los 4 ejercicios.
Modo de uso:
    python corrector.py <carpeta_del_alumno>
Ejemplo:
    python corrector.py .\alumno_juan\
(c) 2026 Real C++ FC — Sala VAR
"""

import re
import sys
import os
from pathlib import Path


# ─── RESPUESTAS CORRECTAS ───────────────────────────────────────────────

CORRECTAS = {

    # ── EJERCICIO 1 ──────────────────────────────────────────────────────
    "ej1": {
        "S1": {
            "ub": "SI",
            "tipo": "dangling-reference",
            "linea": "25",
            "justificacion_keywords": ["local", "destruye", "ambito", "stack", "referencia"],
        },
        "S2": {
            "ub": "SI",
            "tipo": "iterator-invalidation",
            "linea": "35",
            "justificacion_keywords": ["invalid", "iterador", "push_back", "realloc"],
        },
        "S3": {
            "ub": "SI",
            "tipo": "data-race",
            "linea": "48",
            "justificacion_keywords": ["hilo", "race", "sincronizacion", "atomic", "mutex", "concurrencia"],
        },
    },

    # ── EJERCICIO 2 ──────────────────────────────────────────────────────
    "ej2": {
        "Q1_lineas": [
            "Posesion: 20 Tiros: 10",
            "Messi (95)",
            "Promedio: 91",
            "Goles contador: 2",
            "UB",
        ],
        "Q1_acepta_var": True,  # acepta variantes como "20 metros" o "20 metros"
        "Q2": {
            "linea": "56",
            "keywords": ["por valor", "referencia", "GoalCounter&", "devolver *this", "encadenamiento"],
            "fix_keywords": ["GoalCounter&", "operator+=", "return *this"],
        },
        "Q3": {
            "linea": "67",
            "keywords": ["division entera", "entero", "trunca", "static_cast", "double"],
            "fix_keywords": ["static_cast<double>", "double", ".0"],
        },
        "Q4": {
            "linea": "90",
            "keywords": ["fuera de rango", "out_of_range", "scores.at", "indice", "bounds", "size()", "undefined"],
            "fix_keywords": [".at(", "size()", "indice"],
        },
    },

    # ── EJERCICIO 3 ──────────────────────────────────────────────────────
    "ej3": {
        "Q1_opcion": "perfect-forwarding",
        "Q2_concept": "PassCallable",
    },

    # ── EJERCICIO 4 ──────────────────────────────────────────────────────
    "ej4": {
        "Q1": {
            "variable": "pressureCount",
            "keywords_ub": ["data race", "read-modify-write", "sin sincronizacion", "varios hilos", "atomic", "mutex"],
        },
        "Q2_keywords": ["lock", "mutex", "serializa", "isNearby", "scope", "costoso", "200000", "sin()"],
        "Q3_opcion": "std::atomic<int> para pressureCount",
        "Q4_keywords": ["std::atomic<int>", "fetch_add"],
    },
}

PUNTAJE_MAX = {
    "ej1": 25,
    "ej2": 25,
    "ej3": 25,
    "ej4": 25,
}


# ─── FUNCIONES DE EXTRACCION ────────────────────────────────────────────

def leer_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def extraer_campo(texto, etiqueta):
    """Extrae el valor de '- <etiqueta>: <valor>' """
    m = re.search(rf"-\s*{re.escape(etiqueta)}\s*:\s*(.+)", texto, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extraer_campo_flex(texto, etiqueta):
    """Extrae campo cuando el nombre puede contener parentesis extra """
    patron = rf"-\s*{re.escape(etiqueta)}.*?:\s*(.+)"
    m = re.search(patron, texto, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extraer_bloque_codigo(texto):
    """Extrae contenido entre ```cpp ... ``` """
    bloques = re.findall(r"```(?:cpp)?\s*(.*?)```", texto, re.DOTALL)
    return bloques


def extraer_respuesta_q1_ej3(texto):
    lines = texto.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("Respuesta:"):
            val = line.split(":", 1)[1].strip().lower()
            if val:
                return val
    return ""


def extraer_lineas_salida(texto):
    """Extrae las lineas del bloque de codigo de Q1 (salida exacta)"""
    bloques = extraer_bloque_codigo(texto)
    if bloques:
        lineas = [l.strip() for l in bloques[0].split("\n") if l.strip()]
        result = []
        for l in lineas:
            if ":" in l:
                result.append(l.split(":", 1)[1].strip())
            else:
                result.append(l)
        return result
    return []


def extraer_checkbox(texto, opcion):
    patron = rf"-\s*\[(x|X| )\]\s*{re.escape(opcion)}"
    m = re.search(patron, texto)
    return m is not None and m.group(1).lower() == "x"


def extraer_opcion_q3_ej4(texto):
    opciones = [
        "std::atomic<int> para pressureCount",
        "mutex solo alrededor del incremento",
        "ambos combinados",
    ]
    for op in opciones:
        if extraer_checkbox(texto, op):
            return op
    return ""


def dividir_por_secciones(texto, prefijo):
    """Divide el texto en secciones por '## <prefijo>N' """
    partes = re.split(rf"(?=##\s+{re.escape(prefijo)}\d)", texto)
    return [p.strip() for p in partes if p.strip()]


# ─── CORRECCION POR EJERCICIO ───────────────────────────────────────────

def corregir_ej1(texto):
    puntaje = 0
    detalles = {}
    secciones = dividir_por_secciones(texto, "S")
    for sn in ["S1", "S2", "S3"]:
        ref = CORRECTAS["ej1"][sn]
        # Encontrar la seccion correspondiente
        sec_texto = ""
        for sec in secciones:
            if sec.startswith(f"## {sn}") or sn in sec:
                sec_texto = sec
                break
        if not sec_texto:
            sec_texto = texto  # fallback

        ub = extraer_campo(sec_texto, "UB").upper()
        tipo = extraer_campo(sec_texto, "Tipo").strip().lower()
        linea = extraer_campo(sec_texto, "Linea").strip()
        just = extraer_campo(sec_texto, "Justificacion").strip().lower()

        pts = 0
        ok_ub = ub == ref["ub"]
        ok_tipo = tipo == ref["tipo"]
        ok_linea = linea == ref["linea"]
        ok_just = any(kw in just for kw in ref["justificacion_keywords"])

        if ok_ub:
            pts += 1
        if ok_tipo:
            pts += 2
        if ok_linea:
            pts += 2
        if ok_just:
            pts += 1

        puntaje += pts
        detalles[sn] = {
            "pts": pts,
            "max": 6,
            "ok_ub": ok_ub,
            "ok_tipo": ok_tipo,
            "ok_linea": ok_linea,
            "ok_just": ok_just,
        }

    puntaje_final = round(puntaje / 18 * 25)
    return min(puntaje_final, 25), detalles


def corregir_ej2(texto):
    puntaje = 0
    detalles = {}

    # Q1 - Salida exacta (10 pts)
    lineas_estudiante = extraer_lineas_salida(texto)
    ref_lineas = CORRECTAS["ej2"]["Q1_lineas"]
    aciertos_lineas = 0
    for i, ref_l in enumerate(ref_lineas):
        if i < len(lineas_estudiante):
            l_est = lineas_estudiante[i].strip()
            if l_est.upper() == "UB" and ref_l == "UB":
                aciertos_lineas += 2
            elif l_est == ref_l:
                aciertos_lineas += 2
    detalles["Q1"] = {"pts": aciertos_lineas, "max": 10, "lineas_esperadas": ref_lineas, "lineas_recibidas": lineas_estudiante}
    puntaje += aciertos_lineas

    # Q2 - GoalCounter (5 pts)
    seccion_q2 = texto.split("## Q2")[-1].split("## Q3")[0] if "## Q3" in texto else texto.split("## Q2")[-1]
    linea_q2 = extraer_campo(seccion_q2, "Linea")
    desc_q2 = extraer_campo(seccion_q2, "Descripcion").lower()
    codigo_q2 = extraer_bloque_codigo(seccion_q2)
    texto_codigo_q2 = codigo_q2[0].lower() if codigo_q2 else ""

    pts_q2 = 0
    ok_q2_linea = linea_q2 == CORRECTAS["ej2"]["Q2"]["linea"]
    ok_q2_desc = any(kw in desc_q2 for kw in CORRECTAS["ej2"]["Q2"]["keywords"])
    ok_q2_fix = any(kw in texto_codigo_q2 for kw in CORRECTAS["ej2"]["Q2"]["fix_keywords"])
    if ok_q2_linea:
        pts_q2 += 1
    if ok_q2_desc:
        pts_q2 += 2
    if ok_q2_fix:
        pts_q2 += 2
    detalles["Q2"] = {"pts": pts_q2, "max": 5, "ok_linea": ok_q2_linea, "ok_desc": ok_q2_desc, "ok_fix": ok_q2_fix}
    puntaje += pts_q2

    # Q3 - averageRating (5 pts)
    seccion_q3 = texto.split("## Q3")[-1].split("## Q4")[0] if "## Q4" in texto else texto.split("## Q3")[-1] if "## Q3" in texto else ""
    if seccion_q3:
        linea_q3 = extraer_campo(seccion_q3, "Linea")
        desc_q3 = extraer_campo(seccion_q3, "Descripcion").lower()
        codigo_q3 = extraer_bloque_codigo(seccion_q3)
        texto_codigo_q3 = codigo_q3[0].lower() if codigo_q3 else ""

        pts_q3 = 0
        ok_q3_linea = linea_q3 == CORRECTAS["ej2"]["Q3"]["linea"]
        ok_q3_desc = any(kw in desc_q3 for kw in CORRECTAS["ej2"]["Q3"]["keywords"])
        ok_q3_fix = any(kw in texto_codigo_q3 for kw in CORRECTAS["ej2"]["Q3"]["fix_keywords"])
        if ok_q3_linea:
            pts_q3 += 1
        if ok_q3_desc:
            pts_q3 += 2
        if ok_q3_fix:
            pts_q3 += 2
        detalles["Q3"] = {"pts": pts_q3, "max": 5, "ok_linea": ok_q3_linea, "ok_desc": ok_q3_desc, "ok_fix": ok_q3_fix}
        puntaje += pts_q3

    # Q4 - scores (5 pts)
    seccion_q4 = texto.split("## Q4")[-1] if "## Q4" in texto else ""
    if seccion_q4:
        linea_q4 = extraer_campo(seccion_q4, "Linea")
        desc_q4 = extraer_campo(seccion_q4, "Descripcion").lower()
        codigo_q4 = extraer_bloque_codigo(seccion_q4)
        texto_codigo_q4 = codigo_q4[0].lower() if codigo_q4 else ""

        pts_q4 = 0
        ok_q4_linea = linea_q4 == CORRECTAS["ej2"]["Q4"]["linea"]
        ok_q4_desc = any(kw in desc_q4 for kw in CORRECTAS["ej2"]["Q4"]["keywords"])
        ok_q4_fix = any(kw in texto_codigo_q4 for kw in CORRECTAS["ej2"]["Q4"]["fix_keywords"])
        if ok_q4_linea:
            pts_q4 += 1
        if ok_q4_desc:
            pts_q4 += 2
        if ok_q4_fix:
            pts_q4 += 2
        detalles["Q4"] = {"pts": pts_q4, "max": 5, "ok_linea": ok_q4_linea, "ok_desc": ok_q4_desc, "ok_fix": ok_q4_fix}
        puntaje += pts_q4

    return min(puntaje, 25), detalles


def corregir_ej3(texto):
    puntaje = 0
    detalles = {}

    # Q1 (10 pts)
    q1_text = extraer_respuesta_q1_ej3(texto)
    # Tambien buscar en linea de "Respuesta:"
    if not q1_text:
        # Buscar mas exhaustivamente
        lines = texto.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("Respuesta:"):
                q1_text = line.split(":", 1)[1].strip().lower()
                break

    opcion_correcta = CORRECTAS["ej3"]["Q1_opcion"]
    ok_q1 = q1_text == opcion_correcta
    detalles["Q1"] = {"pts": 10 if ok_q1 else 0, "max": 10, "esperado": opcion_correcta, "recibido": q1_text}
    puntaje += 10 if ok_q1 else 0

    # Q2 (15 pts)
    codigos = extraer_bloque_codigo(texto)
    texto_concept = " ".join(codigos).lower()
    # Verificar que define PassCallable
    ok_nombre = "passcallable" in texto_concept
    ok_invocable = "invocable" in texto_concept or "std::invocable" in texto_concept
    ok_retorno = "same_as" in texto_concept or "convertible_to" in texto_concept or "not" in texto_concept
    ok_not_void = "void" in texto_concept

    pts_q2 = 0
    if ok_nombre:
        pts_q2 += 5
    if ok_invocable:
        pts_q2 += 4
    if ok_retorno:
        pts_q2 += 3
    if ok_not_void:
        pts_q2 += 3

    detalles["Q2"] = {
        "pts": pts_q2, "max": 15,
        "ok_nombre": ok_nombre,
        "ok_invocable": ok_invocable,
        "ok_retorno": ok_retorno,
        "ok_not_void": ok_not_void,
    }
    puntaje += pts_q2

    return min(puntaje, 25), detalles


def corregir_ej4(texto):
    puntaje = 0
    detalles = {}

    # Q1 (10 pts)
    seccion_q1 = texto.split("## Q1")[-1].split("## Q2")[0] if "## Q2" in texto else texto.split("## Q1")[-1]
    variable = extraer_campo_flex(seccion_q1, "Variable").lower()
    por_que = extraer_campo_flex(seccion_q1, "Por que es UB").lower()
    ref_var = CORRECTAS["ej4"]["Q1"]["variable"].lower()
    ok_var = ref_var in variable
    ok_ub = any(kw in por_que for kw in CORRECTAS["ej4"]["Q1"]["keywords_ub"])

    pts_q1 = (5 if ok_var else 0) + (5 if ok_ub else 0)
    detalles["Q1"] = {"pts": pts_q1, "max": 10, "ok_variable": ok_var, "ok_ub": ok_ub}
    puntaje += pts_q1

    # Q2 (5 pts)
    seccion_q2 = texto.split("## Q2")[-1].split("## Q3")[0] if "## Q3" in texto else texto.split("## Q2")[-1]
    resp_q2 = seccion_q2.lower()
    ok_q2 = any(kw in resp_q2 for kw in CORRECTAS["ej4"]["Q2_keywords"])
    detalles["Q2"] = {"pts": 5 if ok_q2 else 0, "max": 5, "ok": ok_q2}
    puntaje += 5 if ok_q2 else 0

    # Q3 (5 pts)
    opcion = extraer_opcion_q3_ej4(texto)
    ok_q3 = opcion == CORRECTAS["ej4"]["Q3_opcion"]
    detalles["Q3"] = {"pts": 5 if ok_q3 else 0, "max": 5, "esperado": CORRECTAS["ej4"]["Q3_opcion"], "recibido": opcion}
    puntaje += 5 if ok_q3 else 0

    # Q4 (5 pts)
    codigos = extraer_bloque_codigo(texto)
    texto_q4 = " ".join(codigos).lower()
    ok_atomic = "atomic<int>" in texto_q4 or "atomic_int" in texto_q4
    ok_fetch = "fetch_add" in texto_q4
    pts_q4 = (3 if ok_atomic else 0) + (2 if ok_fetch else 0)
    detalles["Q4"] = {"pts": pts_q4, "max": 5, "ok_atomic": ok_atomic, "ok_fetch": ok_fetch}
    puntaje += pts_q4

    return min(puntaje, 25), detalles


# ─── MAIN ───────────────────────────────────────────────────────────────

def procesar_alumno(carpeta):
    carpeta = Path(carpeta)
    if not carpeta.is_dir():
        print(f"ERROR: '{carpeta}' no es una carpeta valida.")
        return

    resultados = {}
    puntaje_total = 0

    for ej, archivo, fn_corrector in [
        ("ej1", "exercise1_offside_trap/ANSWER.md", corregir_ej1),
        ("ej2", "exercise2_var_review/ANSWER.md", corregir_ej2),
        ("ej3", "exercise3_tiki_taka_api/ANSWER.md", corregir_ej3),
        ("ej4", "exercise4_press_high/ANSWER.md", corregir_ej4),
    ]:
        ruta = carpeta / archivo
        texto = leer_archivo(ruta)
        if not texto:
            print(f"  {ej}: Archivo no encontrado -> 0/{PUNTAJE_MAX[ej]}")
            resultados[ej] = {"pts": 0, "max": PUNTAJE_MAX[ej], "detalle": "Archivo no encontrado"}
            continue

        pts, detalle = fn_corrector(texto)
        resultados[ej] = {"pts": pts, "max": PUNTAJE_MAX[ej], "detalle": detalle}
        puntaje_total += pts

    return resultados, puntaje_total


def imprimir_resultados(resultados, puntaje_total):
    print("=" * 60)
    print("  CORRECTOR - HACKATHON C++ CHAMPIONS LEAGUE")
    print("=" * 60)

    for ej in ["ej1", "ej2", "ej3", "ej4"]:
        r = resultados[ej]
        nombre = {
            "ej1": "Ej1 - Offside Trap (UB)",
            "ej2": "Ej2 - VAR Review (Debugging)",
            "ej3": "Ej3 - Tiki-Taka API (Concepts)",
            "ej4": "Ej4 - Press High (Concurrencia)",
        }[ej]
        print(f"\n  {nombre}")
        print(f"  {'=' * 40}")
        print(f"  Puntaje: {r['pts']}/{r['max']}")

        det = r["detalle"]
        if isinstance(det, str):
            print(f"  {det}")
        elif isinstance(det, dict):
            for sub, info in det.items():
                if isinstance(info, dict):
                    sub_pts = info.get("pts", 0)
                    sub_max = info.get("max", 1)
                    barra = "  " + "=" * sub_pts + "." * (sub_max - sub_pts)
                    # Mostrar detalles relevantes
                    extras = []
                    for k, v in info.items():
                        if k.startswith("ok_") and isinstance(v, bool):
                            extras.append(f"{k[3:]}: {'OK' if v else 'X'}")
                    if extras:
                        print(f"    {sub}: {sub_pts}/{sub_max} [{', '.join(extras)}]")
                    else:
                        print(f"    {sub}: {sub_pts}/{sub_max}")
                    if "lineas_esperadas" in info and "lineas_recibidas" in info:
                        print(f"      Esperado: {info['lineas_esperadas']}")
                        print(f"      Recibido: {info['lineas_recibidas']}")

    print(f"\n  {'=' * 40}")
    print(f"  TOTAL: {puntaje_total}/100")
    print(f"  {'=' * 40}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python corrector.py <carpeta_del_alumno>")
        print("     python corrector.py .")
        sys.exit(1)

    carpeta = sys.argv[1]
    resultados, puntaje_total = procesar_alumno(carpeta)
    imprimir_resultados(resultados, puntaje_total)


if __name__ == "__main__":
    main()
