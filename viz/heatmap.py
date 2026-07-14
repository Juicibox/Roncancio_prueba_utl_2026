from pathlib import Path
import sqlite3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# Configuración
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "db" / "puestos_2026.db"

OUTPUT = BASE_DIR / "viz" / "heatmap_municipios.png"

# ==========================================
# Conexión
# ==========================================

conn = sqlite3.connect(DB_FILE)

# ==========================================
# Consulta
# ==========================================

df = pd.read_sql(
    """
    SELECT
        m.nombre AS municipio,
        r.nombre_candidato AS candidato,
        SUM(r.votos) AS votos
    FROM resultados r
    JOIN municipios m
        ON r.codigo_municipio = m.codigo
    WHERE r.corporacion='CAMARA'
      AND r.codigo_candidato<>0
    GROUP BY
        municipio,
        candidato;
    """,
    conn
)

conn.close()

# ==========================================
# Calcular porcentaje por municipio
# ==========================================

totales = (
    df
    .groupby("municipio")["votos"]
    .transform("sum")
)

df["porcentaje"] = (
    df["votos"] / totales * 100
)

# ==========================================
# Top 8 candidatos (global)
# ==========================================

top8 = (
    df
    .groupby("candidato")["votos"]
    .sum()
    .nlargest(8)
    .index
)

df = df[
    df["candidato"].isin(top8)
]

# ==========================================
# Pivot
# ==========================================

tabla = (
    df
    .pivot(
        index="candidato",
        columns="municipio",
        values="porcentaje"
    )
    .fillna(0)
)

# Mantener el orden solicitado

orden = [
    "TUNJA",
    "DUITAMA",
    "SOGAMOSO",
    "PAIPA"
]

tabla = tabla[orden]

# ==========================================
# Figura
# ==========================================

fig, ax = plt.subplots(figsize=(8,6))

im = ax.imshow(
    tabla.values,
    aspect="auto"
)

# Etiquetas

ax.set_xticks(np.arange(len(tabla.columns)))
ax.set_xticklabels(tabla.columns)

ax.set_yticks(np.arange(len(tabla.index)))
ax.set_yticklabels(tabla.index)

plt.setp(
    ax.get_xticklabels(),
    rotation=45,
    ha="right"
)

# ==========================================
# Anotaciones
# ==========================================
maximo = tabla.values.max()

for i in range(tabla.shape[0]):
    for j in range(tabla.shape[1]):

        valor = tabla.iloc[i, j]

        color = "white" if valor > maximo/2 else "black"

        ax.text(
            j,
            i,
            f"{valor:.1f}%",
            ha="center",
            va="center",
            color=color,
            fontsize=9
        )

# Barra de color

cbar = fig.colorbar(im)

cbar.set_label("% votos")

# Título

ax.set_title(
    "Top 8 candidatos Cámara\nParticipación porcentual por municipio"
)

plt.tight_layout()

OUTPUT.parent.mkdir(exist_ok=True)

plt.savefig(
    OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Heatmap generado correctamente.")
print(OUTPUT)