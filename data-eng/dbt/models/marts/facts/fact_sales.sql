select
    row_number() over (order by si.item_id)::bigint    as sale_key,
    d.date_key                                         as date_key,
    p.product_key                                      as product_key,
    c.customer_key                                     as customer_key,
    l.location_key                                     as location_key,
    si.sale_id                                         as sale_id,
    si.quantity                                        as quantity,
    si.unit_price                                      as unit_price,
    si.unit_cost                                       as unit_cost,
    (si.quantity * si.unit_price)::numeric(14,2)       as revenue,
    (si.quantity * (si.unit_price - si.unit_cost))::numeric(14,2) as gross_profit,
    s.discount                                         as discount,
    s.status                                           as status,
    s.sale_date                                        as sale_date,
    s.currency                                         as currency
from {{ ref('stg_sale_items') }} si
join {{ ref('stg_sales') }} s on s.sale_id = si.sale_id
left join {{ ref('dim_product') }} p on p.product_id = si.product_id
left join {{ ref('dim_customer') }} c on c.customer_id = s.customer_id
left join {{ ref('dim_location') }} l on l.branch_id = s.branch_id
left join {{ ref('dim_date') }} d on d.full_date = s.sale_date::date