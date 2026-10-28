# Learning path

These lessons explain the project from zero, in the order you would build it. Each one points at the real files,
so read a lesson, open the file it mentions, run the command, and look at the output.

| # | Lesson | You will be able to... | Time |
|---|---|---|---|
| 01 | [Star schema](01_star_schema.md) | explain facts, dimensions and grain, and why analysts model data this way | 30 min |
| 02 | [dbt and the warehouse layers](02_dbt_warehouse.md) | read and change a dbt project: sources, staging, marts, tests, lineage | 45 min |
| 03 | [Metrics and KPI definitions](03_metrics_and_kpis.md) | define GMV, AOV, retention, late rate precisely, and spot the traps | 30 min |
| 04 | [Analysis and statistics](04_analysis_and_statistics.md) | go from "late orders get worse reviews" to an estimate with a confidence interval and controls | 45 min |
| 05 | [Power BI and DAX](05_power_bi.md) | build the dashboard and explain filter context and CALCULATE | 60 min |
| 06 | [SQL interview practice](06_sql_interview_practice.md) | solve 22 interview-style questions (window functions, cohorts, dedup, anti-joins) | 2-3 h |
| 07 | [Interview questions about this project](07_interview_questions.md) | answer "walk me through your project" and the follow-ups | 30 min |

Glossary for the e-commerce words used everywhere:

| Term | Meaning here |
|---|---|
| **Marketplace** | Olist connects many small sellers to customers; it does not own the stock |
| **GMV** | Gross Merchandise Value: item prices + freight of valid orders (not revenue to Olist, which earns a commission) |
| **AOV** | Average Order Value = GMV / valid orders |
| **Valid order** | any status except `canceled` and `unavailable` |
| **Cohort** | all customers whose first order was in the same month |
| **Boleto** | a Brazilian payment slip paid at a bank or online, popular with people without credit cards |
| **Installments** | Brazilian credit cards commonly split one purchase into monthly payments (`parcelas`) |
| **BRL / R$** | Brazilian real |
