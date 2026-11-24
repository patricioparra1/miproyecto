"""Modelos de proyeccion sobre series mensuales."""
import numpy as np
import pandas as pd


def _indice_mes(idx, origen):
    return ((idx.year - origen.year) * 12 + (idx.month - origen.month)).to_numpy()


def _diseno(t, mes):
    """Matriz [1, t, 11 indicadores de mes]: tendencia lineal mas estacionalidad mensual."""
    return np.column_stack([np.ones(len(t)), t] + [(mes == m).astype(float) for m in range(2, 13)])


def _meses_futuros(serie, horizonte):
    return pd.date_range(serie.index[-1] + pd.offsets.MonthBegin(1), periods=horizonte, freq="MS")


def proyectar_lineal(serie, horizonte):
    """y = a + b*t + efecto del mes. Retorna (DataFrame con valor y banda del 95%, pendiente por anio)."""
    t = _indice_mes(serie.index, serie.index[0])
    X = _diseno(t, serie.index.month.to_numpy())
    y = serie.to_numpy(dtype=float)
    ok = ~np.isnan(y)
    coef, *_ = np.linalg.lstsq(X[ok], y[ok], rcond=None)
    sigma = (y[ok] - X[ok] @ coef).std(ddof=X.shape[1])
    futuro = _meses_futuros(serie, horizonte)
    pred = _diseno(_indice_mes(futuro, serie.index[0]), futuro.month.to_numpy()) @ coef
    return pd.DataFrame({"fecha": futuro, "valor": pred, "inferior": pred - 1.96 * sigma, "superior": pred + 1.96 * sigma}), coef[1] * 12


def proyectar_promedio_movil(serie, horizonte, ventana):
    """Cada mes proyectado es el promedio de los ultimos `ventana` meses (incluidos los ya proyectados)."""
    historia = list(serie.dropna().to_numpy()[-ventana:])
    valores = []
    for _ in range(horizonte):
        v = float(np.mean(historia[-ventana:]))
        valores.append(v)
        historia.append(v)
    return pd.DataFrame({"fecha": _meses_futuros(serie, horizonte), "valor": valores})


def evaluar(serie, metodo, ventana=12, meses_prueba=12):
    """Retrospectiva: entrena sin los ultimos `meses_prueba` y compara con lo ocurrido. Retorna (MAE, RMSE) o None."""
    entrenamiento, prueba = serie.iloc[:-meses_prueba], serie.iloc[-meses_prueba:]
    if entrenamiento.dropna().size < 24:
        return None
    if metodo == "lineal":
        pred = proyectar_lineal(entrenamiento, meses_prueba)[0]["valor"].to_numpy()
    else:
        pred = proyectar_promedio_movil(entrenamiento, meses_prueba, ventana)["valor"].to_numpy()
    error = prueba.to_numpy(dtype=float) - pred
    error = error[~np.isnan(error)]
    return float(np.abs(error).mean()), float(np.sqrt((error ** 2).mean()))
