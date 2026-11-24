"""Logica del dashboard: filtros, indicadores, proyeccion y graficos (sin interfaz)."""
import base64
import io
import threading

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.estadisticas import NOMBRES, PRINCIPALES, UNIDADES, agregar_variables_principales, volatilidad_diaria
from src.proyeccion import evaluar, proyectar_lineal, proyectar_promedio_movil

COLORES = {"temperatura": "#D55E00", "humedad": "#0072B2", "presion": "#009E73", "viento": "#CC79A7"}
ESTACIONES_ANIO = ["verano", "otono", "invierno", "primavera"]
_candado = threading.Lock()  # Matplotlib no es seguro entre hilos


def cargar(ruta):
    return agregar_variables_principales(pd.read_csv(ruta, parse_dates=["fecha"]))


def opciones(datos):
    return {"estaciones": sorted(datos["estacion"].unique()), "variables": [{"id": v, "nombre": NOMBRES[v], "unidad": UNIDADES[v]} for v in PRINCIPALES],
            "anio_min": int(datos["anio"].min()), "anio_max": int(datos["anio"].max())}


def filtrar(datos, estaciones=None, anio_min=None, anio_max=None, estaciones_anio=None):
    f = datos
    if estaciones:
        f = f[f["estacion"].isin(estaciones)]
    if anio_min is not None:
        f = f[(f["anio"] >= anio_min) & (f["anio"] <= anio_max)]
    if estaciones_anio:
        f = f[f["estacion_anio"].isin(estaciones_anio)]
    return f


def serie_mensual(datos, variable):
    """Media mensual corrigiendo la entrada de estaciones nuevas (ver visualizaciones.py)."""
    t = datos.assign(periodo=datos["fecha"].dt.to_period("M")).groupby(["periodo", "estacion"])[variable].mean().unstack()
    t = t.dropna(axis=1, thresh=max(1, int(0.6 * len(t))))
    serie = (t - t.mean()).mean(axis=1) + t.mean().mean()
    serie.index = serie.index.to_timestamp()
    return serie.asfreq("MS")


