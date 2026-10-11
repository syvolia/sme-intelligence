{{ config(materialized='view') }}

select
    id::text                                          as sale_id,
    business_id::text                                 as business_id,
    branch_id::text                                   as branch_id,
    customer_id::text                                 as customer_id,
    sale_date                                         as sale_date,
    currency                                          as currency,
    total_amount::numeric(14,2)                       as total_amount,
    discount::numeric(14,2)                           as discount,
    status                                            as status,
    created_at                                        as created_at
from {{ var('source_schema', 'public') }}.sales