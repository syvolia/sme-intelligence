with stock as (
    select
        branch_id,
        product_id,
        sum(case
                when movement_type = 'in'  then quantity
                when movement_type = 'out' then -quantity
                else quantity
            end)::int as current_stock
    from {{ ref('stg_inventory') }}
    group by 1, 2
),
last_day as (
    select max(sale_date)::date as d from {{ ref('stg_sales') }}
),
demand as (
    select
        s.branch_id,
        si.product_id,
        sum(si.quantity)::int                    as units_30d,
        (sum(si.quantity)::float / 30.0)         as daily_demand
    from {{ ref('stg_sale_items') }} si
    join {{ ref('stg_sales') }} s on s.sale_id = si.sale_id
    where s.status <> 'cancelled'
      and s.sale_date >= (select d - interval '30 days' from last_day)
    group by 1, 2
),
last_snapshot as (
    select max(sale_date) as snapshot_date from {{ ref('stg_sales') }}
)
select
    (select to_char(snapshot_date, 'YYYYMMDD')::int from last_snapshot)     as date_key,
    p.product_key                                                            as product_key,
    l.location_key                                                           as location_key,
    coalesce(st.current_stock, 0)::int                                       as current_stock,
    coalesce(d.units_30d, 0)::int                                            as units_last_30d,
    coalesce(d.daily_demand, 0)::numeric(10,2)                               as daily_demand,
    case
        when coalesce(d.daily_demand, 0) > 0
            then (coalesce(st.current_stock, 0)::float / d.daily_demand)::numeric(10,1)
        else null
    end                                                                      as days_remaining,
    p.reorder_point                                                          as reorder_point,
    p.lead_time_days                                                         as lead_time_days,
    (coalesce(d.daily_demand, 0) * p.lead_time_days)::numeric(10,1)          as lead_time_demand,
    p.cost_price                                                             as cost_price,
    p.supplier_name                                                          as supplier_name,
    (coalesce(st.current_stock, 0) * p.cost_price)::numeric(14,2)            as inventory_value,
    case
        when coalesce(st.current_stock, 0) <= 0 then 'CRITICAL'
        when coalesce(d.daily_demand, 0) > 0
             and coalesce(st.current_stock, 0) <= (d.daily_demand * p.lead_time_days)
            then 'CRITICAL'
        when coalesce(st.current_stock, 0) <= p.reorder_point then 'LOW'
        else 'HEALTHY'
    end                                                                      as risk
from {{ ref('dim_product') }} p
cross join {{ ref('dim_location') }} l
left join stock st
    on st.branch_id = l.branch_id and st.product_id = p.product_id
left join demand d
    on d.branch_id = l.branch_id and d.product_id = p.product_id