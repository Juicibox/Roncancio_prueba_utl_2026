WITH votos_partido AS (

    SELECT
        codigo_municipio,
        zona,
        puesto,
        mesa,
        codigo_partido,
        SUM(votos) AS votos_partido
    FROM resultados
    GROUP BY
        codigo_municipio,
        zona,
        puesto,
        mesa,
        codigo_partido

),

votos_candidato AS (

    SELECT
        codigo_municipio,
        zona,
        puesto,
        mesa,
        codigo_partido,
        codigo_candidato,
        SUM(votos) AS votos_candidato
    FROM resultados
    GROUP BY
        codigo_municipio,
        zona,
        puesto,
        mesa,
        codigo_partido,
        codigo_candidato

)

SELECT

    m.nombre AS municipio,

    vc.zona,

    vc.puesto,

    vc.mesa,

    p.nombre AS partido,

    c.nombre AS candidato,

    vc.votos_candidato,

    vp.votos_partido,

    ROUND(
        100.0 * vc.votos_candidato /
        vp.votos_partido,
        2
    ) AS porcentaje

FROM votos_candidato vc

INNER JOIN votos_partido vp

    ON vc.codigo_municipio = vp.codigo_municipio
   AND vc.zona = vp.zona
   AND vc.puesto = vp.puesto
   AND vc.mesa = vp.mesa
   AND vc.codigo_partido = vp.codigo_partido

INNER JOIN municipios m
    ON vc.codigo_municipio = m.codigo

INNER JOIN partidos p
    ON vc.codigo_partido = p.codigo

INNER JOIN candidatos c
    ON vc.codigo_candidato = c.codigo

WHERE

    100.0 * vc.votos_candidato / vp.votos_partido > 60

ORDER BY

    porcentaje DESC,
    municipio,
    vc.puesto,
    vc.mesa;