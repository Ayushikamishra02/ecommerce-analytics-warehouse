-- Level: hard
-- Question: Find the dates between 2017-01-01 and 2018-08-31 with ZERO orders (gaps in the data).
-- Concepts: date spine + anti-join; you cannot find missing rows by grouping the rows that exist
select d.date
from core.dim_date d
where d.date between '2017-01-01' and '2018-08-31'
  and not exists (select 1 from core.fct_orders o where o.purchase_date = d.date)
order by 1;
