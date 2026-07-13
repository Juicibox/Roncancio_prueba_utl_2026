from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "db" / "puestos_2026.db"
SCHEMA_FILE = BASE_DIR / "db" / "schema.sql"
CSV_FILE = BASE_DIR / "sample_data" / "MMV_filtrado.csv"

def conectar_db():
    """
    Crea la conexión con SQLite.
    """
    conn = sqlite3.connect(DB_FILE)

    conn.execute("PRAGMA foreign_keys = ON;")

    return conn

def crear_esquema(conn):
    """
    Crea las tablas de la base de datos.
    """

    with SCHEMA_FILE.open("r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.commit()

def normalizar_texto(serie):
    """
    Normaliza una columna de texto.
    """
    return (
        serie
        .fillna("")
        .str.strip()
        .str.title()
        .str.replace(r"\s+", " ", regex=True)
    )

def cargar_csv():
    """
    Carga el archivo filtrado.
    """

    return pd.read_csv(
        CSV_FILE,
        sep=","
    )

    # Columnas normalizadas
    for columna in ["PARNOMBRE", "CANNOMBRE"]:
        df[columna] = normalizar_texto(df[columna])

    return df

def cargar_municipios(conn, df):
    """
    Inserta los municipios en la base de datos.
    """

    municipios = (
        df[
            ["MUN", "MUNNOMBRE", "DEPNOMBRE"]
        ]
        .drop_duplicates()
        .sort_values("MUN")
    )

    datos = [
        (
            row.MUN,
            row.MUNNOMBRE,
            row.DEPNOMBRE
        )
        for row in municipios.itertuples(index=False)
    ]

    conn.executemany(
        """
        INSERT OR IGNORE INTO municipios
        (codigo, nombre, departamento)
        VALUES (?, ?, ?)
        """,
        datos
    )

    conn.commit()

    print(f" Municipios cargados: {len(datos)}")

def cargar_partidos(conn, df):

    partidos = (
        df[
            ["PAR", "PARNOMBRE"]
        ]
        .drop_duplicates()
        .sort_values("PAR")
    )

    datos = [
        (
            row.PAR,
            row.PARNOMBRE
        )
        for row in partidos.itertuples(index=False)
    ]

    conn.executemany(
        """
        INSERT OR IGNORE INTO partidos
        (codigo, nombre)
        VALUES (?, ?)
        """,
        datos
    )

    conn.commit()

    print(f"Partidos cargados: {len(datos)}")

def cargar_candidatos(conn, df):
    """
    Inserta los candidatos en la base de datos.
    """

    candidatos = (
        df[
            ["CAN", "CANNOMBRE", "CANCEDULA", "PAR"]
        ]
        .groupby("CAN", as_index=False)
        .first()
        .sort_values("CAN")
    )

    datos = [
        (
            row.CAN,
            row.CANNOMBRE,
            row.CANCEDULA,
            row.PAR
        )
        for row in candidatos.itertuples(index=False)
    ]

    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO candidatos
            (codigo, nombre, cedula, codigo_partido)
            VALUES (?, ?, ?, ?)
            """,
            datos
        )

    print(f"Candidatos cargados: {len(datos)}")

def cargar_resultados(conn, df):
    """
    Inserta los resultados electorales en la base de datos.
    """

    print("Cargando resultados...")

    datos = list(
        df[
            [
                "MUN",
                "CORNOMBRE",
                "ZONA",
                "PUESTO",
                "PUESNOMBRE",
                "MESA",
                "CIR",
                "COMUNOMBRE",
                "PAR",
                "CAN",
                "VOTOS"
            ]
        ].itertuples(index=False, name=None)
    )

    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO resultados (
                codigo_municipio,
                corporacion,
                zona,
                puesto,
                nombre_puesto,
                mesa,
                circunscripcion,
                comunidad,
                codigo_partido,
                codigo_candidato,
                votos
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            datos
        )

    print(f" Resultados cargados: {len(datos)}")

def registrar_carga(conn, archivo, registros, observaciones="Carga exitosa"):
    with conn:
        conn.execute(
            """
            INSERT INTO carga_log (
                proceso,
                archivo,
                registros_insertados,
                observaciones
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "ETL",
                archivo,
                registros,
                observaciones
            )
        )

def main():

    conn = None

    try:

        conn = conectar_db()

        crear_esquema(conn)

        df = cargar_csv()

        cargar_municipios(conn, df)

        cargar_partidos(conn, df)

        cargar_candidatos(conn, df)

        cargar_resultados(conn, df)

        registrar_carga(
            conn,
            CSV_FILE.name,
            len(df)
        )

        print("\nETL finalizado correctamente.")

    except Exception as e:

        print(f"\nError: {e}")

    finally:

        if conn:
            conn.close()

if __name__ == "__main__":
    main()