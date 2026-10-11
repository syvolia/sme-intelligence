with sales_agg as (
    select
        customer_id,
        min(sale_date)::date as first_seen,
        max(sale_date)::date as last_seen
    from {{ ref('stg_sales') }}
    where customer_id is not null
    group by 1
)
select
    row_number() over (order by c.customer_id)::int as customer_key,
    c.customer_id,
    c.business_id,
    c.name,
    c.phone,
    c.email,
    c.segment,
    a.first_seen,
    a.last_seen
from {{ ref('stg_customers') }} c
left join sales_agg a on a.customer_id = c.customer_id