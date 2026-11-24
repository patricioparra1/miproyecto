# Comportamiento climatico integrado - Avance 2

Limpieza, tratamiento de nulos y transformacion del dataset weatherAUS (observaciones diarias de 49 estaciones de Australia).

Integrantes: Patricio Parra, Benjamin Carrillo, Simon Leiva. Secciones 1 y 2, profesor Alex.

## Estructura

    datos/originales/        weatherAUS.csv sin modificar
    datos/procesados/        dataset_limpio.csv generado por el pipeline
    reportes/                avance_1.pdf, avance_2.pdf y metricas_avance_2.json
    src/carga.py             lectura del archivo
    src/limpieza.py          nombres, filas vacias, duplicados, fuera de rango y nulos
    src/transformaciones.py  conversion de tipos y variables nuevas
    src/validaciones.py      diagnostico y validaciones
    main.py                  ejecuta el pipeline completo

## Ejecucion

Desde la raiz del proyecto:

    pip install -r requirements.txt
    python main.py

Orden del pipeline: carga, diagnostico, limpieza, tratamiento de nulos, transformaciones, validacion y exportacion.
Todas las rutas son relativas a la raiz.
