{{ config(materialized='view') }}

select
    id::text         as branch_id,
    business_id::text as business_id,
    name             as name,
    location         as location
from {{ var('source_schema', 'public') }}.branches