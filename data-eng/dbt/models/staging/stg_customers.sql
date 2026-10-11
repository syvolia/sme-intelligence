{{ config(materialized='view') }}

select
    id::text         as customer_id,
    business_id::text as business_id,
    name             as name,
    phone            as phone,
    email            as email,
    segment          as segment,
    created_at       as created_at
from {{ var('source_schema', 'public') }}.customers