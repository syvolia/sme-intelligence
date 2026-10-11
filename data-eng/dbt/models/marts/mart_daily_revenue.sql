select
    d.full_date                                                       as date,
    l.branch_id                                                       as branch_id,
    l.branch_name                                                     as branch_name,
    count(distinct f.sale_id)::int                                    as orders,
    sum(f.revenue)::numeric(14,2)                                     as revenue,
    sum(f.gross_profit)::numeric(14,2)                                as gross_profit,
    (sum(f.revenue) / nullif(count(distinct f.sale_id), 0))::numeric(14,2) as aov
from {{ ref('fact_sales') }} f
join {{ ref('dim_date') }} d on d.date_key = f.date_key
join {{ ref('dim_location') }} l on l.location_key = f.location_key
where f.status <> 'cancelled'
group by 1, 2, 3