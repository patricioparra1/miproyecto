"""Genera avance_1.pdf y avance_2.pdf con las cifras reales del pipeline.
Uso: python informes.py <carpeta_entrega> <salida_avance_1.txt> <salida_avance_2.txt>
"""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle)

BASE, SAL1, SAL2 = sys.argv[1], sys.argv[2], sys.argv[3]
INSTITUCION = "[Nombre de la institución]"
REPO = "[Enlace al repositorio de GitHub]"
ASIGNATURA = "Programación Avanzada"
TITULO = "Comportamiento Climático Integrado"
FECHA = "2 de noviembre de 2026"
INTEGRANTES = ["Patricio Parra", "Benjamín Carrillo", "Simón Leiva"]
AZUL = colors.HexColor("#1F3A5F")

ss = getSampleStyleSheet()
cuerpo = ParagraphStyle("c", parent=ss["BodyText"], fontName="Helvetica", fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15, textColor=AZUL, spaceBefore=12, spaceAfter=8, keepWithNext=1)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, textColor=AZUL, spaceBefore=8, spaceAfter=4, keepWithNext=1)
celda = ParagraphStyle("t", fontName="Helvetica", fontSize=8, leading=10)
celda_h = ParagraphStyle("th", parent=celda, fontName="Helvetica-Bold", textColor=colors.white)
pie = ParagraphStyle("p", parent=cuerpo, fontSize=8.5, textColor=colors.grey, alignment=TA_CENTER)
cod = ParagraphStyle("cod", fontName="Courier", fontSize=7, leading=8.4)

