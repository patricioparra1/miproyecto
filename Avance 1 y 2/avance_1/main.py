from src.carga import cargar_datos, inspeccionar_datos

RUTA = "datos/weatherAUS.csv"


def main():
    datos = cargar_datos(RUTA)
    if datos is not None:
        print("Carga realizada correctamente.")
        inspeccionar_datos(datos)
    else:
        print("El programa finalizo sin procesar los datos.")


if __name__ == "__main__":
    main()
