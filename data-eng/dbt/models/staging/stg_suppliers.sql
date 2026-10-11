{{ config(materialized='view') }}

select
    id::text         as supplier_id,
    business_id::text as business_id,
    name             as name,
    contact          as contact,
    country          as country
from {{ var('source_schema', 'public') }}.suppliers