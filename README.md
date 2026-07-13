# Election Analytics Challenge

## Descripción

Este proyecto desarrolla una solución integral para el análisis de resultados electorales utilizando información oficial de la Registraduría Nacional del Estado Civil. La solución comprende el proceso completo de extracción, transformación y carga (ETL), el diseño de una base de datos relacional, la implementación de consultas SQL para resolver los retos propuestos y la construcción de un dashboard interactivo para la visualización de los resultados.

El objetivo principal es demostrar buenas prácticas en ingeniería de datos, modelado relacional, análisis mediante SQL y visualización de información, manteniendo una arquitectura sencilla, reproducible y fácilmente escalable.

---

# Arquitectura del proyecto

```text
                Registraduría Nacional
                         │
                         ▼
                    MMV.csv (Original)
                         │
                         ▼
              Limpieza y filtrado (Python)
                         │
                         ▼
                  MMV_filtrado.csv
                         │
                         ▼
                   ETL (Pandas + SQLite)
                         │
                         ▼
              Base de datos relacional
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
   Consultas SQL                  Dashboard
```

---

# Estructura del proyecto

```text
election-analytics/
│
├── README.md
├── requirements.txt
│
├── scraper/
│   └── scraper.py
│
├── sample_data/
│   ├── MMV.csv
│   └── MMV_filtrado.csv
│
├── db/
│   ├── schema.sql
│   ├── etl.py
│   └── puestos_2026.db
│
├── sql/
│   ├── reto_3_1.sql
│   ├── reto_3_2.sql
│   └── reto_3_3.sql
│
├── dashboard/
│   └── app.py
│
└── docs/
```

---

# Tecnologías utilizadas

* Python 3
* Pandas
* SQLite
* SQL
* Streamlit
* Plotly
* Git

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/election-analytics.git
cd election-analytics
```

## 2. Crear entorno virtual

```bash
python -m venv .venv
```

Activar el entorno:

Windows

```bash
.venv\Scripts\activate
```

Linux / Mac

```bash
source .venv/bin/activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Ejecución

## 1. Procesar el archivo original

```bash
python scraper/scraper.py
```

Este proceso:

* Lee el archivo oficial `MMV.csv`.
* Filtra únicamente los municipios de interés.
* Genera `MMV_filtrado.csv`.

---

## 2. Ejecutar el ETL

```bash
python db/etl.py
```

El proceso ETL realiza automáticamente:

* Creación del esquema de base de datos.
* Carga del archivo CSV.
* Limpieza de datos.
* Normalización de texto.
* Inserción de municipios.
* Inserción de partidos.
* Inserción de candidatos.
* Inserción de resultados electorales.
* Registro de la carga realizada.

---

## 3. Ejecutar el dashboard

```bash
streamlit run dashboard/app.py
```

---

# Modelo de datos

El proyecto utiliza una base de datos relacional diseñada para minimizar redundancia y facilitar las consultas analíticas.

## municipios

Contiene el catálogo de municipios utilizados durante el análisis.

| Campo        | Descripción  |
| ------------ | ------------ |
| codigo       | Código DANE  |
| nombre       | Municipio    |
| departamento | Departamento |

---

## partidos

Catálogo de partidos políticos.

| Campo  | Descripción        |
| ------ | ------------------ |
| codigo | Código del partido |
| nombre | Nombre del partido |

---

## candidatos

Información de los candidatos.

| Campo          | Descripción          |
| -------------- | -------------------- |
| codigo         | Código del candidato |
| nombre         | Nombre               |
| cedula         | Documento            |
| codigo_partido | Partido político     |

---

## resultados

Tabla de hechos del modelo.

Cada registro representa la cantidad de votos obtenidos por un candidato en una mesa determinada.

Principales variables:

* municipio
* corporación
* zona
* puesto
* mesa
* partido
* candidato
* votos

---

## carga_log

Tabla utilizada para registrar cada ejecución del proceso ETL.

---

# Proceso ETL

El proceso ETL fue implementado completamente en Python utilizando Pandas y SQLite.

Las principales etapas son:

