-- Calendar table covering the whole dataset, for BI tools (Power BI needs a proper date dimension).
select
    d::date                                       as date,
    year(d)                                       as year,
    quarter(d)                                    as quarter,
    month(d)                                      as month,
    strftime(d, '%Y-%m')                          as year_month,
    strftime(d, '%b')                             as month_name,
    isodow(d)                                     as iso_weekday,
    strftime(d, '%a')                             as weekday_name,
    isodow(d) in (6, 7)                           as is_weekend,
    d::date in ('2016-11-25', '2017-11-24')       as is_black_friday,
    date_trunc('month', d)::date                  as month_start,
    date_trunc('month', d)::date between '{{ var("first_complete_month") }}' and '{{ var("last_complete_month") }}'
                                                  as in_complete_month
from range(date '2016-09-01', date '2018-11-01', interval 1 day) t(d)
