"""Proceso completo: preparacion de datos, estadisticas, indicadores y graficos."""
import contextlib
import io
import os

import pandas as pd

from src.estadisticas import agregar_variables_principales, calcular_estadisticas, calcular_frecuencias, volatilidad_diaria
from src.indicadores import calcular_indicadores
from src.pipeline import ejecutar_pipeline
from src.resumenes import atipicos, correlaciones, extremos, por_anio, por_estacion, por_estacion_del_anio
from src.visualizaciones import generar_graficos

RUTA_LIMPIO = "datos/procesados/dataset_limpio.csv"
CARPETA = "resultados"


def main():
    # El Avance 2 se vuelve a ejecutar para que todo el proceso sea reproducible desde cero
    with contextlib.redirect_stdout(io.StringIO()):
        ok = ejecutar_pipeline()
    if not ok:
        print("No fue posible preparar los datos.")
        return
    datos = pd.read_csv(RUTA_LIMPIO, parse_dates=["fecha"])
    datos = agregar_variables_principales(datos)
    print(f"Dataset limpio cargado: {len(datos)} registros, {datos['estacion'].nunique()} estaciones.")

    estadisticas = calcular_estadisticas(datos)
    frecuencias = calcular_frecuencias(datos)
    indicadores = calcular_indicadores(datos)
    os.makedirs(CARPETA, exist_ok=True)
    estadisticas.to_csv(f"{CARPETA}/estadisticas.csv", index=False, encoding="utf-8-sig")
    frecuencias.to_csv(f"{CARPETA}/frecuencias.csv", index=False, encoding="utf-8-sig")
    indicadores.to_csv(f"{CARPETA}/indicadores.csv", index=False, encoding="utf-8-sig")
    for nombre, tabla in (("estadisticas_estaciones", por_estacion(datos)), ("estadisticas_estacional", por_estacion_del_anio(datos)),
                          ("estadisticas_anual", por_anio(datos)), ("correlaciones", correlaciones(datos)),
                          ("atipicos", atipicos(datos)), ("extremos", extremos(datos))):
        tabla.to_csv(f"{CARPETA}/{nombre}.csv", index=False, encoding="utf-8-sig")
    graficos = generar_graficos(datos, f"{CARPETA}/graficos")

    pd.set_option("display.width", 200, "display.max_columns", 20)
    print("\n== Estadisticas descriptivas ==")
    print(estadisticas.to_string(index=False))
    print("\n== Volatilidad diaria ==")
    print(volatilidad_diaria(datos).to_string(index=False))
    print("\n== Indicadores ==")
    for _, f in indicadores.iterrows():
        print(f"{f['indicador']}: {f['resultado']}")
    print("\n== Archivos generados ==")
    print("resultados/estadisticas.csv, frecuencias.csv, indicadores.csv y 6 tablas de apoyo")
    for g in graficos:
        print(f"resultados/graficos/{g}")


if __name__ == "__main__":
    main()
