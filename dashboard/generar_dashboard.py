from pathlib import Path
import sqlite3
import pandas as pd
import json

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "db" / "puestos_2026.db"

OUTPUT_HTML = BASE_DIR / "dashboard" / "index.html"


conn = sqlite3.connect(DB_FILE)

df_municipios = pd.read_sql("""
SELECT
    m.nombre,
    SUM(r.votos) AS votos
FROM resultados r
JOIN municipios m
    ON r.codigo_municipio = m.codigo
WHERE corporacion='CAMARA'
GROUP BY m.nombre
ORDER BY votos DESC;
""", conn)

df_top10 = pd.read_sql("""
SELECT
    m.nombre AS municipio,
    r.nombre_candidato AS candidato,
    r.codigo_partido,
    p.nombre AS partido,
    SUM(r.votos) AS votos
FROM resultados r
JOIN municipios m
    ON r.codigo_municipio = m.codigo
JOIN partidos p
    ON r.codigo_partido = p.codigo
WHERE r.corporacion = 'CAMARA'
  AND r.codigo_candidato <> 0
GROUP BY
    m.nombre,
    r.nombre_candidato,
    r.codigo_partido,
    p.nombre
ORDER BY
    municipio,
    votos DESC;
""", conn)

# print(df_top10.head(15))

df_lider = pd.read_sql("""
WITH votos_partido AS (

    SELECT
        m.nombre AS municipio,
        p.nombre AS partido,
        SUM(r.votos) AS votos
    FROM resultados r
    JOIN municipios m
        ON r.codigo_municipio = m.codigo
    JOIN partidos p
        ON r.codigo_partido = p.codigo
    WHERE r.corporacion = 'SENADO'
      AND p.nombre <> 'CANDIDATOS TOTALES'
    GROUP BY
        municipio,
        partido

)

SELECT *
FROM votos_partido
ORDER BY municipio, votos DESC;
""", conn)

# print(df_lider.head(10))

df_ratio = pd.read_sql("""
WITH votos_camara AS (

    SELECT
        codigo_municipio,
        zona,
        puesto,
        nombre_puesto,
        SUM(votos) AS votos_camara
    FROM resultados
    WHERE corporacion = 'CAMARA'
      AND codigo_partido = 4
    GROUP BY
        codigo_municipio,
        zona,
        puesto,
        nombre_puesto

),

votos_senado AS (

    SELECT
        codigo_municipio,
        zona,
        puesto,
        nombre_puesto,
        SUM(votos) AS votos_senado
    FROM resultados
    WHERE corporacion = 'SENADO'
      AND codigo_partido = 3020
    GROUP BY
        codigo_municipio,
        zona,
        puesto,
        nombre_puesto

)

SELECT
    m.nombre AS municipio,
    c.puesto,
    c.nombre_puesto,
    c.votos_camara,
    COALESCE(s.votos_senado,0) AS votos_senado,
    ROUND(
        CAST(COALESCE(s.votos_senado,0) AS REAL) /
        NULLIF(c.votos_camara,0),
        4
    ) AS ratio
FROM votos_camara c
LEFT JOIN votos_senado s
    ON c.codigo_municipio = s.codigo_municipio
   AND c.zona = s.zona
   AND c.puesto = s.puesto
   AND c.nombre_puesto = s.nombre_puesto
JOIN municipios m
    ON c.codigo_municipio = m.codigo
ORDER BY
    municipio,
    c.puesto;
""", conn)

# print(df_ratio.head())

# -----------------------------
# Convertir DataFrames a JSON
# -----------------------------

municipios_json = json.dumps(
    df_municipios.to_dict(orient="records"),
    ensure_ascii=False
)

top10_json = json.dumps(
    df_top10.to_dict(orient="records"),
    ensure_ascii=False
)

lider_json = json.dumps(
    df_lider.to_dict(orient="records"),
    ensure_ascii=False
)

