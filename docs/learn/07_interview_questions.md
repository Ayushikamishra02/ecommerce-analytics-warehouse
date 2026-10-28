# 07 · Interview questions about this project

Practise answering out loud. Aim for 30–60 seconds per answer: the point, the evidence, the trade-off.

## The walkthrough

**"Walk me through this project."**

> I built an analytics warehouse for a Brazilian e-commerce marketplace, Olist: about 100k orders across 9 raw
> tables. I loaded the raw files into DuckDB, then used dbt to clean them and model a star schema (two fact
> tables, four dimensions) plus analytics marts for KPIs, cohorts and RFM. 68 dbt tests check keys,
> relationships and that the marts reconcile to the facts. On top of that I answered business questions with
> statistics; the main one was that late delivery is the strongest driver of bad reviews: late orders get 1–2
> stars 63% of the time vs 9.5%, and that holds after controlling for region, basket and category. I exported the
> model to Power BI with documented DAX measures and also built a Streamlit dashboard. Everything rebuilds
> with one command and runs in CI.

**"What was the hardest part?"** Definitions, not code. For example `customer_id` turned out to be per order, so
the naive repeat rate was 0%; the real person id gave 3%. Reviews had duplicates per order. Deciding and
documenting each rule (and testing it) took longer than writing the SQL.

## Data modelling

**Why two fact tables?** Different grains. Reviews and delivery belong to an order; category and seller belong
to an item. One table would double-count freight or over-weight multi-item orders in review averages.

**Why DuckDB and not Postgres / Snowflake?** It's free, serverless and fast for analytics on a laptop, so anyone
can clone and run the project. dbt abstracts the database: switching to Snowflake or BigQuery means changing
`profiles.yml` and a few date functions.

**How would this run in production?** Raw data lands in cloud storage daily; an orchestrator (Airflow, Dagster,
dbt Cloud) runs `dbt build`; failures block the dashboard refresh; marts are materialised incrementally for the
big facts (`materialized='incremental'` with a `unique_key`) so each run processes only new orders.

**What is an incremental model and when would you use one here?** A model that inserts/merges only new or
changed rows instead of rebuilding. Worth it when the fact is large (hundreds of millions of rows); at 100k rows,
a full rebuild in seconds is simpler and safer.

**Slowly changing dimensions?** If a seller's state changes, Type 1 overwrites, Type 2 keeps history with
validity dates (dbt snapshots). The snapshot data has one version per entity, so Type 1 was enough; I'd add a
snapshot on sellers in production.

## Data quality

**What tests did you write and why?** Primary keys unique and not null; foreign keys exist in the dimension;
accepted values for status and review score; non-negative money; reconciliation tests (monthly KPIs sum to the
fact table to the cent; item fact sums to order fact). Reconciliations catch the bugs that matter most: numbers
that disagree between reports.

**Tell me about a test you set to warn instead of fail.** Payments differ from items + freight on 0.26% of
orders, explained by installment interest and vouchers. That's real behaviour, not a pipeline bug, so it warns
only if the share rises above 0.5%. Failing the build on known, explained noise trains people to ignore failures.

**How did you handle the geolocation table?** 1M rows, several per zip prefix, some outside Brazil. I kept
points inside Brazil's bounding box and took the median per zip: one point per zip, robust to outliers.

## Analysis and statistics

**How do you know lateness *causes* bad reviews?** I don't know it for certain; it's observational. The
evidence: a 53-point difference with a tight bootstrap CI, a dose-response gradient (each extra day of delay is
worse), robustness in a logistic regression with region, basket, payment and category (OR 18, CI 17–19), and
consistency across months (Spearman 0.59). The definitive test would be an experiment on promised dates.

**Explain an odds ratio of 18 to a non-technical manager.** I wouldn't use the odds ratio with them. I'd say:
"63 out of 100 late orders get a 1–2 star review; for on-time orders it's 9 or 10 out of 100." The odds ratio is
for showing that the effect survives controls.

**Something that surprised you?** Region looked important (the Northeast has worse reviews), but once lateness
was in the model, region's effect vanished (OR 1.02). The Northeast isn't harder to please; its parcels are later.
And multi-seller orders get bad reviews 4× as often despite rarely being late, probably because parcels arrive
separately and customers review before the order is complete.

**What would you recommend to the business?**
1. Make delivery promises accurate (slightly conservative) rather than optimistic: arriving early barely helps,
   arriving late costs a lot. Test it with an experiment.
2. Send the review survey after the *last* parcel of multi-seller orders.
3. Focus seller-quality work on the 39 busy sellers averaging under 3.5 stars (only 4.6% of GMV).
4. Retention is the growth gap: 97% of customers buy once. Start by fixing first-order experience (lateness).

**What are the limitations?** Data ends in 2018; one review per order and every order has one (the public sample
was selected that way); no costs or margins, so GMV not profit; delivery estimates are Olist's, so lateness is
relative to their promise, not an absolute speed.

## SQL / BI quick fire

- *Find the top category per state* → `row_number() over (partition by state order by revenue desc) = 1`
  (SQL Q08).
- *Deduplicate reviews* → `row_number()` partitioned by `order_id`, keep 1 (Q15).
- *Why did joining orders to items to payments inflate revenue?* Fan-out: each order row repeats once per item ×
  per payment. Aggregate each child to order level first (Q17).
- *How do you find days with zero sales?* A date spine and an anti-join; you can't group rows that don't exist
  (Q21).
- *Measure vs calculated column?* See lesson 05.

## Questions to ask them

- "How do your analysts and finance agree on metric definitions: a semantic layer, dbt metrics, a wiki?"
- "What does a data-quality incident look like here, and how is it caught?"
- "How much of the role is building models vs answering ad-hoc questions?"
