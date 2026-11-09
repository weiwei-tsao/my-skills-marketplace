---
name: award-vs-cash-check
description: Use when the user is about to redeem points or miles for a flight, asks whether an award ticket is worth it versus paying cash, or asks whether a fee-bearing points-earning channel (e.g. prepaid-card reloads at a grocery store) is still worth running — "值不值得用积分换", "换国泰划算吗", "现金票还是里程票", "充值还值得做吗", "award vs cash". Prices the same-date cash fare and the award cost (miles + taxes/surcharges), and computes the cost per point of the earning channel.
---

# Award vs Cash Check

## Overview

Two different questions. Do not merge them.

| Question | Compare | Command |
|---|---|---|
| **A. Redeem this ticket?** Points are already in hand. | Value per source point vs. the points' **best alternative use**: the cash-out floor and the keep-for-later target. The acquisition cost is sunk, so it does not decide this. | `calc.py redeem` |
| **B. Keep running the earning channel?** | The channel's **acquisition cost per point** vs. what the user's redemptions actually get. | `calc.py cost` |

Value per source point = **(cash fare − what the cash ticket would earn − award surcharges) ÷ source points**. Carrier surcharges (e.g. Cathay on Asia Miles) can eat most of the value. Price both sides for the **same itinerary and date** before transferring, because transfers can't be undone.

## Question A — redeem or pay cash

### Inputs (ask only for what's missing)

| Input | Default / note |
|---|---|
| Route incl. connections, dates, cabin, passengers | required |
| Award program + miles required | read from the booking page or ask the user |
| Award taxes + carrier surcharges | read from the booking page or ask the user; convert to CAD |
| Source currency + transfer ratio + bonus | e.g. RBC Avion → Asia Miles 1:1, +15% when a promo is live |
| Points the cash ticket would earn (`--earn`, CAD) | e.g. 3x air on a travel card; value them at the user's own rate |
| Cash-out value per point (`--cashout`) | default 0.58¢ (Avion statement credit); set per currency |
| Keep-for-later bar (`--target`) | default 1.0¢ |
| Acquisition cost (`--acq`, optional) | only for reporting profit; get it from `calc.py cost` |

If the user already has the numbers, skip browsing and go straight to the calculator.

### Workflow

1. **Cash fare.** Same flights, same date, same cabin. Use the **browser-use** skill, the repo default; plain fetch is often blocked. Check the airline's own site first, then Google Flights or one OTA. Take the lower bookable fare for the identical routing, not a cheaper different routing. Record URL, timestamp, currency and fare brand.
2. **Award cost.** Miles + taxes/surcharges from the award program's booking page. Use a logged-in session if needed, and stop and ask at login walls. Record the same fields.
3. **Convert to CAD** at the card's real rate: a no-FX card is about the network rate; otherwise add ~2.5%. State the rate used.
4. **Run** `python3 calc.py redeem --cash <CAD> --surcharges <CAD> --miles <n> [--ratio r --bonus b --earn CAD --acq cents]`. The script is in this skill folder; `--demo` runs the self-check.

### Output

1. **Verdict** in one line:
   - `REDEEM` when value ≥ target.
   - `BORDERLINE` when value is between cash-out and target.
   - `PAY CASH, keep points` when value < cash-out.
2. **Value per source point**, plus the two thresholds the script prints: **breakeven cash fare** and **target cash fare** ("redeem only if cash is above $X"). If `--acq` was given, also report the profit vs. acquisition cost, labelled as informational.
3. **Inputs table**: item | value | source URL | checked at.
4. **Caveats** that apply:
   - FX assumption.
   - A cash fare earns card points/miles and elite credit; an award usually doesn't.
   - Fare class and flexibility differ (award change fees vs. basic economy).
   - Quoted surcharges can change before ticketing.
   - The transfer bonus has a deadline.

## Question B — is the earning channel worth it

Run `python3 calc.py cost` with the channel's terms:

```
cost_per_reload   = reload_fee + withdraw_fee × reload_amt ÷ withdraw_amt + monthly_fee ÷ reloads_per_month
points_per_reload = (reload_amt + reload_fee) × earn_rate      # the fee is charged on the card too
acq_cents         = cost_per_reload ÷ points_per_reload × 100
```

Defaults are the user's Ontario reload channel, confirmed 2026-11:
- reload: $7.85 flat fee+tax per reload, with a store cap of $500 per reload;
- withdrawal: $1.95 flat per withdrawal of $1,000;
- account: $1 per month;
- about 7 reloads a month, earning 3x at the grocery store.

That gives **≈0.589¢ per point**.

Report the following:
- **The cost per point**, and whether it is above the cash-out value. If it is, cashing out loses money, so these points are only worth spending on high-value redemptions.
- **The sensitivity.** Fewer reloads per month spreads the monthly fee over fewer points. Withdrawing every $500 instead of every $1,000 doubles the withdrawal fee per reload; at the defaults that raises the cost to ≈0.653¢.
- **The real margin.** Compare the cost with the value per point from the user's actual recent redemptions, taken from Question A runs, not an aspirational valuation.

## Follow-ups (suggest, don't assume)

- Other transfer partners may price the same flights with lower surcharges. Check live on that partner's site; don't rely on remembered partner rules.
- If the verdict is PAY CASH, point out that the points stay banked for a higher-fare date: peak holidays, last-minute travel, premium cabin.

## Common mistakes

- Letting the acquisition cost decide a redemption. Once points are in hand, the cost is sunk; compare only with what else the points could do.
- Comparing against a cash fare for a different routing or date.
- Forgetting surcharges, or forgetting to divide miles by (1 + bonus) to get source points.
- Ignoring what the cash ticket would earn.
- Mixing per-person and all-passenger numbers. One card charge for award taxes often covers several passengers, while the statement line shows only the lead passenger. Confirm the passenger count before splitting the charge. Keep cash fare, surcharges and miles on the same basis: either all per person, or all for every passenger.
- Treating a flat withdrawal fee as a percentage. It only reaches its lowest rate when each withdrawal is the maximum amount.