ratio_json = json.dumps(
    df_ratio.to_dict(orient="records"),
    ensure_ascii=False
)

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {{
    --bg-color: #f5f7fa;
    --panel-bg: #ffffff;
    --text-color: #1f2937;
    --text-muted: #666666;
    --card-shadow: rgba(0, 0, 0, 0.08);
    --border-color: #e2e8f0;
    --card-bg: #ffffff;
    --lider-bg: #f8fafc;
    --dropdown-bg: #ffffff;
    --dropdown-text: #1f2937;
}}

[data-theme="dark"] {{
    --bg-color: #0f172a;
    --panel-bg: #1e293b;
    --text-color: #f8fafc;
    --text-muted: #94a3b8;
    --card-shadow: rgba(0, 0, 0, 0.3);
    --border-color: #334155;
    --card-bg: #1e293b;
    --lider-bg: #1e293b;
    --dropdown-bg: #334155;
    --dropdown-text: #f8fafc;
}}

body{{
    margin:0;
    padding:25px;
    background: var(--bg-color);
    color: var(--text-color);
    font-family:Arial,Helvetica,sans-serif;
    transition: background 0.3s, color 0.3s;
}}

h1{{
    margin:0;
    color: var(--text-color);
}}

h2{{
    margin-top:0;
    color: var(--text-color);
}}

.container{{
    max-width:1400px;
    margin:auto;
}}

.header-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 15px;
    margin-bottom: 15px;
}}

.cards{{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:15px;
    margin-top:25px;
}}

.card{{
    background: var(--card-bg);
    color: var(--text-color);
    padding:20px;
    border-radius:12px;
    box-shadow:0 3px 10px var(--card-shadow);
    text-align:center;
    transition: background 0.3s, box-shadow 0.3s;
}}

.card h3{{
    margin:0;
    color: var(--text-muted);
}}

.card h1{{
    margin-top:10px;
    color: var(--text-color);
}}

.panel{{
    background: var(--panel-bg);
    margin-top:20px;
    padding:20px;
    border-radius:12px;
    box-shadow:0 3px 10px var(--card-shadow);
    transition: background 0.3s, box-shadow 0.3s;
}}

.controls-row {{
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 20px;
}}

select{{
    padding:8px 12px;
    font-size:16px;
    background: var(--dropdown-bg);
    color: var(--dropdown-text);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    cursor: pointer;
}}

button {{
    padding: 8px 16px;
    font-size: 14px;
    font-weight: bold;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    cursor: pointer;
    background: #007C34;
    color: white;
    transition: opacity 0.2s, background 0.2s;
}}

button:hover {{
    opacity: 0.9;
}}

.theme-toggle-btn {{
    background: var(--panel-bg);
    color: var(--text-color);
    border: 1px solid var(--border-color);
}}

#g1,#g2,#g3{{
    width:100%;
    height:450px;
}}

</style>
</head>

<body>

<div class="container">

<div class="header-container">
    <div>
        <h1>🗳️ Análisis de Resultados Congreso </h1>
        <p style="color: var(--text-muted); margin: 5px 0 0 0;">Resultados electorales • Boyacá 2026</p>
    </div>
    <button class="theme-toggle-btn" id="themeToggleBtn">🌙 Modo Oscuro</button>
</div>

<div class="cards">

<div class="card">
<h3>Municipios</h3>
<h1>{len(df_municipios)}</h1>
</div>

<div class="card">
<h3>Candidatos</h3>
<h1>{df_top10["candidato"].nunique()}</h1>
</div>

<div class="card">
<h3>Partidos</h3>
<h1>{df_top10["partido"].nunique()}</h1>
</div>

<div class="card">
<h3>Registros</h3>
<h1>{len(df_ratio)}</h1>
</div>

</div>

<div class="panel">

<h2>Comparativo votos Cámara</h2>

<div id="g1"></div>

</div>

<div class="panel">

<h2>Municipio</h2>

<div class="controls-row">
    <select id="municipio"></select>
    <button id="exportCsvBtn">📥 Exportar Municipio a CSV</button>
</div>

