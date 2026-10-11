select
    row_number() over (order by b.name)::int as location_key,
    b.branch_id,
    b.business_id,
    b.name as branch_name,
    b.location,
    bu.country
from {{ ref('stg_branches') }} b
left join {{ ref('stg_businesses') }} bu on bu.business_id = b.business_id