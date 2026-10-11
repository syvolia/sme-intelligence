{{ config(materialized='view') }}

select
    id::text                       as po_id,
    business_id::text              as business_id,
    supplier_id::text              as supplier_id,
    product_id::text               as product_id,
    quantity::int                  as quantity,
    unit_cost::numeric(14,2)       as unit_cost,
    order_date                     as order_date,
    expected_date                  as expected_date,
    received_date                  as received_date,
    status                         as status
from {{ var('source_schema', 'public') }}.purchase_orders