<div id="liderCard"
style="
background: var(--lider-bg);
padding:18px;
border-left:8px solid #007C34;
border-radius:10px;
margin-bottom:20px;
border-top: 1px solid var(--border-color);
border-right: 1px solid var(--border-color);
border-bottom: 1px solid var(--border-color);
">

<h3 style="margin:0;color: var(--text-muted);">
Partido líder Senado
</h3>

<h2 id="liderNombre" style="margin-top:10px;">
-
</h2>

<h3 id="liderVotos">
-
</h3>

</div>

<div id="g2"></div>

</div>

<div class="panel">

<h2>Ratio Verde Senado / Cámara</h2>

<div id="g3"></div>

</div>

<div style="
margin-top:30px;
text-align:center;
color:gray;
font-size:13px;
">

Election Analytics Challenge • Dashboard desarrollado con Python, SQLite y Plotly

</div>

<script>

const municipios = {municipios_json};
const top10 = {top10_json};
const lider = {lider_json};
const ratio = {ratio_json};

//=============================
// Colores
//=============================

const colores = {{
    verde:"#007C34",
    pacto:"#7B2D8B",
    centro:"#1E477D",
    conservador:"#E07B00",
    gris:"#4B5563"
}};

//=============================
// Tema Claro / Oscuro - Auxiliares
//=============================

function isDarkTheme() {{
    return document.documentElement.getAttribute('data-theme') === 'dark';
}}

function getTextColor() {{
    return isDarkTheme() ? '#f8fafc' : '#1f2937';
}}

function getGridColor() {{
    return isDarkTheme() ? '#334155' : '#e2e8f0';
}}

function getPlotlyConfig(titleText) {{
    const textColor = getTextColor();
    const gridColor = getGridColor();
    return {{
        title: {{
            text: titleText,
            font: {{ color: textColor }}
        }},
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {{ color: textColor }},
        xaxis: {{ 
            gridcolor: gridColor, 
            tickfont: {{ color: textColor }},
            linecolor: gridColor
        }},
        yaxis: {{ 
            gridcolor: gridColor, 
            tickfont: {{ color: textColor }},
            linecolor: gridColor
        }}
    }};
}}

//=============================
// Selector municipios
//=============================

const selector=document.getElementById("municipio");

municipios.forEach(m=>{{
    const op=document.createElement("option");
    op.value=m.nombre;
    op.textContent=m.nombre;
    selector.appendChild(op);
}});

//=============================
// Grafico 1
//=============================

Plotly.newPlot(
'g1',
[{{
    x:municipios.map(x=>x.nombre),
    y:municipios.map(x=>x.votos),
    type:'bar',
    marker:{{
        color:colores.verde
    }}
}}],
Object.assign(getPlotlyConfig('Votos Cámara por municipio'), {{
    margin:{{t:50}}
}})
);

function colorPartido(codigo){{
    codigo = Number(codigo);
    switch(codigo){{
        // Liberal
        case 1:
            return "#D32F2F";

        // Conservador
        case 2:
        case 3093:
            return "#E07B00";

        // Alianza Verde
        case 4:
        case 3020:
            return "#007C34";

        // Centro Democrático
        case 11:
            return "#1E477D";

        // Pacto Histórico
        case 3058:
        case 3063:
            return "#7B2D8B";

        default:
            return "#9CA3AF";
    }}
}}

//=============================
// Funcion actualizar
//=============================

