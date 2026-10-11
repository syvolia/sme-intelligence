with bounds as (
    select
        min(sale_date)::date as min_date,
        max(sale_date)::date as max_date
    from {{ ref('stg_sales') }}
),
spine as (
    select generate_series(min_date, max_date, interval '1 day')::date as full_date
    from bounds
)
select
    to_char(full_date, 'YYYYMMDD')::int                as date_key,
    full_date                                          as full_date,
    extract(day from full_date)::int                   as day,
    extract(week from full_date)::int                  as week,
    extract(month from full_date)::int                 as month,
    extract(quarter from full_date)::int               as quarter,
    extract(year from full_date)::int                  as year,
    extract(dow from full_date)::int                   as day_of_week,
    extract(dow from full_date) in (0, 6)              as is_weekend
from spine