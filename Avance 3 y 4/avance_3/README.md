# Comportamiento climatico integrado - Avance 3

Estadistica descriptiva, indicadores automaticos y graficos sobre el dataset limpio del Avance 2
(observaciones diarias de 49 estaciones de Australia, 2008-2017).

Pregunta del proyecto: que variable climatica presenta mayores cambios en el tiempo.

Integrantes: Patricio Parra, Benjamin Carrillo, Simon Leiva. Secciones 1 y 2, profesor Alex.

## Estructura

    datos/originales/        weatherAUS.csv sin modificar
    datos/procesados/        dataset_limpio.csv
    resultados/              estadisticas.csv, frecuencias.csv, indicadores.csv
    resultados/graficos/     grafico_01.png a grafico_04.png
    reportes/                avance_3.pdf
    src/pipeline.py          preparacion de datos (Avance 2)
    src/carga.py, limpieza.py, transformaciones.py, validaciones.py
    src/estadisticas.py      estadisticas descriptivas y volatilidad
    src/indicadores.py       nueve indicadores del proyecto
    src/visualizaciones.py   graficos con Matplotlib
    main.py                  ejecuta todo el proceso

## Ejecucion

Desde la raiz del proyecto:

    pip install -r requirements.txt
    python main.py

Al ejecutarlo se vuelve a preparar el dataset y se regeneran las tablas y los graficos.
