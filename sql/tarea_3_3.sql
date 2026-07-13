WITH votos_candidato_ca AS (

    SELECT
        codigo_municipio,
        codigo_candidato,
        SUM(votos) AS votos_candidato
    FROM resultados
    WHERE corporacion = 'CAMARA'
      AND codigo_partido = 4
      AND codigo_candidato <> 0
    GROUP BY
        codigo_municipio,
        codigo_candidato

),

votos_partido_ca AS (

    SELECT
        codigo_municipio,
        SUM(votos) AS votos_partido
    FROM resultados
    WHERE corporacion = 'CAMARA'
      AND codigo_partido = 4
    GROUP BY
        codigo_municipio

),

votos_partido_se AS (

    SELECT
        codigo_municipio,
        SUM(votos) AS votos_se
    FROM resultados
    WHERE corporacion = 'SENADO'
      AND codigo_partido = 3020
    GROUP BY
        codigo_municipio

),

atribucion AS (

    SELECT

        vc.codigo_candidato,

        (
            CAST(vc.votos_candidato AS REAL)
            / vp.votos_partido
        ) * COALESCE(vs.votos_se, 0) AS atribucion

    FROM votos_candidato_ca vc

    INNER JOIN votos_partido_ca vp
        ON vc.codigo_municipio = vp.codigo_municipio

    LEFT JOIN votos_partido_se vs
        ON vc.codigo_municipio = vs.codigo_municipio

)

SELECT

    c.codigo,

    c.nombre AS candidato,

    ROUND(SUM(a.atribucion), 2) AS atribucion_total

FROM atribucion a

INNER JOIN candidatos c
    ON a.codigo_candidato = c.codigo

GROUP BY
    c.codigo,
    c.nombre

ORDER BY
    atribucion_total DESC

LIMIT 5;