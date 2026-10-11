with last_day as (
    select max(sale_date)::date as d from {{ ref('stg_sales') }}
),
agg as (
    select
        c.customer_id,
        c.customer_key,
        c.name,
        coalesce(
            (select d from last_day) - max(s.sale_date)::date,
            999999
        )::int as recency_days,
        count(distinct s.sale_id)::int as frequency,
        coalesce(sum(si.quantity * si.unit_price), 0)::numeric(14,2) as monetary
    from {{ ref('dim_customer') }} c
    left join {{ ref('stg_sales') }} s
        on s.customer_id = c.customer_id and s.status <> 'cancelled'
    left join {{ ref('stg_sale_items') }} si on si.sale_id = s.sale_id
    group by 1, 2, 3
),
scored as (
    select
        customer_id,
        customer_key,
        name,
        recency_days,
        frequency,
        monetary,
        (6 - ntile(5) over (order by recency_days asc))::int as r_score,
        ntile(5) over (order by frequency asc)::int          as f_score,
        ntile(5) over (order by monetary asc)::int           as m_score
    from agg
)
select
    customer_id,
    customer_key,
    name,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    case
        when r_score >= 4 and f_score >= 4 and m_score >= 4 then 'High Value'
        when r_score >= 3 and f_score >= 3                   then 'Loyal'
        when r_score <= 2 and f_score >= 3                   then 'At Risk'
        when r_score >= 4 and f_score <= 2                   then 'New'
        else 'Inactive'
    end as segment
from scored