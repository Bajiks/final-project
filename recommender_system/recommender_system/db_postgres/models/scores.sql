SELECT CAST(user_id as INT),
    CAST(movie_id as INT),
    CAST(rating as INT)
FROM {{ source('recommender_system_raw', 'scores') }}
