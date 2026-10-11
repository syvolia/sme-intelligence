select
    row_number() over (order by p.sku)::int as product_key,
    p.product_id,
    p.sku,
    p.name,
    p.category,
    p.unit,
    p.cost_price,
    p.sell_price,
    p.reorder_point,
    p.lead_time_days,
    p.supplier_id,
    s.name as supplier_name
from {{ ref('stg_products') }} p
left join {{ ref('stg_suppliers') }} s on s.supplier_id = p.supplier_id