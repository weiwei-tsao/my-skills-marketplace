#!/usr/bin/env python3
"""Award vs cash — two separate questions, all money in CAD, values in cents per SOURCE point.

cost   : what does one source point cost to earn via a fee-bearing reload channel?
         cost_per_reload = reload_fee + withdraw_fee * reload_amt / withdraw_amt + monthly_fee / reloads_per_month
         points_per_reload = (reload_amt + reload_fee) * earn_rate        # the fee is charged on the card too
         -> used to judge "is the reload channel still worth running?", NOT to judge a redemption.

redeem : is THIS ticket worth points, given points already in hand (acquisition cost is sunk)?
         value = (cash_fare - cash_ticket_earn - award_surcharges) / source_points
         source_points = miles / (1 + transfer_bonus) / transfer_ratio
         compare value with the points' best alternative use: cash-out floor and the keep-for-later target.
"""
import argparse


def acq_cost(reload_fee=7.85, reload_amt=500.0, withdraw_fee=1.95, withdraw_amt=1000.0,
             monthly_fee=1.0, reloads_per_month=7.0, earn_rate=3.0):
    cost = reload_fee + withdraw_fee * reload_amt / withdraw_amt + monthly_fee / reloads_per_month
    pts = (reload_amt + reload_fee) * earn_rate
    return dict(cost_per_reload_cad=round(cost, 3), points_per_reload=round(pts, 2),
                cost_rate_pct=round(cost / reload_amt * 100, 3),
                acq_cents=round(cost / pts * 100, 4))


def evaluate(cash, surcharges, miles, ratio=1.0, bonus=0.0, earn=0.0,
             cashout=0.58, target=1.0, acq=None):
    pts = miles / (1 + bonus) / ratio
    value = (cash - earn - surcharges) / pts * 100
    verdict = ("REDEEM" if value >= target else
               "BORDERLINE — redeem only if no better use is coming" if value >= cashout else
               "PAY CASH, keep points")
    out = dict(source_points=round(pts), value_cents=round(value, 3),
               cashout_floor_cents=cashout, target_cents=target, verdict=verdict,
               breakeven_cash_fare=round(surcharges + earn + pts * cashout / 100, 2),
               target_cash_fare=round(surcharges + earn + pts * target / 100, 2))
    if acq is not None:  # informational only: profit on the points' original cost
        out["profit_vs_acq_cad"] = round((value - acq) * pts / 100, 2)
    return out


def demo():
    # acquisition: Ontario reload $7.85 per $500, withdraw $1.95 per $1,000, $1/month, 3x card
    c = acq_cost()
    assert abs(c["acq_cents"] - 0.5886) < 0.0005, c
    assert abs(acq_cost(reloads_per_month=1)["acq_cents"] - 0.6449) < 0.0005
    assert abs(acq_cost(withdraw_amt=500)["acq_cents"] - 0.6526) < 0.0005  # withdrawing every $500
    # redemption, per person YYZ<->HGH via HKG round trip (Cathay, 2026-10): 76,000 Asia Miles,
    # Avion->Asia Miles 1:1 +15%, taxes+surcharges ~CAD 720 (a 3-passenger charge split per person)
    a = evaluate(1500, 720, 76000, bonus=0.15, acq=c["acq_cents"])
    assert a["source_points"] == 66087 and abs(a["value_cents"] - 1.180) < 0.01, a
    assert a["verdict"] == "REDEEM" and a["profit_vs_acq_cad"] > 0, a
    b = evaluate(1200, 720, 76000, bonus=0.15)
    assert abs(b["value_cents"] - 0.726) < 0.01 and b["verdict"].startswith("BORDERLINE"), b
    d = evaluate(1000, 720, 76000, bonus=0.15)
    assert abs(d["value_cents"] - 0.424) < 0.01 and d["verdict"] == "PAY CASH, keep points", d
    assert abs(d["breakeven_cash_fare"] - 1103.3) < 1, d
    print("self-check ok")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--demo", action="store_true", help="run the self-check")
    sub = p.add_subparsers(dest="cmd")

    pc = sub.add_parser("cost", help="cost per source point of a fee-bearing reload channel")
    pc.add_argument("--reload-fee", type=float, default=7.85, help="fee+tax per reload, CAD (flat)")
    pc.add_argument("--reload-amt", type=float, default=500.0, help="amount per reload (store cap), CAD")
    pc.add_argument("--withdraw-fee", type=float, default=1.95, help="flat fee per withdrawal, CAD")
    pc.add_argument("--withdraw-amt", type=float, default=1000.0, help="amount taken out per withdrawal, CAD")
    pc.add_argument("--monthly-fee", type=float, default=1.0, help="account fee per month, CAD")
    pc.add_argument("--reloads-per-month", type=float, default=7.0)
    pc.add_argument("--earn-rate", type=float, default=3.0, help="card points per $ at the reload store")

    pr = sub.add_parser("redeem", help="is this award worth the points already in hand?")
    pr.add_argument("--cash", type=float, required=True, help="same-itinerary cash fare, CAD")
    pr.add_argument("--surcharges", type=float, required=True, help="award taxes + carrier surcharges, CAD")
    pr.add_argument("--miles", type=float, required=True, help="award miles required")
    pr.add_argument("--ratio", type=float, default=1.0, help="program miles per source point before bonus")
    pr.add_argument("--bonus", type=float, default=0.0, help="transfer bonus, e.g. 0.15")
    pr.add_argument("--earn", type=float, default=0.0, help="CAD value of points the CASH ticket would earn")
    pr.add_argument("--cashout", type=float, default=0.58, help="cash-out value of one source point, cents")
    pr.add_argument("--target", type=float, default=1.0, help="'keep for a better redemption' bar, cents")
    pr.add_argument("--acq", type=float, help="optional: acquisition cost, cents (report profit only)")

    a = p.parse_args()
    if a.demo or a.cmd is None:
        demo()
    else:
        res = (acq_cost(a.reload_fee, a.reload_amt, a.withdraw_fee, a.withdraw_amt, a.monthly_fee,
                        a.reloads_per_month, a.earn_rate) if a.cmd == "cost" else
               evaluate(a.cash, a.surcharges, a.miles, a.ratio, a.bonus, a.earn, a.cashout, a.target, a.acq))
        for k, v in res.items():
            print(f"{k}: {v}")
