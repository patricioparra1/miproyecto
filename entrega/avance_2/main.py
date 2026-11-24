"""Pipeline del Avance 2: carga, diagnostico, limpieza, nulos, transformaciones, validacion y exportacion."""
import json
import os

from src.carga import cargar_datos
from src.limpieza import (anular_fuera_de_rango, eliminar_duplicados, eliminar_filas_vacias,
                          normalizar_columnas, quitar_espacios, seleccionar_columnas, tratar_nulos)
from src.transformaciones import TABLA_TRANSFORMACIONES, convertir_tipos, crear_variables
from src.validaciones import VARIABLES, diagnosticar, validar

RUTA_ORIGINAL = "datos/originales/weatherAUS.csv"
RUTA_SALIDA = "datos/procesados/dataset_limpio.csv"
RUTA_METRICAS = "reportes/metricas_avance_2.json"
NUEVAS = ["anio", "mes", "estacion_anio", "amplitud_termica", "rafaga_ms", "rango_temperatura"]


def main():
    original = cargar_datos(RUTA_ORIGINAL)
    if original is None:
        print("El programa finalizo sin procesar los datos.")
        return
    print(f"Carga realizada correctamente: {original.shape[0]} filas, {original.shape[1]} columnas.")

    # 1. Diagnostico del conjunto original completo y de las variables seleccionadas
    datos = normalizar_columnas(original)
    antes_completo = diagnosticar(datos)
    registro = []
    datos = seleccionar_columnas(datos, registro)
    antes = diagnosticar(datos)
    print("\n== Diagnostico inicial ==")
    print(f"Filas: {antes['filas']}  Columnas originales: {antes_completo['columnas']}  Seleccionadas: {antes['columnas']}")
    print(f"Nulos (23 columnas originales): {antes_completo['nulos_total']}")
    print(f"Nulos (variables seleccionadas): {antes['nulos_total']}")
    print(f"Filas duplicadas: {antes['duplicados']}  Claves repetidas: {antes['claves_repetidas']}")
    print(f"Fuera de rango: {antes['fuera_de_rango_total']}  Tmin > Tmax: {antes['temp_min_mayor_a_max']}")
    print(f"Categorias inconsistentes: {antes['categorias_inconsistentes']}")
    print(f"Filas sin ninguna medicion: {antes['filas_sin_datos_climaticos']}")
    print("\nNulos por columna (seleccionadas):")
    for col, n in antes["nulos"].items():
        print(f"  {col:<14}{n:>7}  ({antes['nulos_pct'][col]}%)")

    # 2. Limpieza
    datos = quitar_espacios(datos)
    datos = convertir_tipos(datos)
    datos = eliminar_filas_vacias(datos, registro)
    datos = eliminar_duplicados(datos, registro)
    datos = anular_fuera_de_rango(datos, registro)

    # 3. Nulos
    datos, tabla_nulos = tratar_nulos(datos, registro)

    # 4. Transformaciones
    datos = crear_variables(datos).sort_values(["fecha", "estacion"]).reset_index(drop=True)

    # 5. Validacion
    print("\n== Validacion ==")
    resultados = validar(datos, list(datos.columns))
    for descripcion, ok in resultados:
        print(f"[{'OK' if ok else 'FALLA'}] {descripcion}")
    if not all(ok for _, ok in resultados):
        print("La validacion fallo; no se exporta el archivo.")
        return

    # 6. Exportacion (el original no se modifica)
    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    datos.to_csv(RUTA_SALIDA, index=False)
    despues = diagnosticar(datos)
    print(f"\nArchivo exportado en {RUTA_SALIDA}: {datos.shape[0]} filas, {datos.shape[1]} columnas")

    print("\n== Registro de limpieza ==")
    for fila in registro:
        print(f"{fila['accion']}: {fila['cantidad']}")
    print("\n== Tratamiento de nulos ==")
    for fila in tabla_nulos:
        print(f"{fila['variable']:<14}{fila['nulos_iniciales']:>7} -> {fila['nulos_finales']:<6}{fila['estrategia']}")
    print("\n== Dataset limpio (muestra) ==")
    print(datos.sample(5, random_state=1).to_string())

    metricas = {"antes_completo": antes_completo, "antes": antes, "despues": despues, "registro": registro,
                "tabla_nulos": tabla_nulos, "transformaciones": TABLA_TRANSFORMACIONES,
                "variables_transformadas": len(VARIABLES) + 1, "variables_nuevas": len(NUEVAS), "validacion": resultados}
    os.makedirs(os.path.dirname(RUTA_METRICAS), exist_ok=True)
    with open(RUTA_METRICAS, "w", encoding="utf-8") as archivo:
        json.dump(metricas, archivo, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    main()
