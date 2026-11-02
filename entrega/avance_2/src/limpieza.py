"""Limpieza: nombres, texto, duplicados, fuera de rango y nulos."""
import unicodedata

import numpy as np
import pandas as pd

from src.validaciones import RANGOS, VARIABLES

# Variables seleccionadas del dataset original (el resto no aporta a la pregunta del proyecto)
RENOMBRES = {
    "date": "fecha", "location": "estacion",
    "mintemp": "temp_min", "maxtemp": "temp_max", "temp9am": "temp_9am", "temp3pm": "temp_15h",
    "humidity9am": "humedad_9am", "humidity3pm": "humedad_15h",
    "pressure9am": "presion_9am", "pressure3pm": "presion_15h",
    "windspeed9am": "viento_9am", "windspeed3pm": "viento_15h",
    "windgustspeed": "rafaga_max", "windgustdir": "dir_rafaga",
}
LIMITE_INTERPOLACION = 3  # registros consecutivos maximos a interpolar


def _normalizar_nombre(nombre):
    nombre = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()
    return nombre.strip().lower().replace(" ", "_")


def normalizar_columnas(datos):
    """Nombres en minusculas sin espacios ni tildes, y renombrado a terminos del proyecto."""
    datos = datos.copy()
    datos.columns = [RENOMBRES.get(_normalizar_nombre(c), _normalizar_nombre(c)) for c in datos.columns]
    return datos


def seleccionar_columnas(datos, registro):
    """Conserva solo las variables del proyecto."""
    conservar = list(RENOMBRES.values())
    descartadas = [c for c in datos.columns if c not in conservar]
    registro.append({"accion": "Columnas descartadas (no relacionadas con el proyecto o con mas de 38% de nulos)",
                     "cantidad": len(descartadas), "detalle": descartadas})
    return datos[conservar].copy()


def quitar_espacios(datos):
    """Elimina espacios sobrantes y unifica a mayusculas las categorias."""
    datos = datos.copy()
    for col in ("estacion", "dir_rafaga"):
        datos[col] = datos[col].str.strip()
    datos["dir_rafaga"] = datos["dir_rafaga"].str.upper()
    return datos


def eliminar_filas_vacias(datos, registro):
    """Elimina registros sin ninguna medicion climatica."""
    n = len(datos)
    datos = datos.dropna(subset=VARIABLES, how="all")
    registro.append({"accion": "Registros sin ninguna medicion climatica eliminados", "cantidad": n - len(datos)})
    return datos


def eliminar_duplicados(datos, registro):
    """Elimina filas identicas y claves (fecha, estacion) repetidas, conservando la primera."""
    n = len(datos)
    datos = datos.drop_duplicates()
    registro.append({"accion": "Filas duplicadas eliminadas", "cantidad": n - len(datos)})
    n = len(datos)
    datos = datos.drop_duplicates(subset=["fecha", "estacion"], keep="first")
    registro.append({"accion": "Claves (fecha, estacion) repetidas eliminadas", "cantidad": n - len(datos)})
    return datos


def anular_fuera_de_rango(datos, registro):
    """Convierte a nulo los valores fisicamente imposibles; se tratan luego como nulos."""
    datos = datos.copy()
    total = 0
    for col, (minimo, maximo) in RANGOS.items():
        mascara = (datos[col] < minimo) | (datos[col] > maximo)
        datos.loc[mascara, col] = np.nan
        total += int(mascara.sum())
    registro.append({"accion": "Valores fuera de rango anulados", "cantidad": total})
    return datos


def tratar_nulos(datos, registro):
    """Imputa segun el tipo de variable. Retorna (datos, tabla de tratamiento)."""
    datos = datos.sort_values(["estacion", "fecha"]).reset_index(drop=True)
    mes = datos["fecha"].dt.month
    tabla = []
    estrategias = {
        "continua": ("Interpolacion por estacion y mediana estacion-mes",
                     "Variable continua con fuerte dependencia del dia anterior; la mediana cubre huecos largos"),
        "viento": ("Mediana por estacion y mes",
                   "Distribucion asimetrica con rafagas; la media se distorsiona"),
    }
    for col in VARIABLES:
        iniciales = int(datos[col].isna().sum())
        if col.startswith(("viento", "rafaga")):
            clave = "viento"
        else:
            clave = "continua"
            datos[col] = datos.groupby("estacion")[col].transform(
                lambda s: s.interpolate(limit=LIMITE_INTERPOLACION, limit_area="inside"))
        datos[col] = datos[col].fillna(datos.groupby(["estacion", mes])[col].transform("median"))
        sin_sensor = int(datos.groupby("estacion")[col].transform(lambda s: s.isna().all()).sum())
        estrategia, just = estrategias[clave]
        if sin_sensor:
            just += f". Quedan {sin_sensor} nulos en estaciones que nunca midieron la variable"
        tabla.append({"variable": col, "nulos_iniciales": iniciales, "estrategia": estrategia,
                      "justificacion": just, "nulos_finales": int(datos[col].isna().sum())})
    iniciales = int(datos["dir_rafaga"].isna().sum())
    datos["dir_rafaga"] = datos["dir_rafaga"].fillna("desconocido")
    tabla.append({"variable": "dir_rafaga", "nulos_iniciales": iniciales, "estrategia": "Categoria 'desconocido'",
                  "justificacion": "Variable categorica: no se puede promediar ni inventar una direccion",
                  "nulos_finales": int(datos["dir_rafaga"].isna().sum())})
    return datos, tabla
