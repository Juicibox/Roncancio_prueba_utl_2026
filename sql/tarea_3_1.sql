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

    m.codigo AS codigo_municipio,
    m.nombre AS municipio,

    c.zona,
    c.puesto,
    c.nombre_puesto,

    c.votos_camara,

    COALESCE(s.votos_senado, 0) AS votos_senado,

    ROUND(
        CAST(COALESCE(s.votos_senado, 0) AS REAL)
        / NULLIF(c.votos_camara, 0),
        4
    ) AS ratio

FROM votos_camara c

INNER JOIN votos_senado s
       ON c.codigo_municipio = s.codigo_municipio
      AND c.zona = s.zona
      AND c.puesto = s.puesto
      AND c.nombre_puesto = s.nombre_puesto

INNER JOIN municipios m
        ON c.codigo_municipio = m.codigo

ORDER BY
    m.nombre,
    c.zona,
    c.puesto;