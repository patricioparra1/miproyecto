"""Tablas de apoyo al analisis: por estacion, por estacion del anio, por anio, correlaciones, atipicos y extremos."""
import numpy as np
import pandas as pd

from src.estadisticas import NOMBRES, PRINCIPALES, UNIDADES

COLS = list(PRINCIPALES)


def por_estacion(datos):
    """Promedios de cada estacion meteorologica y periodo con registros."""
    g = datos.groupby("estacion")
    t = g[COLS + ["temp_max", "rafaga_max"]].mean()
    t.insert(0, "registros", g.size())
    t.insert(1, "desde", g["fecha"].min().dt.strftime("%Y-%m"))
    t.insert(2, "hasta", g["fecha"].max().dt.strftime("%Y-%m"))
    return t.round(2).reset_index().sort_values("temp_max", ascending=False)


def por_estacion_del_anio(datos):
    orden = ["verano", "otono", "invierno", "primavera"]
    t = datos.groupby("estacion_anio")[COLS + ["temp_max", "amplitud_termica"]].mean().reindex(orden)
    t.insert(0, "registros", datos.groupby("estacion_anio").size().reindex(orden))
    return t.round(2).reset_index()


def por_anio(datos, desde=2009, hasta=2016):
    """Media anual usando solo estaciones con datos en el primer y en el ultimo anio, para no mezclar estaciones distintas."""
    base = datos.groupby(["estacion", "anio"])[COLS].mean()
    anual = base.unstack("anio")
    comunes = anual[COLS[0]][[desde, hasta]].dropna().index
    filas = []
    for a in range(desde, hasta + 1):
        sub = base.xs(a, level="anio").reindex(comunes)
        fila = {"anio": a, "estaciones": int(sub.dropna(how="all").shape[0])}
        fila.update(sub.mean().round(2).to_dict())
        filas.append(fila)
    return pd.DataFrame(filas)


def correlaciones(datos):
    return datos[COLS + ["temp_max", "amplitud_termica"]].corr().round(2).reset_index(names="variable")


def atipicos(datos):
    """Valores fuera de [Q1 - 1,5 IQR, Q3 + 1,5 IQR]."""
    filas = []
    for v in COLS + ["temp_max", "rafaga_max"]:
        s = datos[v].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        li, ls = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
        n = int(((s < li) | (s > ls)).sum())
        filas.append({"variable": v, "unidad": UNIDADES[v], "limite_inferior": round(li, 2), "limite_superior": round(ls, 2),
                      "atipicos": n, "porcentaje": round(n / len(s) * 100, 2)})
    return pd.DataFrame(filas)


def extremos(datos, k=10):
    cal = datos.nlargest(k, "temp_max")[["fecha", "estacion", "temp_max", "humedad_15h"]].copy()
    cal.insert(0, "tipo", "temperatura máxima")
    cal = cal.rename(columns={"temp_max": "valor", "humedad_15h": "humedad_15h"})
    ven = datos.nlargest(5, "rafaga_max")[["fecha", "estacion", "rafaga_max", "humedad_15h"]].copy()
    ven.insert(0, "tipo", "ráfaga máxima")
    ven = ven.rename(columns={"rafaga_max": "valor"})
    out = pd.concat([cal, ven])
    out["fecha"] = out["fecha"].dt.strftime("%d-%m-%Y")
    return out.reset_index(drop=True)