function actualizar(){{

const muni=selector.value;

//========================
// Partido líder Senado
//========================

let liderMunicipio = lider
    .filter(x => x.municipio === muni)
    .sort((a,b)=>b.votos-a.votos)[0];

document.getElementById("liderNombre").innerHTML =
liderMunicipio.partido;

document.getElementById("liderVotos").innerHTML =
liderMunicipio.votos.toLocaleString()+" votos";


//-----------------------------
// TOP 10
//-----------------------------

let datosTop=top10
.filter(x=>x.municipio===muni)
.sort((a,b)=>b.votos-a.votos)
.slice(0,10);


Plotly.newPlot(
'g2',
[{{
    x:datosTop.map(x=>x.votos),
    y:datosTop.map(x=>x.candidato),
    orientation:'h',
    type:'bar',
    marker:{{
        color:datosTop.map(x=>colorPartido(x.codigo_partido))
    }}
}}],
Object.assign(getPlotlyConfig('Top 10 candidatos Cámara'), {{
    margin:{{l:250,t:50}}
}})
);


//-----------------------------
// Ratio Verde
//-----------------------------

let datosRatio=ratio.filter(x=>x.municipio===muni);

Plotly.newPlot(
'g3',
[{{
    x:datosRatio.map(x=>x.nombre_puesto),
    y:datosRatio.map(x=>x.ratio),
    mode:'lines+markers',
    line:{{color:colores.verde}}
}}],
Object.assign(getPlotlyConfig('Ratio Verde Senado/Cámara'), {{
    shapes:[{{
        type:'line',
        x0:0,
        x1:1,
        xref:'paper',
        y0:1,
        y1:1,
        line:{{
            color:'red',
            dash:'dash'
        }}
    }}],
    margin:{{
        l:60,
        r:20,
        t:50,
        b:180
    }}
}})
);

}}

selector.addEventListener(
"change",
actualizar
);

//=============================
// Alternador Tema Oscuro / Claro
//=============================

const themeToggleBtn = document.getElementById("themeToggleBtn");

function setTheme(theme) {{
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    if (theme === "dark") {{
        themeToggleBtn.textContent = "☀️ Modo Claro";
    }} else {{
        themeToggleBtn.textContent = "🌙 Modo Oscuro";
    }}
    
    // Redibujar gráficos para aplicar los nuevos colores de fuente y fondo
    const textColor = getTextColor();
    const gridColor = getGridColor();
    const update = {{
        font: {{ color: textColor }},
        xaxis: {{ 
            gridcolor: gridColor, 
            tickfont: {{ color: textColor }},
            linecolor: gridColor
        }},
        yaxis: {{ 
            gridcolor: gridColor, 
            tickfont: {{ color: textColor }},
            linecolor: gridColor
        }},
        title: {{
            font: {{ color: textColor }}
        }}
    }};
    
    if (document.getElementById('g1').classList.contains('js-plotly-plot')) {{
        Plotly.relayout('g1', update);
    }}
    if (document.getElementById('g2').classList.contains('js-plotly-plot')) {{
        Plotly.relayout('g2', update);
    }}
    if (document.getElementById('g3').classList.contains('js-plotly-plot')) {{
        Plotly.relayout('g3', update);
    }}
}}

themeToggleBtn.addEventListener("click", () => {{
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    setTheme(newTheme);
}});

// Detectar preferencia guardada o del sistema
const savedTheme = localStorage.getItem("theme");
const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
if (savedTheme) {{
    setTheme(savedTheme);
}} else if (systemPrefersDark) {{
    setTheme("dark");
}} else {{
    setTheme("light");
}}

//=============================
// Exportación a CSV
////=============================

document.getElementById("exportCsvBtn").addEventListener("click", () => {{
    const muni = selector.value;
    const datosTop = top10
        .filter(x => x.municipio === muni)
        .sort((a,b)=>b.votos-a.votos)
        .slice(0,10);

    let csvContent = "data:text/csv;charset=utf-8,\\uFEFF";
    csvContent += "Municipio,Candidato,Partido,Votos\\n";

    datosTop.forEach(row => {{
        const candidatoEscaped = '"' + row.candidato.replace(/"/g, '""') + '"';
        const partidoEscaped = '"' + row.partido.replace(/"/g, '""') + '"';
        csvContent += row.municipio + ',' + candidatoEscaped + ',' + partidoEscaped + ',' + row.votos + '\\n';
    }});

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "resultados_camara_" + muni.toLowerCase() + ".csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}});

//=============================
// Primer dibujo
//=============================

selector.selectedIndex=0;
actualizar();

</script>

</body>
</html>
"""

OUTPUT_HTML.write_text(
    html,
    encoding="utf-8"
)

conn.close()

print("Dashboard generado correctamente.")
print(OUTPUT_HTML)