def P(t, e=cuerpo): return Paragraph(t, e)
def tabla(filas, anchos, fuente=None):
    datos = [[Paragraph(str(c), celda_h if i == 0 else celda) for c in f] for i, f in enumerate(filas)]
    t = Table(datos, colWidths=[a * cm for a in anchos], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C2CC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F9")]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return [t, Spacer(1, 8)]
def codigo(txt): return [Preformatted(txt, cod, maxLineLength=130), Spacer(1, 8)]
def n(x): return f"{x:,}".replace(",", ".")
def lista(items): return [P("&bull; " + i) for i in items]

def numerar(c, doc):
    c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawCentredString(A4[0] / 2, 1.2 * cm, f"{TITULO} - {ASIGNATURA} - pág. {doc.page}")

def portada(avance, subtitulo):
    e = [Spacer(1, 2 * cm), P(f"<b>{INSTITUCION}</b>", ParagraphStyle("x", parent=cuerpo, fontSize=14, alignment=TA_CENTER)),
         P(ASIGNATURA, ParagraphStyle("x", parent=cuerpo, fontSize=12, alignment=TA_CENTER)), Spacer(1, 3 * cm),
         P(f"<b>{TITULO}</b>", ParagraphStyle("t", parent=cuerpo, fontSize=26, leading=32, alignment=TA_CENTER, textColor=AZUL)),
         P(f"Proyecto 4 · Avance {avance}", ParagraphStyle("x", parent=cuerpo, fontSize=14, alignment=TA_CENTER)),
         P(subtitulo, ParagraphStyle("x", parent=cuerpo, fontSize=12, alignment=TA_CENTER)), Spacer(1, 3 * cm)]
    e += tabla([["Integrantes", "<br/>".join(INTEGRANTES)], ["Sección", "Secciones 1 y 2"], ["Docente", "Alex"],
                ["Fecha de entrega", FECHA], ["Repositorio", REPO]], [4, 11])
    return e + [PageBreak()]

def figura(ruta, ancho=15): 
    from PIL import Image as PI
    w, h = PI.open(ruta).size
    return [Image(ruta, width=ancho * cm, height=ancho * cm * h / w), Spacer(1, 6)]

def diagrama_pipeline(ruta):
    etapas = ["Fuente de datos\n(BoM Australia)", "Descarga y\nalmacenamiento\ndatos/", "Carga\ncon Pandas", "Validación de\nestructura", "Limpieza y\ntransformación",
              "Análisis\nexploratorio", "Visualización", "Interpretación", "Informe final"]
    fig, ax = plt.subplots(figsize=(10, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3.6)
    pos = [(0.6 + i * 2.2, 2.6) for i in range(5)] + [(0.6 + 1.1 + i * 2.2, 0.9) for i in range(4)]
    for (x, y), t in zip(pos, etapas):
        ax.add_patch(FancyBboxPatch((x - 0.9, y - 0.5), 1.8, 1.0, boxstyle="round,pad=0.03", fc="#E8EEF6", ec="#1F3A5F"))
        ax.text(x, y, t, ha="center", va="center", fontsize=7.5)
    for i in range(8):
        (x1, y1), (x2, y2) = pos[i], pos[i + 1]
        if i == 4: ax.annotate("", xy=(x2 + 0.9, y2 + 0.5), xytext=(x1 - 0.2, y1 - 0.5), arrowprops=dict(arrowstyle="->", color="#1F3A5F"))
        else: ax.annotate("", xy=(x2 - 0.92, y2), xytext=(x1 + 0.92, y1), arrowprops=dict(arrowstyle="->", color="#1F3A5F"))
    fig.savefig(ruta, dpi=200, bbox_inches="tight"); plt.close(fig)

EXCLUIR_A1 = "Resumen estadistico"
sal1 = open(SAL1, encoding="utf-8").read().split(EXCLUIR_A1)[0].rstrip() + "\n\nResumen estadistico: (omitido en el informe por su extension)"
sal2 = open(SAL2, encoding="utf-8").read()
m = json.load(open(os.path.join(BASE, "avance_2/reportes/metricas_avance_2.json"), encoding="utf-8"))
A, AC, D = m["antes"], m["antes_completo"], m["despues"]
os.makedirs("/tmp/figs", exist_ok=True)

# =================== AVANCE 1 ===================
diagrama_pipeline("/tmp/figs/pipeline.png")
e = portada(1, "Definición del problema y carga inicial de datos con Pandas")
e += [P("1. Descripción del problema", h1),
 P("<b>Contexto.</b> Los cambios ambientales se reflejan en variables que se miden todos los días: la temperatura, la humedad del aire, la presión atmosférica y la velocidad del viento. Cada una se registra en estaciones meteorológicas, pero suele revisarse por separado, lo que dificulta saber cuál de ellas varía más y cómo se comparan entre sí."),
 P("<b>Organización y proceso.</b> El proyecto trabaja con las observaciones de la red de estaciones de la Oficina de Meteorología de Australia (Bureau of Meteorology), organismo público que registra y publica datos del tiempo atmosférico. El proceso estudiado es la medición diaria en cada estación y su consolidación en archivos tabulares para el análisis."),
 P("<b>Necesidad detectada.</b> Los datos existen, pero no están listos para analizarse: los nombres de las columnas están en inglés, las fechas se leen como texto, hay una gran cantidad de valores faltantes y las variables se miden a distintas horas del día. Se necesita un proceso programado y reproducible que cargue los datos, los revise, los prepare y entregue indicadores comparables entre variables."),
 P("<b>Pregunta principal.</b> ¿Qué variable climática presenta mayores cambios en el tiempo?"),
 P("<b>Objetivo general.</b> Analizar los registros diarios de temperatura, humedad, presión y velocidad del viento para identificar cuál de ellas presenta mayor variación a lo largo del tiempo, mediante un pipeline desarrollado en Python y Pandas."),
 P("<b>Objetivos específicos.</b>")] + lista([
 "Cargar el dataset y documentar su estructura, sus tipos de datos y su calidad inicial.",
 "Calcular indicadores estadísticos (promedio, desviación estándar y rango) de cada variable.",
 "Comparar la variación de las cuatro variables con medidas comparables entre sí, como el coeficiente de variación.",
 "Generar reportes de forma automática a partir del código."]) + [
 P("<b>Usuarios potenciales.</b> Estudiantes e investigadores de ciencias ambientales, equipos de meteorología y organizaciones agrícolas o energéticas que necesiten conocer el comportamiento del clima."),
 P("<b>Decisiones que se pueden apoyar.</b> Definir qué variable conviene monitorear con mayor frecuencia, identificar en qué estaciones del año se requiere más planificación en actividades al aire libre o agrícolas, y detectar qué estaciones de medición necesitan revisión por falta de datos."),
 P("2. Fuente de datos", h1),
 P("Se utiliza el conjunto <i>weatherAUS</i>, que reúne observaciones diarias de 49 estaciones de Australia. Es adecuado porque contiene las cuatro variables del proyecto, cubre casi diez años y presenta problemas reales de calidad (valores faltantes, columnas innecesarias, fechas como texto) que permiten construir un proceso de limpieza completo.")]
e += tabla([["Elemento", "Información del proyecto"],
 ["Nombre del conjunto de datos", "weatherAUS (Rain in Australia)"],
 ["Organización responsable", "Oficina de Meteorología de Australia (Bureau of Meteorology). Versión distribuida en Kaggle"],
 ["URL o ubicación del archivo", "https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package. Copia usada: https://github.com/acakin/weatherAUS. En el repositorio del proyecto: datos/weatherAUS.csv"],
 ["Fecha de consulta", "2 de noviembre de 2026"],
 ["Formato", "CSV separado por comas, valores faltantes como NA"],
 ["Cantidad aproximada de registros", f"{n(AC['filas'])}"],
 ["Cantidad de variables", f"{AC['columnas']} (se documentan 14 en el diccionario)"],
 ["Período cubierto", "1 de noviembre de 2007 al 25 de junio de 2017"],
 ["Licencia o condición de uso", "Datos de la Oficina de Meteorología de Australia. Uso académico citando la fuente; no contienen datos personales"],
 ["Frecuencia de actualización", "Sin actualización: es un archivo histórico cerrado en 2017"],
 ["Limitaciones detectadas", "Muchos valores faltantes; 4 estaciones sin presión y 2 sin ráfaga; mediciones solo a las 9 am y 3 pm; el período de 10 años no permite hablar de cambio climático de largo plazo; es una copia de terceros de los datos oficiales"]], [4.5, 12])
e += [P("3. Diccionario de datos", h1),
 P("El dataset tiene 23 columnas. Se documentan las 14 que se usarán, porque corresponden a las cuatro variables del proyecto más las claves de fecha y estación. Se descartan las columnas de lluvia, evaporación, horas de sol y nubosidad por no relacionarse con la pregunta, y porque evaporación, sol y nubosidad tienen entre 38% y 48% de datos faltantes.")]
dic = [["Variable", "Descripción", "Tipo original", "Tipo esperado", "Unidad o formato", "Valores permitidos", "¿Nulos?", "Ejemplo"],
 ["Date", "Fecha de la observación", "str", "datetime64", "AAAA-MM-DD", "Fechas válidas", "No", "2008-12-01"],
 ["Location", "Estación meteorológica", "str", "str (categoría)", "Nombre", "49 estaciones", "No", "Albury"],
 ["MinTemp", "Temperatura mínima del día", "float64", "float64", "°C", "-15 a 50", "Sí", "13.4"],
 ["MaxTemp", "Temperatura máxima del día", "float64", "float64", "°C", "-15 a 55", "Sí", "22.9"],
 ["Temp9am", "Temperatura a las 9 am", "float64", "float64", "°C", "-15 a 50", "Sí", "16.9"],
 ["Temp3pm", "Temperatura a las 3 pm", "float64", "float64", "°C", "-15 a 55", "Sí", "21.8"],
 ["Humidity9am", "Humedad relativa a las 9 am", "float64", "float64", "%", "0 a 100", "Sí", "71"],
 ["Humidity3pm", "Humedad relativa a las 3 pm", "float64", "float64", "%", "0 a 100", "Sí", "22"],
 ["Pressure9am", "Presión atmosférica a las 9 am", "float64", "float64", "hPa", "900 a 1100", "Sí", "1007.7"],
 ["Pressure3pm", "Presión atmosférica a las 3 pm", "float64", "float64", "hPa", "900 a 1100", "Sí", "1007.1"],
 ["WindSpeed9am", "Velocidad del viento a las 9 am", "float64", "float64", "km/h", "0 a 150", "Sí", "20"],
 ["WindSpeed3pm", "Velocidad del viento a las 3 pm", "float64", "float64", "km/h", "0 a 150", "Sí", "24"],
 ["WindGustSpeed", "Ráfaga máxima del día", "float64", "float64", "km/h", "0 a 200", "Sí", "44"],
 ["WindGustDir", "Dirección de la ráfaga máxima", "str", "str (categoría)", "16 puntos cardinales", "N, NNE, NE, ..., NNW", "Sí", "W"]]
e += tabla(dic, [2.3, 3.2, 1.5, 1.8, 1.9, 2.2, 1.2, 1.9]) + [
 P("Variables numéricas: temperaturas, humedades, presiones y velocidades. Categóricas: Location y WindGustDir. De fecha: Date. No hay variables booleanas ni identificadores únicos; el registro se identifica por la combinación Date y Location. No existen códigos especiales: los faltantes aparecen como NA. Como posibles errores de formato, Date llega como texto y los nombres de columnas están en inglés y en formato mixto."),
 P("4. Diseño del pipeline", h1)]
e += figura("/tmp/figs/pipeline.png", 16)
e += tabla([["Etapa", "Entrada", "Proceso", "Salida", "Herramienta"],
 ["Obtención", "Fuente original", "Descargar el CSV desde Kaggle o GitHub", "datos/weatherAUS.csv", "Navegador / git"],
 ["Carga", "Archivo CSV", "Leer archivo con control de errores", "DataFrame", "Pandas"],
 ["Validación", "DataFrame", "Revisar columnas, tipos, nulos y duplicados", "Diagnóstico inicial", "Pandas"],
 ["Limpieza", "Datos originales", "Seleccionar columnas, tratar nulos y duplicados", "Datos limpios", "Pandas"],
 ["Análisis", "Datos limpios", "Calcular indicadores por variable", "Resultados", "Pandas"],
 ["Visualización", "Resultados", "Crear gráficos comparativos", "Figuras", "Matplotlib"],
 ["Reporte", "Resultados y figuras", "Interpretar hallazgos", "Informe final", "PDF"]], [2.3, 2.7, 5.2, 3.2, 3])
e += [P("Justificación de las decisiones del diseño", h2)] + lista([
 "<b>Fuente:</b> contiene las cuatro variables del proyecto, es verificable y su volumen (145 mil registros) permite análisis estadísticos con sentido.",
 "<b>Almacenamiento:</b> el archivo original se guarda sin modificar en datos/ y los resultados se escribirán en una carpeta aparte. Pesa 14 MB, por lo que cabe en GitHub.",
 "<b>Validación de columnas:</b> se comparará la lista de columnas leídas con la esperada, y se revisarán tipos y rangos físicos de cada variable.",
 "<b>Valores faltantes:</b> se tratarán según el tipo de variable (interpolación o mediana para las numéricas, categoría &quot;desconocido&quot; para las categóricas) y nunca con ceros.",
 "<b>Transformaciones esperadas:</b> convertir la fecha a datetime, renombrar columnas, extraer año y mes, y clasificar la temperatura por rangos.",
 "<b>Resultados esperados:</b> indicadores por variable, comparación de su variabilidad y reportes generados desde el código."])
e += [P("5. Carga inicial con Pandas", h1),
 P("La carga está en <font name='Courier'>src/carga.py</font>. La función <font name='Courier'>cargar_datos(ruta)</font> lee el CSV con <font name='Courier'>pd.read_csv</font>, devuelve un DataFrame y controla los errores de archivo inexistente, archivo vacío, formato ilegible y codificación. La función <font name='Courier'>inspeccionar_datos(datos)</font> muestra dimensiones, columnas, tipos, primeros registros, nulos, duplicados y resumen estadístico. El archivo <font name='Courier'>main.py</font> las importa y se ejecuta desde la raíz con <font name='Courier'>python main.py</font>, usando una ruta relativa."),
 P("Salida real de la ejecución", h2)] + codigo(sal1)
e += [P("6. Resultados de la inspección inicial", h1)] + lista([
 f"El dataset tiene {n(AC['filas'])} filas y {AC['columnas']} columnas; la fecha y las categorías se leen como texto y las medidas como float64.",
 f"Hay {n(AC['nulos_total'])} valores nulos en total. Las columnas con más faltantes son Sunshine (48,0%), Evaporation (43,2%), Cloud3pm (40,8%) y Cloud9am (38,4%).",
 "Entre las variables del proyecto, la presión tiene 10,4% de nulos y la ráfaga de viento 7,1%; el resto está bajo 4%.",
 f"No hay filas duplicadas ({AC['duplicados']}) ni combinaciones de fecha y estación repetidas ({AC['claves_repetidas']}).",
 f"Se encontraron {AC['filas_sin_datos_climaticos']} registros sin ninguna medición climática.",
 f"No hay valores fuera de los rangos físicos definidos ({A['fuera_de_rango_total']}) ni temperaturas mínimas mayores que las máximas ({A['temp_min_mayor_a_max']})."])
e += [P("7. Problemas detectados en los datos", h1)]
e += tabla([["Problema detectado", "Variable afectada", "Cantidad", "Posible tratamiento"],
 ["Valores nulos", "Todas salvo Date y Location", n(AC["nulos_total"]), "Interpolación o mediana por estación; &quot;desconocido&quot; en categorías"],
 ["Columnas con demasiados nulos", "Sunshine, Evaporation, Cloud9am, Cloud3pm", "4 columnas (38% a 48%)", "Descartar: no se relacionan con la pregunta"],
 ["Estaciones sin sensor", "Pressure9am y Pressure3pm (4 estaciones), WindGustSpeed (2)", "6 casos", "Mantener nulo y documentarlo"],
 ["Registros sin ninguna medición", "Variables climáticas", str(AC["filas_sin_datos_climaticos"]), "Eliminar los registros"],
 ["Fecha como texto", "Date", n(AC["filas"]), "Convertir con pd.to_datetime()"],
 ["Nombres poco descriptivos", "Las 23 columnas", "23", "Renombrar en español y snake_case"],
 ["Unidades mixtas entre variables", "Viento (km/h), presión (hPa), temperatura (°C)", "3 unidades", "Mantener y usar medidas relativas para comparar"],
 ["Filas duplicadas", "Todas", "0", "Sin acción"],
 ["Valores fuera de rango", "Variables numéricas", "0", "Sin acción; se validará en cada ejecución"],
 ["Categorías escritas de distinta forma", "WindGustDir, Location", "0", "Sin acción; se normalizará a mayúsculas por seguridad"]], [3.8, 4.7, 2.8, 5.2])
e += [P("8. Conclusión del avance", h1),
 P("La fuente seleccionada permite abordar el problema, porque contiene temperatura, humedad, presión y viento en 49 estaciones durante casi diez años. El dataset tiene 145.460 registros y 23 columnas, de las cuales 14 se usarán en el proyecto. La carga con Pandas funciona de forma estable y controla los errores de lectura."),
 P("Los problemas iniciales más relevantes son la gran cantidad de valores faltantes, sobre todo en presión (10,4%) y en las columnas de nubosidad, evaporación y sol, que se descartarán. Además, cuatro estaciones no miden presión y dos no miden ráfaga, la fecha se almacena como texto y hay 308 registros vacíos. No se detectaron duplicados ni valores fuera de rango."),
 P("Serán necesarias las siguientes transformaciones: convertir la fecha, renombrar las columnas, imputar los nulos de forma diferenciada, extraer año y mes, y crear variables derivadas. El siguiente paso es el Avance 2: construir los módulos de limpieza, transformaciones y validaciones, y generar el archivo procesado sin modificar el original."),
 P("9. Respuestas metacognitivas", h1)]
qa = [("¿Qué criterio utilizaron para seleccionar el problema?", "Nos correspondió el Proyecto 4. Lo abordamos porque el clima combina variables distintas y permite comparar su comportamiento con una pregunta clara."),
 ("¿Por qué la fuente elegida es adecuada?", "Es de un organismo meteorológico oficial, tiene las cuatro variables, abarca casi diez años y sirve para practicar limpieza porque trae faltantes reales."),
 ("¿Qué variable podría generar mayores dificultades durante la limpieza?", "La presión atmosférica, con 10,4% de nulos y cuatro estaciones que no la miden, y la ráfaga de viento, que falta completa en dos estaciones."),
 ("¿Qué supuestos están realizando sobre los datos?", "Que las mediciones fueron tomadas con instrumentos calibrados, que un valor faltante es una omisión y no un cero, y que la copia de Kaggle coincide con los datos oficiales."),
 ("¿Qué decisión del pipeline fue más difícil?", "Cómo tratar los nulos: la presión no se puede inventar en estaciones sin sensor, por lo que decidimos mantenerlos y documentarlos."),
 ("¿Qué aprendieron al realizar la primera carga con Pandas?", "Que la carga debe incluir revisión de tipos y de nulos, porque la fecha se lee como texto y los NA del archivo se convierten solos en valores nulos."),
 ("¿Qué error apareció durante la implementación?", "Al ejecutar main.py desde otra carpeta apareció ModuleNotFoundError: No module named 'src'."),
 ("¿Cómo resolvieron ese error?", "Ejecutando el programa siempre desde la raíz del proyecto, con una ruta relativa al archivo de datos, y manteniendo el archivo __init__.py en src."),
 ("¿Cómo distribuyeron las tareas dentro del equipo?", "Patricio Parra: carga de datos y repositorio. Benjamín Carrillo: fuente de datos y diccionario. Simón Leiva: descripción del problema, pipeline e informe. Todos revisaron la entrega."),
 ("¿Qué evidencia demuestra que el proyecto puede continuar?", "El programa carga 145.460 registros sin errores, el diagnóstico inicial está documentado y los problemas detectados tienen un tratamiento definido.")]
for q, r in qa: e += [P(f"<b>{q}</b>", ParagraphStyle("q", parent=cuerpo, spaceAfter=1)), P(r)]
e += [P("10. Referencias", h1)] + lista([
 "Bureau of Meteorology (Australia). Observaciones meteorológicas diarias. http://www.bom.gov.au/climate/data/",
 "Young, J. y Young, A. Rain in Australia (weatherAUS). Kaggle. https://www.kaggle.com/datasets/jsphyg/weather-dataset-rattle-package",
 "acakin. weatherAUS (repositorio de GitHub). https://github.com/acakin/weatherAUS",
 "The pandas development team. pandas documentation. https://pandas.pydata.org/docs/"])
SimpleDocTemplate(os.path.join(BASE, "avance_1/reportes/avance_1.pdf"), pagesize=A4, leftMargin=2.3*cm, rightMargin=2.3*cm,
    topMargin=2*cm, bottomMargin=2*cm, title=f"{TITULO} - Avance 1", author=", ".join(INTEGRANTES)).build(e, onFirstPage=lambda c, d: None, onLaterPages=numerar)

# =================== AVANCE 2 ===================
reg = {r["accion"]: r for r in m["registro"]}
tn = m["tabla_nulos"]
sel = [c for c in A["nulos"]]
nulos_a_sel, nulos_d_sel = sum(A["nulos"].values()), sum(D["nulos"][c] for c in sel)
fig, ax = plt.subplots(figsize=(8, 3.6))
vars_ = [c for c in sel if c not in ("fecha", "estacion")]
x = range(len(vars_)); ax.bar([i - 0.2 for i in x], [A["nulos_pct"][c] for c in vars_], 0.4, label="Antes", color="#9AA9BC")
ax.bar([i + 0.2 for i in x], [D["nulos"][c] / D["filas"] * 100 for c in vars_], 0.4, label="Después", color="#1F3A5F")
ax.set_xticks(list(x)); ax.set_xticklabels(vars_, rotation=45, ha="right", fontsize=8); ax.set_ylabel("% de valores nulos"); ax.legend(frameon=False)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig("/tmp/figs/nulos.png", dpi=200); plt.close(fig)

e = portada(2, "Limpieza, tratamiento de nulos y transformación de datos")
e += [P("1. Diagnóstico de calidad", h1),
 P(f"El análisis se hizo sobre el archivo original <font name='Courier'>datos/originales/weatherAUS.csv</font>, que se conserva sin modificaciones. Se revisaron las 23 columnas originales y luego las 14 seleccionadas para el proyecto (fecha, estación, cuatro temperaturas, dos humedades, dos presiones, tres variables de viento y la dirección de la ráfaga)."),]
e += tabla([["Indicador", "Resultado"],
 ["Filas y columnas", f"{n(AC['filas'])} filas y {AC['columnas']} columnas (14 seleccionadas)"],
 ["Tipos de datos", "Date y categorías como texto (str); las 11 medidas como float64"],
 ["Valores nulos (23 columnas)", n(AC["nulos_total"])],
 ["Valores nulos (14 variables seleccionadas)", f"{n(nulos_a_sel)}"],
 ["Filas duplicadas", str(A["duplicados"])],
 ["Claves (fecha, estación) repetidas", str(A["claves_repetidas"])],
 ["Registros sin ninguna medición", str(A["filas_sin_datos_climaticos"])],
 ["Valores fuera de rango", str(A["fuera_de_rango_total"])],
 ["Temperatura mínima mayor que máxima", str(A["temp_min_mayor_a_max"])],
 ["Categorías inconsistentes", str(A["categorias_inconsistentes"])]], [8, 8.5])
e += [P("Nulos por columna (variables seleccionadas)", h2)]
e += tabla([["Variable", "Nulos", "% de nulos"]] + [[c, n(A["nulos"][c]), f"{A['nulos_pct'][c]:.2f}".replace(".", ",")] for c in sel], [5, 4, 4])
e += [P("<b>Interpretación.</b> El principal problema de calidad son los valores faltantes. Las columnas de nubosidad, evaporación y horas de sol superan el 38% de nulos y se descartaron. Entre las variables del proyecto, la presión (10,4%) y la ráfaga (7,1%) son las más afectadas, porque cuatro estaciones nunca midieron presión y dos nunca midieron ráfaga. El resto de la calidad es buena: no hay duplicados, valores fuera de rango, temperaturas incoherentes ni categorías mal escritas. Para la validación de rangos se usaron límites físicos plausibles para Australia (temperatura entre -15 y 55 °C, humedad entre 0 y 100%, presión entre 900 y 1100 hPa, viento hasta 150 km/h y ráfaga hasta 200 km/h).")]
e += [P("2. Limpieza realizada", h1), P("Todas las eliminaciones y modificaciones quedan registradas por el programa en <font name='Courier'>reportes/metricas_avance_2.json</font>. Las acciones aplicadas fueron:")]
e += tabla([["Acción", "Cantidad", "Justificación"],
 ["Normalizar nombres de columnas (minúsculas, sin tildes ni espacios, en español)", "23", "Facilita el uso y la lectura del código"],
 ["Descartar columnas no relacionadas o con más de 38% de nulos", str(reg["Columnas descartadas (no relacionadas con el proyecto o con mas de 38% de nulos)"]["cantidad"]), "Lluvia, evaporación, sol, nubosidad y dirección del viento a las 9 am y 3 pm no responden a la pregunta del proyecto"],
 ["Eliminar espacios y unificar a mayúsculas las categorías", "2 columnas", "Evita que una misma categoría aparezca escrita de dos formas"],
 ["Eliminar registros sin ninguna medición climática", str(reg["Registros sin ninguna medicion climatica eliminados"]["cantidad"]), "No aportan información; imputarlos sería inventar datos completos"],
 ["Eliminar filas duplicadas", str(reg["Filas duplicadas eliminadas"]["cantidad"]), "No se encontraron filas idénticas"],
 ["Revisar claves (fecha, estación) repetidas", str(reg["Claves (fecha, estacion) repetidas eliminadas"]["cantidad"]), "No hay identificadores repetidos"],
 ["Corregir valores fuera de rango", str(reg["Valores fuera de rango anulados"]["cantidad"]), "No se encontraron valores físicamente imposibles"]], [7, 2.2, 7.3])
e += [P("3. Tratamiento de nulos", h1),
 P("Se aplicó una estrategia distinta según el tipo de variable y en ningún caso se reemplazó por cero. Las variables continuas (temperatura, humedad y presión) se interpolan dentro de cada estación hasta en 3 registros consecutivos, porque el valor de un día se parece al de los días vecinos; los huecos más largos se completan con la mediana de la misma estación y el mismo mes. Las variables de viento usan directamente la mediana de la estación y el mes, porque su distribución es asimétrica y la media se distorsiona con las rafagas. La dirección de la ráfaga es categórica, por lo que se usa la categoría &quot;desconocido&quot;. Los nulos iniciales de la tabla se cuentan después de eliminar los 308 registros sin mediciones.")]
e += tabla([["Variable", "Nulos iniciales", "Estrategia", "Justificación", "Nulos finales"]] +
 [[t["variable"], n(t["nulos_iniciales"]), t["estrategia"], t["justificacion"], n(t["nulos_finales"])] for t in tn], [2.3, 1.8, 3.5, 7, 1.9])
e += [P("Los nulos que permanecen en presion_9am, presion_15h y rafaga_max corresponden a estaciones que nunca registraron esa variable (cuatro y dos estaciones, respectivamente). Se mantienen como nulos porque cualquier valor imputado sería inventado y porque su ausencia tiene significado: el sensor no existe. La validación comprueba que no queden otros nulos.")]
e += figura("/tmp/figs/nulos.png", 13)
e += [P("4. Transformaciones aplicadas", h1)]
e += tabla([["Variable original", "Transformación", "Resultado", "Tipo final"]] + [list(t) for t in m["transformaciones"]], [3.8, 5.6, 4, 3.1])
e += [P("Se aplicaron siete transformaciones, sobre el mínimo de tres exigido. Con ellas, la fecha queda lista para análisis temporal, las variables derivadas permiten comparar por año y estación, y la amplitud térmica y la ráfaga en m/s facilitan las comparaciones del Avance 3.")]
e += [P("5. Modularización del código", h1)]
e += tabla([["Archivo", "Responsabilidad"],
 ["src/carga.py", "Lectura del CSV con control de errores e inspección inicial"],
 ["src/limpieza.py", "Normalización de nombres, selección de columnas, duplicados, valores fuera de rango y tratamiento de nulos"],
 ["src/transformaciones.py", "Conversión de tipos y creación de variables"],
 ["src/validaciones.py", "Diagnóstico de calidad y comprobación de columnas, tipos y rangos"],
 ["main.py", "Ejecuta el pipeline en orden y exporta el resultado"]], [4.5, 12])
e += [P("El pipeline sigue el orden: carga, diagnóstico, limpieza, tratamiento de nulos, transformaciones, validación y exportación. Se ejecuta desde la raíz con <font name='Courier'>python main.py</font> y usa solo rutas relativas. Si alguna validación falla, el archivo no se exporta.")]
e += codigo("""    original = cargar_datos(RUTA_ORIGINAL)
    datos = normalizar_columnas(original)
    antes = diagnosticar(datos)
    datos = seleccionar_columnas(datos, registro)
    datos = quitar_espacios(datos)
    datos = convertir_tipos(datos)
    datos = eliminar_filas_vacias(datos, registro)
    datos = eliminar_duplicados(datos, registro)
    datos = anular_fuera_de_rango(datos, registro)
    datos, tabla_nulos = tratar_nulos(datos, registro)
    datos = crear_variables(datos)
    resultados = validar(datos, list(datos.columns))
    datos.to_csv(RUTA_SALIDA, index=False)""")
e += [P("6. Comparación antes y después", h1)]
e += tabla([["Indicador", "Antes", "Después"],
 ["Filas", n(A["filas"]), n(D["filas"])],
 ["Columnas", str(AC["columnas"]), str(D["columnas"])],
 ["Valores nulos (14 variables seleccionadas)", n(nulos_a_sel), n(nulos_d_sel)],
 ["Valores nulos (todas las columnas)", n(AC["nulos_total"]), n(D["nulos_total"])],
 ["Registros sin ninguna medición", str(A["filas_sin_datos_climaticos"]), "0"],
 ["Filas duplicadas", str(A["duplicados"]), str(D["duplicados"])],
 ["Valores fuera de rango", str(A["fuera_de_rango_total"]), str(D["fuera_de_rango_total"])],
 ["Variables transformadas", "0", str(m["variables_transformadas"])],
 ["Variables nuevas", "0", str(m["variables_nuevas"])]], [8, 4, 4.5])
e += [P(f"Los nulos totales después incluyen {n(D['nulos']['rafaga_ms'])} de la variable derivada rafaga_ms, que hereda los nulos de rafaga_max. Los {n(nulos_d_sel)} nulos restantes en las variables seleccionadas pertenecen a estaciones sin sensor.")]
e += [P("7. Evidencias de ejecución", h1), P("Salida real de <font name='Courier'>python main.py</font> ejecutado desde la raíz del proyecto:")]
import pandas as pd
muestra = pd.read_csv(os.path.join(BASE, "avance_2/datos/procesados/dataset_limpio.csv")).sample(5, random_state=1)
muestra = muestra[["fecha", "estacion", "temp_max", "humedad_15h", "presion_15h", "viento_15h", "estacion_anio", "rango_temperatura"]]
corte = sal2.split("== Dataset limpio (muestra) ==")[0].rstrip()
e += codigo("\n".join(l[:150] for l in corte.split("\n")) + "\n\n== Dataset limpio (muestra, df.sample(5)) ==\n" + muestra.to_string())
e += [P("8. Conclusión del avance", h1),
 P(f"Se corrigieron los problemas de estructura y calidad del dataset: se renombraron las columnas, se descartaron nueve columnas que no aportaban, se convirtió la fecha a datetime y se unificaron las categorías. Se eliminaron {reg['Registros sin ninguna medicion climatica eliminados']['cantidad']} registros que no tenían ninguna medición, y no hubo que eliminar duplicados ni corregir valores fuera de rango porque no existían."),
 P(f"Se imputaron los valores faltantes de forma diferenciada: interpolación y mediana por estación y mes en temperatura, humedad y presión; mediana en las variables de viento; y la categoría &quot;desconocido&quot; en la dirección de la ráfaga. Se crearon seis variables nuevas (año, mes, estación del año, amplitud térmica, ráfaga en m/s y rango de temperatura)."),
 P(f"Permanecen pendientes {n(D['nulos']['presion_9am'])} nulos en presión y {n(D['nulos']['rafaga_max'])} en ráfaga, que corresponden a estaciones sin sensor y deberán excluirse o analizarse aparte en esas variables. Además, la imputación con mediana reduce algo la variabilidad, lo que se debe considerar al comparar variables. Con esa salvedad, los datos están preparados para el análisis estadístico del Avance 3."),
 P("9. Repositorio", h1), P(f"Repositorio actualizado: {REPO}")]
SimpleDocTemplate(os.path.join(BASE, "avance_2/reportes/avance_2.pdf"), pagesize=A4, leftMargin=2.3*cm, rightMargin=2.3*cm,
    topMargin=2*cm, bottomMargin=2*cm, title=f"{TITULO} - Avance 2", author=", ".join(INTEGRANTES)).build(e, onFirstPage=lambda c, d: None, onLaterPages=numerar)
print("Informes generados")
