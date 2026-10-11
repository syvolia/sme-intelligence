{{ config(materialized='view') }}

select
    id::text                as movement_id,
    business_id::text       as business_id,
    branch_id::text         as branch_id,
    product_id::text        as product_id,
    movement_type           as movement_type,
    quantity::int           as quantity,
    movement_date           as movement_date,
    reference               as reference
from {{ var('source_schema', 'public') }}.inventory_movements