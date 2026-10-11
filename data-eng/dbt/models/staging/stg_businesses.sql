{{ config(materialized='view') }}

select
    id::text         as business_id,
    name             as name,
    country          as country,
    base_currency    as base_currency
from {{ var('source_schema', 'public') }}.businesses