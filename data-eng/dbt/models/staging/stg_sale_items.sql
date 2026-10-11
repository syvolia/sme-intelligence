{{ config(materialized='view') }}

select
    id::text                       as item_id,
    sale_id::text                  as sale_id,
    product_id::text               as product_id,
    quantity::int                  as quantity,
    unit_price::numeric(14,2)      as unit_price,
    unit_cost::numeric(14,2)       as unit_cost
from {{ var('source_schema', 'public') }}.sale_items