def _png(fig):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=105)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def _estilo(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(alpha=0.25)


def grafico_historico(serie, variable, titulo):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    _estilo(ax)
    ax.plot(serie.index, serie.values, color=COLORES[variable], lw=1, alpha=0.5, label="Media mensual")
    ax.plot(serie.index, serie.rolling(12, min_periods=6).mean(), color=COLORES[variable], lw=2.4, label="Promedio móvil 12 meses")
    ax.set_title(titulo, fontsize=10.5)
    ax.set_xlabel("Mes")
    ax.set_ylabel(f"{NOMBRES[variable]} ({UNIDADES[variable]})")
    ax.legend(frameon=False, fontsize=8.5)
    return _png(fig)


def grafico_proyeccion(serie, variable, modelo, lineal, movil, titulo):
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    _estilo(ax)
    hist = serie.iloc[-72:]
    ax.plot(hist.index, hist.values, color="#4A5568", lw=1.5, label="Histórico")
    if modelo in ("lineal", "comparar") and lineal is not None:
        ax.fill_between(lineal["fecha"], lineal["inferior"], lineal["superior"], color="#D55E00", alpha=0.13, label="Banda 95% (lineal)")
        ax.plot(lineal["fecha"], lineal["valor"], color="#D55E00", lw=2, label="Tendencia lineal + estacionalidad")
    if modelo in ("movil", "comparar") and movil is not None:
        ax.plot(movil["fecha"], movil["valor"], color="#009E73", lw=2, ls="--", label="Promedio móvil")
    ax.axvline(serie.index[-1], color="grey", lw=0.8, ls=":")
    ax.set_title(titulo, fontsize=10.5)
    ax.set_xlabel("Mes")
    ax.set_ylabel(f"{NOMBRES[variable]} ({UNIDADES[variable]})")
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    return _png(fig)


def _f(x, d=2):
    return None if x is None else round(float(x), d)


def calcular_vista(datos, p):
    """Calcula todo lo que muestra el dashboard para una combinacion de filtros y parametros."""
    var = p.get("variable", "temperatura")
    u = UNIDADES[var]
    filtrado = filtrar(datos, p.get("estaciones"), p.get("anio_min"), p.get("anio_max"), p.get("estaciones_anio"))
    filtrado = filtrado.dropna(subset=[var])
    if filtrado.empty:
        return {"error": "No hay datos para esa combinación de filtros. Pruebe con más estaciones o más años."}
    base = filtrar(datos, p.get("estaciones"), p.get("anio_min"), p.get("anio_max")).dropna(subset=[var])
    lugar = "todas las estaciones" if not p.get("estaciones") else (", ".join(p["estaciones"]) if len(p["estaciones"]) <= 3 else f"{len(p['estaciones'])} estaciones")

    # Indicadores sobre los datos diarios filtrados
    fila_max, fila_min = filtrado.loc[filtrado[var].idxmax()], filtrado.loc[filtrado[var].idxmin()]
    vol = volatilidad_diaria(filtrado)
    vol = float(vol.loc[vol["variable"] == var, "indice_volatilidad"].iloc[0]) if filtrado["estacion"].size > 2 else None
    ind = {"promedio": _f(filtrado[var].mean()), "maximo": _f(fila_max[var]), "maximo_detalle": f"{fila_max['estacion']}, {fila_max['fecha']:%d-%m-%Y}",
           "minimo": _f(fila_min[var]), "minimo_detalle": f"{fila_min['estacion']}, {fila_min['fecha']:%d-%m-%Y}",
           "registros": int(len(filtrado)), "volatilidad": _f(vol, 2), "unidad": u}

    serie_hist = serie_mensual(filtrado, var)
    serie = serie_mensual(base, var)
    resp = {"indicadores": ind, "unidad": u, "variable": NOMBRES[var]}
    resp["img_historico"] = grafico_historico(serie_hist, var, f"{NOMBRES[var]}: evolución mensual ({lugar})")
    if serie.dropna().size < 24:
        resp["aviso"] = "Con menos de 24 meses de datos no se puede proyectar. Amplíe el rango de años."
        return resp

    valores = serie.dropna()
    ind["variacion"] = _f(valores.iloc[-12:].mean() - valores.iloc[:12].mean())
    ind["variacion_pct"] = _f(ind["variacion"] / valores.iloc[:12].mean() * 100, 2) if var != "temperatura" else None

    modelo, h, ventana = p.get("modelo", "comparar"), int(p.get("horizonte", 24)), int(p.get("ventana", 12))
    lineal, pend = proyectar_lineal(serie, h)
    movil = proyectar_promedio_movil(serie, h, ventana)
    ev = {"lineal": evaluar(serie, "lineal"), "movil": evaluar(serie, "movil", ventana)}
    with _candado:
        resp["img_proyeccion"] = grafico_proyeccion(serie, var, modelo, lineal, movil, f"Proyección a {h} meses: {NOMBRES[var].lower()} ({lugar})")
    elegido = movil if modelo == "movil" else lineal
    resp["proyeccion"] = {"fecha_final": f"{elegido['fecha'].iloc[-1]:%m-%Y}", "valor_final": _f(elegido["valor"].iloc[-1]),
                          "inferior": _f(lineal["inferior"].iloc[-1]) if modelo != "movil" else None,
                          "superior": _f(lineal["superior"].iloc[-1]) if modelo != "movil" else None, "pendiente_anual": _f(pend, 3)}
    resp["evaluacion"] = [{"modelo": "Tendencia lineal + estacionalidad", "mae": _f(ev["lineal"][0]) if ev["lineal"] else None, "rmse": _f(ev["lineal"][1]) if ev["lineal"] else None},
                          {"modelo": f"Promedio móvil ({ventana} meses)", "mae": _f(ev["movil"][0]) if ev["movil"] else None, "rmse": _f(ev["movil"][1]) if ev["movil"] else None}]

    # Texto interpretativo
    def n(x, d=2, signo=False):
        return f"{x:{'+' if signo else ''}.{d}f}".replace(".", ",")
    cambio_total = pend * len(valores) / 12
    if abs(cambio_total) < 0.1 * valores.std():
        s = [f"En el período seleccionado la {NOMBRES[var].lower()} se mantiene prácticamente estable (tendencia de {n(pend, 3, True)} {u} por año)."]
    else:
        s = [f"La tendencia lineal es de {n(pend, 3, True)} {u} por año: la {NOMBRES[var].lower()} {'sube' if pend > 0 else 'baja'} en el período."]
    s.append(f"El modelo proyecta {n(resp['proyeccion']['valor_final'])} {u} para {resp['proyeccion']['fecha_final']}.")
    if ev["lineal"] and ev["movil"]:
        mejor = "la tendencia lineal con estacionalidad" if ev["lineal"][0] <= ev["movil"][0] else "el promedio móvil"
        s.append(f"En la prueba retrospectiva (últimos 12 meses) {mejor} tuvo menor error medio absoluto.")
    s.append("Es una estimación basada en el comportamiento pasado, no una predicción segura.")
    resp["interpretacion"] = " ".join(s)
    return resp


def resumen_proyecciones(datos, horizonte=24, ventana=12):
    """Tabla con la proyeccion y el error retrospectivo de las cuatro variables (todas las estaciones)."""
    filas = []
    for var in PRINCIPALES:
        serie = serie_mensual(datos.dropna(subset=[var]), var)
        lineal, pend = proyectar_lineal(serie, horizonte)
        ev_l, ev_m = evaluar(serie, "lineal"), evaluar(serie, "movil", ventana)
        filas.append({"variable": var, "unidad": UNIDADES[var], "pendiente_por_anio": round(pend, 3),
                      "valor_proyectado": round(lineal["valor"].iloc[-1], 2), "fecha_proyectada": f"{lineal['fecha'].iloc[-1]:%Y-%m}",
                      "mae_lineal": round(ev_l[0], 2), "mae_promedio_movil": round(ev_m[0], 2)})
    return pd.DataFrame(filas)


def tabla_sensibilidad(datos, ventanas=(3, 6, 12, 24)):
    """Error retrospectivo (MAE) del promedio movil segun su ventana, comparado con la tendencia lineal."""
    filas = []
    for var in PRINCIPALES:
        serie = serie_mensual(datos.dropna(subset=[var]), var)
        fila = {"variable": var, "unidad": UNIDADES[var], "lineal": round(evaluar(serie, "lineal")[0], 2)}
        for v in ventanas:
            fila[f"movil_{v}"] = round(evaluar(serie, "movil", v)[0], 2)
        filas.append(fila)
    return pd.DataFrame(filas)


def tabla_horizontes(datos, horizontes=(12, 24, 36, 60)):
    """Valor proyectado (tendencia lineal) al final de cada horizonte, con su banda del 95%."""
    filas = []
    for var in PRINCIPALES:
        serie = serie_mensual(datos.dropna(subset=[var]), var)
        for h in horizontes:
            lin, _ = proyectar_lineal(serie, h)
            u = lin.iloc[-1]
            filas.append({"variable": var, "unidad": UNIDADES[var], "horizonte_meses": h, "fecha": f"{u['fecha']:%Y-%m}",
                          "valor": round(u["valor"], 2), "inferior": round(u["inferior"], 2), "superior": round(u["superior"], 2)})
    return pd.DataFrame(filas)
