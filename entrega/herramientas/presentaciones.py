"""Genera las presentaciones de Avance 1 y Avance 2 con las cifras reales del pipeline.
Uso: python presentaciones.py <carpeta_entrega>
"""
import json, os, sys
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
AZUL, GRIS, BLANCO = RGBColor(0x1F, 0x3A, 0x5F), RGBColor(0x40, 0x40, 0x40), RGBColor(255, 255, 255)

def nueva():
    p = Presentation(); p.slide_width, p.slide_height = Inches(13.33), Inches(7.5); return p

def texto(s, x, y, w, h, lineas, tam=16, color=GRIS, negrita=False, mono=False):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame; tf.word_wrap = True
    for i, l in enumerate(lineas):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.text = l; par.font.size = Pt(tam); par.font.color.rgb = color; par.font.bold = negrita
        par.font.name = "Consolas" if mono else "Calibri"; par.space_after = Pt(3)

def lamina(p, titulo, notas=""):
    s = p.slides.add_slide(p.slide_layouts[6])
    b = s.shapes.add_shape(1, 0, 0, p.slide_width, Inches(1.0)); b.fill.solid(); b.fill.fore_color.rgb = AZUL; b.line.fill.background()
    texto(s, 0.5, 0.15, 12, 0.8, [titulo], 28, BLANCO, True)
    if notas: s.notes_slide.notes_text_frame.text = notas
    return s

def tabla(s, x, y, w, filas, tam=12, anchos=None):
    t = s.shapes.add_table(len(filas), len(filas[0]), Inches(x), Inches(y), Inches(w), Inches(0.35 * len(filas))).table
    for i, fila in enumerate(filas):
        for j, v in enumerate(fila):
            c = t.cell(i, j); c.text = str(v)
            for par in c.text_frame.paragraphs:
                par.font.size = Pt(tam); par.font.name = "Calibri"; par.font.bold = (i == 0)
                par.font.color.rgb = BLANCO if i == 0 else GRIS
            c.fill.solid(); c.fill.fore_color.rgb = AZUL if i == 0 else (RGBColor(0xF2, 0xF5, 0xF9) if i % 2 else BLANCO)
    if anchos:
        for j, a in enumerate(anchos): t.columns[j].width = Inches(a)

def portada(p, sub):
    s = p.slides.add_slide(p.slide_layouts[6])
    f = s.shapes.add_shape(1, 0, 0, p.slide_width, p.slide_height); f.fill.solid(); f.fill.fore_color.rgb = AZUL; f.line.fill.background()
    texto(s, 0.8, 2.2, 11.5, 1.5, ["Comportamiento Climático Integrado"], 40, BLANCO, True)
    texto(s, 0.8, 3.6, 11.5, 2.8, [sub, "Patricio Parra · Benjamín Carrillo · Simón Leiva",
          "Programación Avanzada · Secciones 1 y 2 · Profesor Alex", "2 de noviembre de 2026"], 20, BLANCO)

n = lambda x: f"{x:,}".replace(",", ".")
m = json.load(open(os.path.join(BASE, "avance_2/reportes/metricas_avance_2.json"), encoding="utf-8"))
AC, A, D = m["antes_completo"], m["antes"], m["despues"]
tn = {r["variable"]: r for r in m["tabla_nulos"]}
sel = [c for c in A["nulos"] if c not in ("fecha", "estacion")]
na, nd = sum(A["nulos"].values()), sum(D["nulos"][c] for c in A["nulos"])

# ---------------- Avance 2 ----------------
p = nueva(); portada(p, "Avance 2 · Limpieza, nulos y transformación de datos")
s = lamina(p, "Diagnóstico de calidad de datos", "Integrante 1. Explicar con palabras propias: de dónde vienen los datos, cuánto pesan y cuál fue el problema principal (los nulos). No leer la lámina.")
texto(s, 0.5, 1.2, 6.3, 1.8, ["Proyecto 4: comportamiento climático integrado", "Fuente: Oficina de Meteorología de Australia (weatherAUS)",
      f"Registros iniciales: {n(AC['filas'])}", f"Variables iniciales: {AC['columnas']} (14 seleccionadas)"], 15)
tabla(s, 0.5, 3.1, 6.1, [["Problema detectado", "Cantidad encontrada"], ["Valores nulos (23 columnas)", n(AC["nulos_total"])],
      ["Valores nulos (14 seleccionadas)", n(na)], ["Registros sin ninguna medición", n(A["filas_sin_datos_climaticos"])], ["Filas duplicadas", n(A["duplicados"])],
      ["Categorías inconsistentes", n(A["categorias_inconsistentes"])], ["Valores fuera de rango", n(A["fuera_de_rango_total"])]], 13, [3.8, 2.3])
