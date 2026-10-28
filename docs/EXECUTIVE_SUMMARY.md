# Executive summary: Olist marketplace, Jan 2017 – Aug 2018

*For a non-technical reader. One page. All figures from the tested warehouse in this repository.*

## The situation

Olist connects small Brazilian sellers to large online marketplaces. Over the 20 complete months in the data it
handled **97,910 orders worth R$15.7M** (GMV: item prices + freight). The business is growing fast and its
customers are mostly satisfied (average review 4.07 / 5), but growth depends almost entirely on new customers.

## Four findings

**1. Growth is strong and comes from volume.** January–August 2018 GMV was **2.4× the same months of 2017**
(+140%). The average order stayed at about R$160, so growth came from more orders, not bigger baskets.
Black Friday 2017 brought 1,166 orders in one day, six times a normal November day.

**2. Late deliveries are the main cause of unhappy customers.** 6.8% of deliveries arrive after the date promised
at checkout. **63% of late orders get a 1–2 star review, against 9.5% of on-time orders.** Each extra day makes it
worse (1–3 days late: 32% bad reviews; 8–14 days: 80%), while arriving early barely helps. The effect holds after
accounting for where the customer lives, what they bought and how they paid. Late orders are 7% of deliveries but
**a third of all bad reviews**.

**3. Customers in the North and Northeast are not harder to please; their parcels are later.** Northeast orders
take 20 days on average (vs 11 in the Southeast) and are late twice as often (12.7% vs 6.1%). Once lateness is
accounted for, region makes no difference to ratings. Sellers are concentrated around São Paulo, so distance
drives both delivery time and freight cost (18.5% of the price in the North vs 13% in the Southeast).

**4. Almost nobody comes back.** Only **3% of customers** place a second order, and in any month after their first
purchase fewer than 1% do. The business is buying growth with new customers each month.

Also notable: orders containing items from **two or more sellers get bad reviews four times as often** (48% vs
13%) even though they are rarely late, probably because parcels arrive separately and the customer reviews before
the order is complete. And **39 busy sellers average below 3.5 stars**; they deliver late twice as often as other
sellers but make only 4.6% of sales.

## Recommendations

| # | Action | Why | How to measure |
|---|---|---|---|
| 1 | **Promise delivery dates the network can keep**, especially for the North/Northeast; test a slightly more conservative estimate on a random half of orders | lateness relative to the promise, not speed itself, drives ratings | experiment: bad-review rate and conversion, treatment vs control |
| 2 | **Send the review request after the last parcel** of multi-seller orders | removes a likely cause of 4× bad-review rate | bad-review rate on multi-seller orders before/after |
| 3 | **Seller quality programme** for the 39 low-rated busy sellers (shipping SLAs, warnings, delisting) | small revenue at risk (4.6%), large share of bad experiences | their late rate and rating over 3 months |
| 4 | **Make retention a goal**: post-delivery offers, especially after an on-time first order | 97% one-time buyers; each 1-point lift in repeat rate ≈ 950 more returning customers | cohort month-1 to month-3 retention |

## Caveats

Data ends in 2018. It is observational: recommendation 1 should be confirmed by the experiment described. GMV is
not Olist's revenue (it earns a commission), and the data has no costs, so these findings say nothing about
profitability. The public sample only includes orders with a review.
