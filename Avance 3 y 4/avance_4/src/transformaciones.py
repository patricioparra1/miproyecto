"""Conversion de tipos y creacion de variables."""
import pandas as pd

from src.validaciones import VARIABLES

ETIQUETAS_TEMP = ["frio", "templado", "calido", "muy_calido"]
CORTES_TEMP = [-float("inf"), 15, 25, 35, float("inf")]


def convertir_tipos(datos):
    """fecha a datetime y variables climaticas a float64 (texto invalido pasa a nulo)."""
    datos = datos.copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"], errors="coerce")
    for col in VARIABLES:
        if datos[col].dtype == "object":
            datos[col] = datos[col].str.replace(",", ".", regex=False)
        datos[col] = pd.to_numeric(datos[col], errors="coerce").astype("float64")
    return datos


def estacion_del_anio(mes):
    """Estacion astronomica aproximada para el hemisferio sur."""
    if mes in (12, 1, 2):
        return "verano"
    if mes in (3, 4, 5):
        return "otono"
    if mes in (6, 7, 8):
        return "invierno"
    return "primavera"


def crear_variables(datos):
    datos = datos.copy()
    datos["anio"] = datos["fecha"].dt.year
    datos["mes"] = datos["fecha"].dt.month
    datos["estacion_anio"] = datos["mes"].map(estacion_del_anio)
    datos["amplitud_termica"] = (datos["temp_max"] - datos["temp_min"]).round(1)
    datos["rafaga_ms"] = (datos["rafaga_max"] / 3.6).round(2)
    datos["rango_temperatura"] = pd.cut(datos["temp_max"], bins=CORTES_TEMP, labels=ETIQUETAS_TEMP).astype("object")
    datos.loc[datos["temp_max"].isna(), "rango_temperatura"] = "desconocido"
    return datos


TABLA_TRANSFORMACIONES = [
    ("fecha (texto)", "pd.to_datetime()", "Marca de tiempo", "datetime64[ns]"),
    ("11 variables climaticas", "pd.to_numeric() y astype(float64)", "Numeros decimales", "float64"),
    ("fecha", "Extraccion de anio y mes con .dt", "anio, mes", "int32"),
    ("mes", "Asignacion de estacion del anio (hemisferio sur)", "estacion_anio", "object"),
    ("temp_max y temp_min", "Resta entre ambas", "amplitud_termica (C)", "float64"),
    ("rafaga_max (km/h)", "Division por 3.6", "rafaga_ms (m/s)", "float64"),
    ("temp_max", "Clasificacion por rangos con pd.cut()", "rango_temperatura", "object"),
]