## Extracción

* Lectura del archivo oficial MMV.csv.
* Validación de estructura.
* Lectura utilizando el separador correspondiente.

## Transformación

Durante esta etapa se realizaron procesos de limpieza como:

* eliminación de espacios innecesarios;
* normalización de cadenas de texto;
* manejo de valores nulos;
* eliminación de duplicados;
* generación de catálogos únicos;
* validación de claves foráneas.

## Carga

La carga se realiza respetando las dependencias del modelo:

1. municipios
2. partidos
3. candidatos
4. resultados
5. carga_log

Para evitar duplicados se utilizaron restricciones UNIQUE junto con la instrucción:

```sql
INSERT OR IGNORE
```

---

# Decisiones de diseño

## Modelo relacional

Se optó por separar las entidades principales en tablas independientes para reducir redundancia y mantener la integridad referencial mediante claves foráneas.

---

## Integridad

Se implementaron:

* Primary Keys
* Foreign Keys
* UNIQUE
* Índices para acelerar consultas

---

## Índices

Se crearon índices sobre:

* municipio
* corporación
* partido
* candidato

con el objetivo de optimizar las consultas analíticas.

---

# Reto 3

Las consultas solicitadas fueron implementadas utilizando Common Table Expressions (CTE), permitiendo una estructura clara, modular y fácilmente mantenible.

## 3.1 Ratio Senado / Cámara

Calcula el ratio:

```
votos_SE / votos_CA
```

para el partido homologado por puesto de votación y municipio.

---

## 3.2 Dominancia extrema

Identifica las mesas donde un candidato concentra más del 60 % de los votos obtenidos por su partido.

La consulta calcula:

```
(votos del candidato / votos del partido) × 100
```

y retorna únicamente los casos cuya participación supera el 60 %.

---

## 3.3 Atribución determinística

Calcula la atribución de votos de Senado hacia los candidatos utilizando la expresión:

```
Aij = (votos_candidato / votos_partido) × votos_SE_partido
```

Posteriormente consolida la atribución obtenida para cada candidato y presenta el Top 5 departamental.

---

# Homologación de partidos

El enunciado de la prueba hace referencia a la siguiente homologación:

```
Cámara : código 5

↓

Senado : código 57
```

Sin embargo, durante la validación del conjunto de datos descargado desde la Registraduría Nacional se encontró una codificación distinta.

La homologación equivalente utilizada en este proyecto corresponde a:

| Corporación | Código | Partido               |
| ----------- | ------ | --------------------- |
| Cámara      | 4      | PARTIDO ALIANZA VERDE |
| Senado      | 3020   | ALIANZA POR COLOMBIA  |

Las consultas SQL fueron adaptadas a esta codificación para mantener consistencia con el conjunto de datos realmente utilizado.

---

# Dashboard

El dashboard interactivo permitirá explorar la información mediante diferentes visualizaciones, incluyendo:

* KPIs generales.
* Participación por municipio.
* Distribución de votos por partido.
* Distribución de votos por candidato.
* Ranking de candidatos.
* Resultados por corporación.
* Mapas interactivos.
* Filtros por municipio, corporación, partido y candidato.

El objetivo es proporcionar una herramienta sencilla para explorar la información generada por la base de datos.

---

# Posibles mejoras

El proyecto fue desarrollado buscando simplicidad y claridad, aunque existen oportunidades de evolución, entre ellas:

* migración de SQLite a PostgreSQL;
* automatización del proceso ETL;
* incorporación de pruebas unitarias;
* despliegue mediante Docker;
* integración continua (CI/CD);
* conexión directa con fuentes oficiales de datos;
* actualización automática del dashboard.

---

# Conclusiones

La solución desarrollada implementa un flujo completo de ingeniería y análisis de datos, desde la adquisición de información hasta su explotación mediante consultas SQL y visualizaciones interactivas.

El proyecto prioriza una arquitectura relacional normalizada, procesos ETL reproducibles, consultas optimizadas mediante CTE e índices, y una documentación clara que facilita su mantenimiento y futura escalabilidad.
