select
    row_number() over (order by po.po_id)::bigint       as po_key,
    d_order.date_key                                    as order_date_key,
    d_recv.date_key                                     as received_date_key,
    p.product_key                                       as product_key,
    s.supplier_key                                      as supplier_key,
    po.po_id                                            as po_id,
    po.quantity                                         as quantity,
    po.unit_cost                                        as unit_cost,
    (po.quantity * po.unit_cost)::numeric(14,2)         as total_cost,
    po.order_date                                       as order_date,
    po.expected_date                                    as expected_date,
    po.received_date                                    as received_date,
    case
        when po.received_date is null then null
        else (extract(epoch from (po.received_date - po.order_date)) / 86400.0)::numeric(10,2)
    end                                                 as lead_time_days,
    case
        when po.received_date is null then null
        else po.received_date <= po.expected_date
    end                                                 as on_time_flag,
    po.status                                           as status
from {{ ref('stg_purchase_orders') }} po
left join {{ ref('dim_product') }} p on p.product_id = po.product_id
left join {{ ref('dim_supplier') }} s on s.supplier_id = po.supplier_id
left join {{ ref('dim_date') }} d_order on d_order.full_date = po.order_date::date
left join {{ ref('dim_date') }} d_recv on d_recv.full_date = po.received_date::date