texto(s, 7.0, 1.2, 6, 0.4, ["Evidencia: df.isnull().sum() (variables seleccionadas)"], 13, AZUL, True)
texto(s, 7.0, 1.6, 6, 4.8, [f"{c:<14}{A['nulos'][c]:>7}" for c in A["nulos"]], 12, mono=True)
texto(s, 0.5, 6.0, 6.3, 1.2, ["Principal problema: valores faltantes, sobre todo en presión (10,4%) y en las columnas de nubosidad, evaporación y sol (38% a 48%)."], 14, AZUL, True)

s = lamina(p, "Acciones realizadas sobre los datos", "Integrantes 2 y 3. Justificar cada decisión y explicar por qué mejora el análisis posterior. No leer las tablas.")
tabla(s, 0.4, 1.2, 8.0, [["Problema", "Acción aplicada", "Justificación"],
  ["Columnas con 38% a 48% de nulos", "Descartar 9 columnas", "No responden la pregunta"],
  [f"{A['filas_sin_datos_climaticos']} registros sin mediciones", "Eliminación", "No tienen información"],
  ["Nulos en temp., humedad y presión", "Interpolación + mediana estación-mes", "Variables continuas"],
  ["Nulos en viento y ráfaga", "Mediana por estación y mes", "Distribución asimétrica"],
  ["Nulos en dirección de ráfaga", "Categoría «desconocido»", "Variable categórica"],
  ["Estaciones sin sensor de presión", "Mantener nulo", "Imputar sería inventar"],
  ["Duplicados y fuera de rango", "Sin acción (0 casos)", "Verificados en el código"]], 11, [2.9, 2.9, 2.2])
def grupo(prefijos):
    f = [tn[v] for v in tn if v.startswith(prefijos)]; return sum(x["nulos_iniciales"] for x in f), sum(x["nulos_finales"] for x in f)
filas = [["Variable", "Nulos iniciales", "Estrategia", "Nulos finales"]]
for nombre, pref, est in [("Temperatura (4)", "temp", "Interpolación + mediana"), ("Humedad (2)", "humedad", "Interpolación + mediana"), ("Presión (2)", "presion", "Interpolación + mediana"),
                          ("Viento y ráfaga (3)", ("viento", "rafaga"), "Mediana"), ("Dirección ráfaga", "dir_", "«desconocido»")]:
    i, fi = grupo(pref); filas.append([nombre, n(i), est, n(fi)])
tabla(s, 8.6, 1.2, 4.5, filas, 10, [1.3, 0.9, 1.4, 0.9])
texto(s, 0.4, 4.4, 12.5, 3, ["Transformaciones realizadas (7):", "• Conversión de fechas: df[\"fecha\"] = pd.to_datetime(df[\"fecha\"])",
  "• Componentes temporales: df[\"anio\"] = df[\"fecha\"].dt.year  y  df[\"mes\"] = df[\"fecha\"].dt.month",
  "• Nuevas variables: amplitud_termica = temp_max - temp_min;  rafaga_ms = rafaga_max / 3.6;  estacion_anio",
  "• Clasificación por rangos: rango_temperatura con pd.cut()",
  "Los nulos restantes en presión y ráfaga son de estaciones que nunca midieron la variable."], 14)

s = lamina(p, "Dataset limpio y preparado para el análisis", "Integrante 4. Mostrar el df.sample(5) real y responder las preguntas de aprendizaje con experiencia propia del equipo.")
tabla(s, 0.5, 1.2, 5.6, [["Indicador", "Antes", "Después"], ["Registros", n(A["filas"]), n(D["filas"])], ["Variables", AC["columnas"], D["columnas"]],
      ["Nulos (14 variables)", n(na), n(nd)], ["Duplicados", n(A["duplicados"]), n(D["duplicados"])], ["Fuera de rango", n(A["fuera_de_rango_total"]), n(D["fuera_de_rango_total"])]], 13, [2.6, 1.5, 1.5])
texto(s, 6.5, 1.2, 6.5, 3, ["Aprendizajes", "• Lo más difícil: decidir qué hacer con la presión, porque hay estaciones que nunca la miden.",
  "• Mayor impacto: tratar los nulos según el tipo de variable en vez de usar un solo método.",
  "• Haríamos distinto: comparar la imputación con otras estrategias y medir cuánto cambia la variabilidad."], 14)
