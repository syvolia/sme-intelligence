{{ config(materialized='view') }}

select
    id::text                       as product_id,
    business_id::text              as business_id,
    sku                            as sku,
    name                           as name,
    category                       as category,
    unit                           as unit,
    cost_price::numeric(14,2)      as cost_price,
    sell_price::numeric(14,2)      as sell_price,
    reorder_point::int             as reorder_point,
    lead_time_days::int            as lead_time_days,
    supplier_id::text              as supplier_id
from {{ var('source_schema', 'public') }}.products