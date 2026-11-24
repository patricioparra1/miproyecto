"""Carga e inspeccion inicial del dataset climatico."""
import pandas as pd


def cargar_datos(ruta):
    """
    Carga un conjunto de datos desde un archivo CSV.

    Parametros
    ----------
    ruta : str
        Ruta relativa del archivo.

    Retorna
    -------
    pandas.DataFrame o None
        DataFrame con los datos, o None si la lectura falla.
    """
    try:
        return pd.read_csv(ruta)
    except FileNotFoundError:
        print(f"Error: no se encontro el archivo '{ruta}'.")
    except pd.errors.EmptyDataError:
        print("Error: el archivo no contiene datos.")
    except pd.errors.ParserError:
        print("Error: no fue posible interpretar el archivo.")
    except UnicodeDecodeError:
        print("Error: la codificacion del archivo no es compatible.")
    return None


def inspeccionar_datos(datos):
    """Muestra la estructura basica del DataFrame."""
    if datos is None:
        print("No existen datos disponibles para inspeccionar.")
        return
    print("\nDimensiones:")
    print(datos.shape)
    print("\nColumnas:")
    print(datos.columns.tolist())
    print("\nTipos de datos:")
    print(datos.dtypes)
    print("\nPrimeros registros:")
    print(datos.head())
    print("\nValores nulos por columna:")
    print(datos.isna().sum())
    print("\nFilas duplicadas:")
    print(datos.duplicated().sum())
    print("\nResumen estadistico:")
    print(datos.describe(include="all"))
