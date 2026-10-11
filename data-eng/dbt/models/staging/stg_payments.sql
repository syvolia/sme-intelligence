{{ config(materialized='view') }}

select
    id::text                    as payment_id,
    business_id::text           as business_id,
    sale_id::text               as sale_id,
    purchase_order_id::text     as purchase_order_id,
    direction                   as direction,
    amount::numeric(14,2)       as amount,
    currency                    as currency,
    payment_date                as payment_date,
    method                      as method
from {{ var('source_schema', 'public') }}.payments