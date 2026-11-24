"""Indicadores automaticos asociados a la pregunta del proyecto."""
import pandas as pd

from src.estadisticas import NOMBRES, PRINCIPALES, volatilidad_diaria


def _fmt(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_indicadores(datos):
    """Retorna un DataFrame con indicador, metodo de calculo, resultado e interpretacion."""
    filas = []

    def agregar(nombre, metodo, resultado, interpretacion):
        filas.append({"indicador": nombre, "metodo_calculo": metodo, "resultado": resultado, "interpretacion": interpretacion})

    # 1. Registros validos
    validos = datos[list(PRINCIPALES)].notna().all(axis=1).sum()
    agregar("Registros válidos", "Filas con las cuatro variables principales no nulas",
            f"{_fmt(validos, 0)} de {_fmt(len(datos), 0)}",
            f"El {_fmt(validos / len(datos) * 100)}% de los registros permite comparar las cuatro variables; el resto pertenece a estaciones sin sensor de presión.")

    # 2. Variable con mayor volatilidad
    vol = volatilidad_diaria(datos).sort_values("indice_volatilidad", ascending=False)
    top, ultimo = vol.iloc[0], vol.iloc[-1]
    agregar("Variable más cambiante día a día", "Cambio medio absoluto entre días consecutivos dividido por la desviación estándar",
            f"{NOMBRES[top['variable']]} ({_fmt(top['indice_volatilidad'], 2)})",
            f"Es la variable que más se modifica de un día al siguiente en relación con su dispersión total; la menos cambiante es {NOMBRES[ultimo['variable']].lower()} ({_fmt(ultimo['indice_volatilidad'], 2)}).")

    # 3. Variacion de la temperatura entre 2009 y 2016, con estaciones presentes en ambos anios
    anual = datos.groupby(["estacion", "anio"])["temperatura"].mean().unstack()
    comunes = anual[[2009, 2016]].dropna()
    dif = (comunes[2016] - comunes[2009]).mean()
    agregar("Variación de temperatura 2009-2016", f"Diferencia de la media anual entre 2016 y 2009 en las {len(comunes)} estaciones con datos en ambos años",
            f"{'+' if dif >= 0 else ''}{_fmt(dif, 2)} °C",
            "Cambio de la temperatura media en siete años. Con una ventana tan corta no permite hablar de cambio climático, solo de la tendencia del período.")

    # 4. Dias muy calidos
    pct = (datos["temp_max"] > 35).mean() * 100
    agregar("Días con temperatura máxima sobre 35 °C", "Porcentaje de registros con temp_max > 35", f"{_fmt(pct, 2)}%",
            "Mide la frecuencia de calor extremo; sirve para priorizar estaciones donde planificar medidas contra olas de calor.")

    # 5. Maximo y registro asociado
    fila = datos.loc[datos["temp_max"].idxmax()]
    agregar("Temperatura máxima registrada", "Valor máximo de temp_max y fila donde ocurre",
            f"{_fmt(fila['temp_max'])} °C ({fila['estacion']}, {fila['fecha'].strftime('%d-%m-%Y')})",
            "Valor extremo del período con su estación y fecha; sirve para verificar que sea plausible y no un error de medición.")

    # 6. Estacion del anio con mas viento
    est = datos.groupby("estacion_anio")["viento"].mean().sort_values(ascending=False)
    agregar("Estación del año con más viento", "Promedio de la velocidad del viento por estación del año",
            f"{est.index[0].capitalize()} ({_fmt(est.iloc[0])} km/h)",
            f"El viento medio es mayor en {est.index[0]} y menor en {est.index[-1]} ({_fmt(est.iloc[-1])} km/h).")

    # 7. Direccion de rafaga mas frecuente
    dirs = datos.loc[datos["dir_rafaga"] != "desconocido", "dir_rafaga"].value_counts()
    agregar("Dirección de ráfaga más frecuente", "Moda de dir_rafaga sin contar la categoría «desconocido»",
            f"{dirs.index[0]} ({_fmt(dirs.iloc[0] / dirs.sum() * 100)}%)",
            "Indica desde dónde sopla con más frecuencia el viento más fuerte del día.")

    # 8. Baja humedad
    bajo = (datos["humedad_15h"] < 30).mean() * 100
    agregar("Días con humedad menor a 30% a las 15 h", "Porcentaje de registros con humedad_15h < 30", f"{_fmt(bajo, 2)}%",
            "Condición de aire seco que aumenta el riesgo de incendios; permite decidir dónde reforzar la vigilancia.")

    # 9. Amplitud estacional relativa
    amp = {}
    for var in PRINCIPALES:
        medias = datos.groupby("estacion_anio")[var].mean()
        amp[var] = (medias.max() - medias.min()) / datos[var].std()
    mayor = max(amp, key=amp.get)
    agregar("Variable con mayor ciclo estacional", "(Media de la estación más alta - media de la más baja) / desviación estándar",
            f"{NOMBRES[mayor]} ({_fmt(amp[mayor], 2)})",
            f"Es la variable cuyo cambio entre estaciones del año pesa más respecto de su dispersión total; en el otro extremo está {NOMBRES[min(amp, key=amp.get)].lower()} ({_fmt(min(amp.values()), 2)}).")
    return pd.DataFrame(filas)
