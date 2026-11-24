"""Graficos del analisis con Matplotlib. Cada funcion guarda un PNG."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import numpy as np

from src.estadisticas import NOMBRES, PRINCIPALES, UNIDADES, volatilidad_diaria

COLORES = {"temperatura": "#D55E00", "humedad": "#0072B2", "presion": "#009E73", "viento": "#CC79A7"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25})


def _guardar(fig, ruta):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    fig.tight_layout()
    fig.savefig(ruta, dpi=160)
    plt.close(fig)


def serie_mensual_estandarizada(datos, variable):
    """Media mensual de una variable, corrigiendo la entrada de estaciones nuevas.

    Se calcula la media mensual de cada estacion, se resta su media propia y se promedian las
    diferencias; asi la serie no cambia solo porque se agregaron estaciones mas calidas o frias.
    """
    t = datos.assign(periodo=datos["fecha"].dt.to_period("M")).groupby(["periodo", "estacion"])[variable].mean().unstack()
    t = t.dropna(axis=1, thresh=24)
    serie = (t - t.mean()).mean(axis=1) + t.mean().mean()
    serie.index = serie.index.to_timestamp()
    return serie


def grafico_volatilidad(datos, ruta):
    vol = volatilidad_diaria(datos).sort_values("indice_volatilidad")
    fig, ax = plt.subplots(figsize=(7, 4))
    barras = ax.barh([NOMBRES[v] for v in vol["variable"]], vol["indice_volatilidad"], color=[COLORES[v] for v in vol["variable"]])
    for b, v in zip(barras, vol["indice_volatilidad"]):
        ax.text(v + 0.01, b.get_y() + b.get_height() / 2, f"{v:.2f}", va="center")
    ax.set_xlabel("Índice de volatilidad diaria (sin unidad)")
    ax.set_title("¿Qué variable cambia más de un día a otro?")
    ax.set_xlim(0, vol["indice_volatilidad"].max() * 1.15)
    ax.grid(axis="y", visible=False)
    _guardar(fig, ruta)


def grafico_evolucion(datos, ruta):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for var in PRINCIPALES:
        s = serie_mensual_estandarizada(datos, var)
        s = s[(s.index >= "2009-01-01") & (s.index <= "2016-12-31")]
        ax.plot(s.index, (s - s.mean()) / s.std(), label=f"{NOMBRES[var]} ({UNIDADES[var]})", color=COLORES[var], lw=1.6)
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xlabel("Mes (2009 a 2016)")
    ax.set_ylabel("Media mensual estandarizada (desv. estándar)")
    ax.set_title("Evolución mensual de las cuatro variables")
    ax.legend(ncol=2, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    _guardar(fig, ruta)


def grafico_cajas(datos, ruta):
    orden = ["verano", "otono", "invierno", "primavera"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    cajas = ax.boxplot([datos.loc[datos["estacion_anio"] == e, "temp_max"] for e in orden], tick_labels=["Verano", "Otoño", "Invierno", "Primavera"],
                       patch_artist=True, flierprops={"markersize": 2, "alpha": 0.3}, medianprops={"color": "black"})
    for c in cajas["boxes"]:
        c.set_facecolor("#F2C9A8")
    ax.set_xlabel("Estación del año (hemisferio sur)")
    ax.set_ylabel("Temperatura máxima diaria (°C)")
    ax.set_title("Distribución de la temperatura máxima por estación del año")
    _guardar(fig, ruta)


def grafico_dispersion(datos, ruta):
    m = datos.dropna(subset=["temp_15h", "humedad_15h"]).sample(8000, random_state=3)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.scatter(m["temp_15h"], m["humedad_15h"], s=6, alpha=0.25, color=COLORES["humedad"])
    ax.set_xlabel("Temperatura a las 15 h (°C)")
    ax.set_ylabel("Humedad relativa a las 15 h (%)")
    ax.set_title(f"Temperatura y humedad a las 15 h (muestra de {len(m):,} días)".replace(",", "."))
    _guardar(fig, ruta)


def grafico_correlaciones(datos, ruta):
    cols = list(PRINCIPALES)
    c = datos[cols].corr().to_numpy()
    fig, ax = plt.subplots(figsize=(5.8, 4.8))
    im = ax.imshow(c, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(4), [NOMBRES[v].split()[0] for v in cols])
    ax.set_yticks(range(4), [NOMBRES[v].split()[0] for v in cols])
    ax.grid(False)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{c[i, j]:.2f}", ha="center", va="center", color="white" if abs(c[i, j]) > 0.6 else "black")
    fig.colorbar(im, ax=ax, label="Coeficiente de correlación de Pearson")
    ax.set_title("Correlación entre variables (valores diarios)")
    _guardar(fig, ruta)


def grafico_estaciones(datos, ruta):
    t = datos.groupby("estacion")["temp_max"].mean().sort_values()
    sel = pd.concat([t.head(8), t.tail(8)])
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(sel.index, sel.values, color=["#56B4E9"] * 8 + ["#D55E00"] * 8)
    ax.axvline(t.mean(), color="grey", ls="--", lw=1, label=f"Promedio de las 49 estaciones ({t.mean():.1f} °C)")
    ax.set_xlabel("Temperatura máxima media (°C)")
    ax.set_ylabel("Estación meteorológica")
    ax.set_title("Las 8 estaciones más frías y las 8 más cálidas")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="y", visible=False)
    _guardar(fig, ruta)


def grafico_climatologia(datos, ruta):
    fig, ejes = plt.subplots(2, 2, figsize=(9, 5.4), sharex=True)
    meses = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    for ax, var in zip(ejes.ravel(), PRINCIPALES):
        g = datos.groupby("mes")[var]
        ax.plot(range(1, 13), g.mean(), marker="o", color=COLORES[var], lw=1.6)
        ax.fill_between(range(1, 13), g.quantile(0.25), g.quantile(0.75), color=COLORES[var], alpha=0.15)
        ax.set_title(f"{NOMBRES[var]} ({UNIDADES[var]})", fontsize=10)
        ax.set_xticks(range(1, 13), meses)
    for ax in ejes[1]:
        ax.set_xlabel("Mes del año")
    fig.suptitle("Ciclo anual de cada variable (línea: media; banda: cuartiles 1 a 3)", fontsize=11)
    _guardar(fig, ruta)


def generar_graficos(datos, carpeta):
    grafico_volatilidad(datos, os.path.join(carpeta, "grafico_01.png"))
    grafico_evolucion(datos, os.path.join(carpeta, "grafico_02.png"))
    grafico_cajas(datos, os.path.join(carpeta, "grafico_03.png"))
    grafico_dispersion(datos, os.path.join(carpeta, "grafico_04.png"))
    grafico_correlaciones(datos, os.path.join(carpeta, "grafico_05.png"))
    grafico_estaciones(datos, os.path.join(carpeta, "grafico_06.png"))
    grafico_climatologia(datos, os.path.join(carpeta, "grafico_07.png"))
    return sorted(os.listdir(carpeta))
