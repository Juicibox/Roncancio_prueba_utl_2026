# Roncancio — Prueba Técnica UTL Senado 2026

## Candidato

**Nombre:** Juan Roncancio

Analista de Datos con experiencia en Python, SQL, SQLite, ETL y visualización de datos. La solución desarrollada implementa un flujo completo de ingeniería de datos para el análisis de resultados electorales utilizando información oficial de la Registraduría Nacional del Estado Civil.

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Juicibox/Roncancio_prueba_utl_2026

```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / Mac

```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Pipeline de ejecución

La arquitectura del proyecto sigue el siguiente flujo:

```text
Registraduría
      │
      ▼
MMV.csv
      │
      ▼
Filtrado municipios
      │
      ▼
MMV_filtrado.csv
      │
      ▼
ETL
      │
      ▼
SQLite
      │
 ┌────┴────┐
 ▼         ▼
SQL    Dashboard
```

Orden de ejecución:

```bash
python scraper/scraper.py
python db/etl.py
python dashboard/generar_dashboard.py
python viz/heatmap.py
python viz/scatter.py
```

Durante el ETL se realizan las siguientes tareas:

- Creación automática del esquema de base de datos.
- Limpieza y normalización de texto.
- Inserción de municipios.
- Inserción de partidos.
- Inserción de candidatos.
- Inserción de resultados electorales.
- Registro de la ejecución en `carga_log`.

La carga respeta el siguiente orden:

1. municipios
2. partidos
3. candidatos
4. resultados
5. carga_log

La base de datos utiliza claves primarias, claves foráneas, restricciones `UNIQUE` e índices para garantizar integridad y optimizar consultas.

---

## API

La información utilizada proviene del archivo oficial de resultados electorales suministrado por la Registraduría Nacional del Estado Civil.

El proyecto trabaja directamente sobre el archivo **MMV.csv**, del cual se genera un subconjunto filtrado (`MMV_filtrado.csv`) correspondiente a los municipios:

- Tunja
- Duitama
- Sogamoso
- Paipa

No requiere servidor ni servicios externos para ejecutar el dashboard.

---

## Municipios en la BD

Municipios cargados:

- Tunja
- Duitama
- Sogamoso
- Paipa

Resumen de la base de datos:

| Tabla | Registros |
|--------|----------:|
| Municipios | 4 |
| Partidos | 83 |
| Candidatos | 119 |
| Resultados | 110761 |

Modelo relacional:

- municipios
- partidos
- candidatos
- resultados
- carga_log

---

## Hallazgos principales

### Homologación de partidos

Durante la validación del conjunto de datos se encontró una codificación diferente a la descrita en el enunciado.

Se utilizó la siguiente homologación:

| Cámara | Senado |
|---------|--------|
| Código 4 — Partido Alianza Verde | Código 3020 — Alianza por Colombia |

Las consultas fueron adaptadas a esta codificación para mantener consistencia con los datos oficiales descargados.

### Ratio Senado / Cámara

Se calculó el ratio entre votos de Senado y Cámara para los partidos homologados por municipio y puesto de votación.

### Dominancia extrema

Se identificaron mesas donde un candidato concentra más del 60 % de la votación obtenida por su partido.

### Atribución determinística

La atribución se calculó mediante:

```
Aij = (Votos candidato / Votos partido Cámara) × Votos partido Senado
```

El ranking por atribución no coincide necesariamente con el ranking por votos en Cámara, ya que la atribución depende simultáneamente del desempeño individual del candidato y de la votación total obtenida por su partido en Senado.

### Dashboard

Se desarrolló un dashboard HTML autocontenido con:

- Comparativo de votos por municipio.
- Top 10 candidatos por municipio.
- Partido líder en Senado.
- Ratio Verde Senado/Cámara.


### Visualizaciones

Se generaron:

- `viz/heatmap_municipios.png`
- `viz/scatter_ca_se.png`

---

## Bonus implementados

### Índices SQLite 
Se implementaron índices sobre:

- municipio
- corporación
- partido
- candidato

Estos índices optimizan las consultas utilizadas por el dashboard y por los retos SQL.

### Explicación del reto 3.3 

El Top de candidatos en Cámara no necesariamente coincide con el Top de atribución en Senado porque la atribución distribuye los votos del partido de Senado de manera proporcional a la votación obtenida por cada candidato en Cámara.

Por esta razón, un candidato con una alta votación en Cámara puede no recibir la mayor atribución en Senado si su partido tuvo un bajo desempeño en dicha corporación.

