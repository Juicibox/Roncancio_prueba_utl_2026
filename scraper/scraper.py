from pathlib import Path
import pandas as pd
import argparse

MUNICIPIOS = [
    "TUNJA",
    "DUITAMA",
    "SOGAMOSO",
    "PAIPA"]

# Ruta a la carpeta raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Archivo original
INPUT_FILE = BASE_DIR / "sample_data" / "MMV.csv"

# Archivo filtrado
OUTPUT_FILE = BASE_DIR / "sample_data" / "MMV_filtrado.csv"

def obtener_argumentos():
    """
    Obtiene los argumentos de la línea de comandos.
    """

    parser = argparse.ArgumentParser(
        description="Filtra los resultados electorales por municipio."
    )

    parser.add_argument(
        "--municipios",
        nargs="+",
        default=MUNICIPIOS,
        help="Lista de municipios a filtrar."
    )

    return parser.parse_args()

def leer_csv():
    """
    Lee el archivo CSV oficial de la Registraduría ya que no está disponible el API.
    """

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {INPUT_FILE}"
        )

    print(f"Leyendo archivo: {INPUT_FILE.name}")

    # El documento CSV original tiene un separador de punto y coma, por lo que se debe especificar el parámetro sep=";" 
    df = pd.read_csv(
        INPUT_FILE,
        sep=";"
    )

    print(f"Registros cargados: {len(df):,}")

    return df

def filtrar_municipios(df, municipios):
    """
    Filtra únicamente los municipios requeridos para la prueba.
    """

    print("\nFiltrando municipios...")

    df_filtrado = df[df["MUNNOMBRE"].isin(municipios)].copy()

    print(f"Registros después del filtro: {len(df_filtrado):,}")

    print("Municipios encontrados:")
    print(df_filtrado["MUNNOMBRE"].value_counts())

    return df_filtrado

def guardar_csv(df):
    """
    Guarda el archivo filtrado en sample_data.
    """

    print("\nGuardando archivo filtrado...")

    df.to_csv(
        OUTPUT_FILE,
        sep=",",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Archivo guardado en: {OUTPUT_FILE}")

def main():

    args = obtener_argumentos()

    df = leer_csv()

    df_filtrado = filtrar_municipios(
        df,
        args.municipios
    )

    guardar_csv(df_filtrado)

    print("\nProceso finalizado correctamente.")


if __name__ == "__main__":
    main()