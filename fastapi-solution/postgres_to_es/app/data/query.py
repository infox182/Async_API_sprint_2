MOVIES_QUERY = """
SELECT
fw.id,
fw.title,
fw.description,
fw.rating as imdb_rating,
fw.creation_date,
COALESCE (JSON_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director'), '[]') AS directors_names,
COALESCE (JSON_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer'), '[]') AS writers_names,
COALESCE (JSON_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor'), '[]') AS actors_names,
COALESCE (
    json_agg(
        DISTINCT jsonb_build_object(
            'id', g.id,
            'name', g.name
        )
    ),
    '[]'
) as genres,
COALESCE (
    json_agg(
        DISTINCT jsonb_build_object(
            'id', p.id,
            'name', p.full_name
        )
    ) FILTER (WHERE pfw.role = 'director'),
    '[]'
) as directors,
COALESCE (
    json_agg(
        DISTINCT jsonb_build_object(
            'id', p.id,
            'name', p.full_name
        )
    ) FILTER (WHERE pfw.role = 'actor'),
    '[]'
) as actors,
COALESCE (
    json_agg(
        DISTINCT jsonb_build_object(
            'id', p.id,
            'name', p.full_name
        )
    ) FILTER (WHERE pfw.role = 'writer'),
    '[]'
) as writers
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.modified > '{date:}' OR p.modified > '{date:}' OR g.modified > '{date:}'
GROUP BY fw.id
ORDER BY fw.modified;
"""

GENRES_QUERY = """
SELECT
    g.id,
    g.name,
    g.description
FROM
    content.genre g
WHERE g.modified > '{date:}'
GROUP BY
    g.id
ORDER BY
    g.modified;

"""

PERSONS_QUERY = """
SELECT
    p.id,
    p.full_name as name
FROM
    content.person p
WHERE p.modified > '{date:}'
GROUP BY 
    p.id
ORDER BY 
    p.modified;
"""
