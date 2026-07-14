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

OUTPUT = BASE_DIR / "viz" / "scatter_ca_se.png"

conn = sqlite3.connect(DB_FILE)

# ==========================================
# Consulta
# ==========================================

df = pd.read_sql(
"""
WITH camara AS (

    SELECT
        codigo_municipio,
        zona,
        puesto,
        mesa,
        SUM(votos) AS votos_ca
    FROM resultados
    WHERE corporacion='CAMARA'
    GROUP BY
        codigo_municipio,
        zona,
        puesto,
        mesa

),

senado AS (

    SELECT
        codigo_municipio,
        zona,
        puesto,
        mesa,
        SUM(votos) AS votos_se
    FROM resultados
    WHERE corporacion='SENADO'
    GROUP BY
        codigo_municipio,
        zona,
        puesto,
        mesa

)

SELECT

m.nombre AS municipio,

c.zona,

c.puesto,

c.mesa,

c.votos_ca,

COALESCE(s.votos_se,0) AS votos_se

FROM camara c

LEFT JOIN senado s

ON c.codigo_municipio=s.codigo_municipio
AND c.zona=s.zona
AND c.puesto=s.puesto
AND c.mesa=s.mesa

JOIN municipios m

ON c.codigo_municipio=m.codigo

ORDER BY municipio, c.puesto, c.mesa;

""",
conn
)

conn.close()

# ==========================================
# Estadísticos
# ==========================================

x = df["votos_ca"].values
y = df["votos_se"].values

pendiente, intercepto = np.polyfit(x, y, 1)

r = np.corrcoef(x, y)[0,1]
colores = {
    "TUNJA":"tab:blue",
    "DUITAMA":"tab:orange",
    "SOGAMOSO":"tab:green",
    "PAIPA":"tab:red"
}

fig, ax = plt.subplots(figsize=(8,6))

for municipio, grupo in df.groupby("municipio"):

    ax.scatter(

        grupo["votos_ca"],
        grupo["votos_se"],

        label=municipio,

        alpha=.7,

        color=colores.get(municipio,"gray")
    )


x_line = np.linspace(
    x.min(),
    x.max(),
    100
)

y_line = pendiente*x_line + intercepto

ax.plot(
    x_line,
    y_line,
    color="black",
    linewidth=2,
    label="OLS"
)

ax.text(

0.03,

0.97,

f"r = {r:.3f}",

transform=ax.transAxes,

verticalalignment="top",

bbox=dict(
    facecolor="white",
    alpha=.8
)

)

ax.set_title("Cámara vs Senado por mesa")

ax.set_xlabel("Votos Cámara")

ax.set_ylabel("Votos Senado")

ax.legend()

plt.tight_layout()

OUTPUT.parent.mkdir(exist_ok=True)

plt.savefig(
    OUTPUT,
    dpi=300
)

plt.close()

print(
    f"r={r:.3f} | pendiente={pendiente:.3f} | n_mesas={len(df)}"
)

print("Scatter generado correctamente.")
print(df.shape)
print(OUTPUT)