PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS  municipios (

    codigo INTEGER PRIMARY KEY,

    nombre TEXT NOT NULL,

    departamento TEXT NOT NULL

);

CREATE TABLE IF NOT EXISTS partidos (
    codigo INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS candidatos (
    codigo INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    cedula TEXT,
    codigo_partido INTEGER NOT NULL,

    FOREIGN KEY (codigo_partido)
        REFERENCES partidos(codigo)
);

CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    codigo_municipio INTEGER NOT NULL,
    corporacion TEXT NOT NULL,
    nombre_candidato TEXT NOT NULL,

    zona INTEGER NOT NULL,
    puesto INTEGER NOT NULL,
    nombre_puesto TEXT NOT NULL,
    mesa INTEGER NOT NULL,

    circunscripcion INTEGER,
    comunidad TEXT,

    codigo_partido INTEGER NOT NULL,
    codigo_candidato INTEGER NOT NULL,

    votos INTEGER NOT NULL,

    FOREIGN KEY (codigo_municipio) REFERENCES municipios(codigo),
    FOREIGN KEY (codigo_partido) REFERENCES partidos(codigo),
    FOREIGN KEY (codigo_candidato) REFERENCES candidatos(codigo),

    UNIQUE (
        codigo_municipio,
        corporacion,
        puesto,
        mesa,
        codigo_partido,
        codigo_candidato
    )
);

CREATE TABLE IF NOT EXISTS carga_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    proceso TEXT NOT NULL,
    archivo TEXT NOT NULL,
    registros_insertados INTEGER NOT NULL,
    observaciones TEXT
);

CREATE INDEX IF NOT EXISTS idx_resultados_municipio
ON resultados(codigo_municipio);

CREATE INDEX IF NOT EXISTS idx_resultados_corporacion
ON resultados(corporacion);

CREATE INDEX IF NOT EXISTS idx_resultados_partido
ON resultados(codigo_partido);

CREATE INDEX IF NOT EXISTS idx_resultados_candidato
ON resultados(codigo_candidato);

CREATE INDEX IF NOT EXISTS idx_resultados_municipio_corporacion
ON resultados(codigo_municipio, corporacion);