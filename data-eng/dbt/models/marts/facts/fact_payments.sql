select
    row_number() over (order by p.payment_id)::bigint   as payment_key,
    d.date_key                                          as date_key,
    l.location_key                                      as location_key,
    c.customer_key                                      as customer_key,
    sup.supplier_key                                    as supplier_key,
    p.payment_id                                        as payment_id,
    p.direction                                         as direction,
    p.amount                                            as amount,
    p.currency                                          as currency,
    p.method                                            as method,
    p.payment_date                                      as payment_date
from {{ ref('stg_payments') }} p
left join {{ ref('stg_sales') }} s on s.sale_id = p.sale_id
left join {{ ref('stg_purchase_orders') }} po on po.po_id = p.purchase_order_id
left join {{ ref('dim_date') }} d on d.full_date = p.payment_date::date
left join {{ ref('dim_location') }} l on l.branch_id = s.branch_id
left join {{ ref('dim_customer') }} c on c.customer_id = s.customer_id
left join {{ ref('dim_supplier') }} sup on sup.supplier_id = po.supplier_id