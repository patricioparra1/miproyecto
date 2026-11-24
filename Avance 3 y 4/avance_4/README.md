# Comportamiento climatico integrado - Avance 4

Dashboard interactivo y proyeccion de datos. Permite explorar el comportamiento historico de temperatura,
humedad, presion y viento en 49 estaciones de Australia y proyectar escenarios futuros.

Integrantes: Patricio Parra, Benjamin Carrillo, Simon Leiva. Secciones 1 y 2, profesor Alex.

## Ejecucion

Desde la raiz del proyecto:

    pip install -r requirements.txt
    python main.py      # prepara los datos y genera resultados/ (tablas, graficos y proyecciones)
    python app.py       # abre el dashboard en http://127.0.0.1:8501

`python app.py 8600` usa otro puerto. El dashboard no necesita bibliotecas adicionales: usa un servidor HTTP
de la biblioteca estandar, Pandas, NumPy y Matplotlib.

## Que se puede hacer en el dashboard

- Filtros: variable, estaciones meteorologicas, rango de anios y estaciones del anio.
- Indicadores dinamicos: promedio, maximo, minimo, volatilidad diaria, variacion y valor proyectado.
- Graficos: historico mensual y proyeccion con banda de incertidumbre.
- Parametros: modelo (tendencia lineal con estacionalidad, promedio movil o ambos), horizonte (6 a 60 meses) y ventana del promedio movil.
- Tabla de error retrospectivo para comparar los dos modelos.

## Estructura

    app.py                   servidor del dashboard
    interfaz/index.html      pagina del dashboard
    src/panel.py             filtros, indicadores y graficos del dashboard
    src/proyeccion.py        modelos de proyeccion y evaluacion
    src/estadisticas.py, indicadores.py, visualizaciones.py   analisis del Avance 3
    src/pipeline.py, carga.py, limpieza.py, transformaciones.py, validaciones.py   preparacion de datos
    datos/                   originales y procesados
    resultados/              tablas, graficos y proyecciones exportadas
    reportes/                avance_4.pdf y capturas del dashboard
    main.py                  ejecuta el proceso completo