mu = pd.read_csv(os.path.join(BASE, "avance_2/datos/procesados/dataset_limpio.csv")).sample(5, random_state=1)
mu = mu[["fecha", "estacion", "temp_max", "humedad_15h", "presion_15h", "viento_15h", "estacion_anio", "rango_temperatura"]]
texto(s, 0.5, 4.1, 12.3, 0.4, ["Evidencia: df.sample(5) del dataset limpio"], 14, AZUL, True)
texto(s, 0.5, 4.5, 12.3, 2, mu.to_string(index=False).split("\n"), 11, mono=True)
p.save(os.path.join(BASE, "avance_2/reportes/presentacion_avance_2.pptx"))

# ---------------- Avance 1 ----------------
p = nueva(); portada(p, "Avance 1 · Definición del problema y carga inicial")
s = lamina(p, "Problema, pregunta y objetivos", "Integrante 1. Explicar el contexto con palabras propias, sin leer.")
texto(s, 0.5, 1.2, 12.3, 5.8, ["Contexto: el clima se mide con varias variables que suelen analizarse por separado.",
  "Necesidad: un proceso reproducible que cargue, revise y compare temperatura, humedad, presión y viento.",
  "Pregunta: ¿qué variable climática presenta mayores cambios en el tiempo?",
  "Objetivo general: identificar qué variable varía más, con un pipeline en Python y Pandas.",
  "Objetivos específicos:", "   • Documentar estructura y calidad del dataset.", "   • Calcular indicadores estadísticos por variable.",
  "   • Comparar la variación de las cuatro variables y generar reportes automáticos.",
  "Usuarios: estudiantes, investigadores y organizaciones agrícolas o energéticas."], 18)
s = lamina(p, "Fuente de datos y diccionario", "Integrante 2. Justificar por qué la fuente sirve y mostrar las variables.")
tabla(s, 0.4, 1.2, 5.9, [["Elemento", "Información"], ["Dataset", "weatherAUS (Rain in Australia)"], ["Responsable", "Oficina de Meteorología de Australia"],
  ["Formato", "CSV, observaciones diarias"], ["Registros", n(AC["filas"])], ["Variables", f"{AC['columnas']} (14 usadas)"], ["Período", "2007-11-01 a 2017-06-25"],
  ["Estaciones", "49"], ["Licencia", "Uso académico con cita de la fuente"], ["Limitación", "Muchos nulos; estaciones sin presión"]], 12, [1.7, 4.2])
tabla(s, 6.6, 1.2, 6.4, [["Variable", "Descripción", "Unidad"], ["Date", "Fecha de observación", "AAAA-MM-DD"], ["Location", "Estación", "Texto"],
  ["MinTemp, MaxTemp", "Temperatura mínima y máxima", "°C"], ["Temp9am, Temp3pm", "Temperatura a las 9 y 15 h", "°C"], ["Humidity9am, 3pm", "Humedad relativa", "%"],
  ["Pressure9am, 3pm", "Presión atmosférica", "hPa"], ["WindSpeed9am, 3pm", "Velocidad del viento", "km/h"], ["WindGustSpeed", "Ráfaga máxima", "km/h"], ["WindGustDir", "Dirección de la ráfaga", "Categoría"]], 12, [2.2, 2.9, 1.3])
s = lamina(p, "Pipeline y carga inicial con Pandas", "Integrante 3. Mostrar el pipeline completo y la salida real de main.py (Avance 1).")
texto(s, 0.5, 1.2, 5.6, 5.5, ["Fuente → Descarga → datos/", "→ Carga con Pandas → Validación", "→ Limpieza y transformación", "→ Análisis exploratorio → Visualización", "→ Interpretación → Informe final",
  "", "src/carga.py: cargar_datos() con control de errores e inspeccionar_datos().", "main.py las ejecuta desde la raíz."], 16)
texto(s, 6.5, 1.2, 6.5, 0.4, ["Evidencia: salida real de python main.py"], 13, AZUL, True)
texto(s, 6.5, 1.6, 6.5, 5.5, [f"Dimensiones: ({AC['filas']}, {AC['columnas']})", f"Nulos totales: {n(AC['nulos_total'])}", f"Filas duplicadas: {AC['duplicados']}", "Nulos por columna (mayores):",
  "  Sunshine       69835", "  Evaporation    62790", "  Cloud3pm       59358", "  Cloud9am       55888", "  Pressure9am    15065", "  Pressure3pm    15028"], 13, mono=True)
p.save(os.path.join(BASE, "avance_1/reportes/presentacion_avance_1.pptx"))
print("Presentaciones generadas")
