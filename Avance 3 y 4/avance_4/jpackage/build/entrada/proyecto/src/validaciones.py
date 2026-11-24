"""Diagnostico y validaciones de columnas, tipos y rangos."""
import pandas as pd

# Rangos fisicamente plausibles para Australia
RANGOS = {
    "temp_min": (-15, 50), "temp_max": (-15, 55), "temp_9am": (-15, 50), "temp_15h": (-15, 55),   # grados C
    "humedad_9am": (0, 100), "humedad_15h": (0, 100),                                              # porcentaje
    "presion_9am": (900, 1100), "presion_15h": (900, 1100),                                        # hPa
    "viento_9am": (0, 150), "viento_15h": (0, 150), "rafaga_max": (0, 200),                        # km/h
}
VARIABLES = list(RANGOS)
CATEGORICAS = ["estacion", "dir_rafaga"]


def contar_fuera_de_rango(datos):
    """Cuenta valores numericos fuera de su rango, por variable."""
    conteo = {}
    for col, (minimo, maximo) in RANGOS.items():
        if col in datos.columns:
            serie = pd.to_numeric(datos[col], errors="coerce")
            conteo[col] = int(((serie < minimo) | (serie > maximo)).sum())
    return conteo


def temperaturas_incoherentes(datos):
    """Filas donde la temperatura minima supera a la maxima."""
    return int((pd.to_numeric(datos["temp_min"], errors="coerce") > pd.to_numeric(datos["temp_max"], errors="coerce")).sum())


def categorias_inconsistentes(datos):
    """Categorias que solo difieren en mayusculas o espacios (p. ej. 'ne' y 'NE ')."""
    total = 0
    for col in CATEGORICAS:
        if col in datos.columns:
            valores = datos[col].dropna().unique()
            total += len(valores) - len({str(v).strip().upper() for v in valores})
    return total


def diagnosticar(datos):
    """Retorna un diccionario con indicadores de calidad del DataFrame."""
    nulos = datos.isna().sum()
    clave = ["fecha", "estacion"]
    fuera = contar_fuera_de_rango(datos)
    return {
        "filas": int(datos.shape[0]),
        "columnas": int(datos.shape[1]),
        "tipos": {c: str(t) for c, t in datos.dtypes.items()},
        "nulos": {c: int(n) for c, n in nulos.items()},
        "nulos_pct": {c: round(float(n) / len(datos) * 100, 2) for c, n in nulos.items()},
        "nulos_total": int(nulos.sum()),
        "filas_sin_datos_climaticos": int(datos[[c for c in VARIABLES if c in datos.columns]].isna().all(axis=1).sum()),
        "duplicados": int(datos.duplicated().sum()),
        "claves_repetidas": int(datos.duplicated(subset=clave).sum()) if set(clave) <= set(datos.columns) else 0,
        "temp_min_mayor_a_max": temperaturas_incoherentes(datos) if "temp_min" in datos else 0,
        "categorias_inconsistentes": categorias_inconsistentes(datos),
        "fuera_de_rango": fuera,
        "fuera_de_rango_total": sum(fuera.values()),
    }


def nulos_sin_justificar(datos):
    """Nulos que no corresponden a estaciones que nunca midieron la variable."""
    pendientes = 0
    for col in VARIABLES:
        sin_sensor = datos.groupby("estacion")[col].transform(lambda s: s.isna().all())
        pendientes += int((datos[col].isna() & ~sin_sensor).sum())
    return pendientes


def validar(datos, columnas_esperadas):
    """Ejecuta las comprobaciones finales. Retorna lista de (descripcion, aprobada)."""
    r = []
    r.append(("Columnas esperadas presentes", all(c in datos.columns for c in columnas_esperadas)))
    r.append(("fecha es datetime64", pd.api.types.is_datetime64_any_dtype(datos["fecha"])))
    r.append(("Variables climaticas son float64", all(pd.api.types.is_float_dtype(datos[c]) for c in VARIABLES)))
    r.append(("Sin nulos salvo estaciones sin sensor", nulos_sin_justificar(datos) == 0))
    r.append(("Sin nulos en fecha, estacion ni dir_rafaga", int(datos[["fecha", "estacion", "dir_rafaga"]].isna().sum().sum()) == 0))
    r.append(("Sin filas duplicadas", int(datos.duplicated().sum()) == 0))
    r.append(("Sin fecha y estacion repetidas", not datos.duplicated(subset=["fecha", "estacion"]).any()))
    r.append(("Temperatura minima <= maxima", temperaturas_incoherentes(datos) == 0))
    r.append(("Valores dentro de rango", sum(contar_fuera_de_rango(datos).values()) == 0))
    return r
