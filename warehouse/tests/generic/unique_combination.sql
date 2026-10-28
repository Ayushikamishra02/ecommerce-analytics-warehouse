{% test unique_combination(model, columns) %}
-- fails for every combination of the columns that appears more than once (a composite primary key check)
select {{ columns | join(', ') }}, count(*) as n
from {{ model }}
group by {{ columns | join(', ') }}
having count(*) > 1
{% endtest %}
