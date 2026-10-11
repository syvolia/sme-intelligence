select
    row_number() over (order by s.name)::int as supplier_key,
    s.supplier_id,
    s.business_id,
    s.name,
    s.country,
    s.contact
from {{ ref('stg_suppliers') }} s