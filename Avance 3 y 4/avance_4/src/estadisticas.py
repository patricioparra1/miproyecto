"""Estadistica descriptiva y medidas de variacion."""
import numpy as np
import pandas as pd

# Variables principales del proyecto: promedio de las mediciones de las 9 am y las 3 pm
PRINCIPALES = {
    "temperatura": ("temp_9am", "temp_15h"),
    "humedad": ("humedad_9am", "humedad_15h"),
    "presion": ("presion_9am", "presion_15h"),
    "viento": ("viento_9am", "viento_15h"),
}
UNIDADES = {"temperatura": "°C", "humedad": "%", "presion": "hPa", "viento": "km/h",
            "temp_max": "°C", "temp_min": "°C", "amplitud_termica": "°C", "rafaga_max": "km/h"}
NOMBRES = {"temperatura": "Temperatura", "humedad": "Humedad relativa", "presion": "Presión atmosférica", "viento": "Velocidad del viento"}
ANALIZADAS = list(PRINCIPALES) + ["temp_max", "temp_min", "amplitud_termica", "rafaga_max"]


def agregar_variables_principales(datos):
    """Agrega una columna diaria por variable (promedio 9 am y 3 pm)."""
    datos = datos.copy()
    for nombre, (manana, tarde) in PRINCIPALES.items():
        datos[nombre] = datos[[manana, tarde]].mean(axis=1)
    return datos


def calcular_estadisticas(datos, columnas=ANALIZADAS):
    """Tabla con las medidas descriptivas de cada variable."""
    filas = []
    for col in columnas:
        s = datos[col].dropna()
        media = s.mean()
        # el coeficiente de variacion solo tiene sentido en escalas con cero absoluto
        cv = np.nan if UNIDADES[col] == "°C" else s.std() / media * 100
        filas.append({"variable": col, "unidad": UNIDADES[col], "registros": int(s.size), "media": media, "mediana": s.median(),
                      "minimo": s.min(), "maximo": s.max(), "rango": s.max() - s.min(), "desviacion_estandar": s.std(),
                      "cuartil_1": s.quantile(0.25), "cuartil_3": s.quantile(0.75), "coef_variacion_pct": cv})
    return pd.DataFrame(filas).round(2)


def calcular_frecuencias(datos, columnas=("estacion_anio", "rango_temperatura", "dir_rafaga")):
    """Frecuencia absoluta y porcentual de las variables categoricas."""
    filas = []
    for col in columnas:
        conteo = datos[col].value_counts()
        for categoria, n in conteo.items():
            filas.append({"variable": col, "categoria": categoria, "frecuencia": int(n), "porcentaje": round(n / len(datos) * 100, 2)})
    return pd.DataFrame(filas)


def volatilidad_diaria(datos):
    """Cambio medio entre dias consecutivos de una misma estacion, dividido por la desviacion estandar.

    Es una medida sin unidades, por lo que permite comparar variables medidas en °C, % y km/h.
    Retorna un DataFrame con el cambio medio absoluto y el indice de volatilidad.
    """
    datos = datos.sort_values(["estacion", "fecha"])
    consecutivo = datos.groupby("estacion")["fecha"].diff().dt.days == 1
    filas = []
    for var in PRINCIPALES:
        cambio = datos.groupby("estacion")[var].diff().abs()[consecutivo]
        filas.append({"variable": var, "unidad": UNIDADES[var], "cambio_medio_diario": cambio.mean(),
                      "desviacion_estandar": datos[var].std(), "indice_volatilidad": cambio.mean() / datos[var].std()})
    return pd.DataFrame(filas).round(3)
