from typing_extensions import TypedDict


class DebtItem(TypedDict):
    name: str
    balance: float
    interest_rate: float
    emi: float


async def plan_debt_payoff(debts: list[DebtItem], extra_monthly: float = 0.0) -> str:
    """
    Advise the user on the best strategy to pay off multiple debts. Compares
    avalanche (highest interest first) and snowball (smallest balance first)
    methods and shows total interest saved.

    Args:
        debts: List of debts, each with name, balance (INR), interest_rate (annual %), and emi (monthly payment INR)
        extra_monthly: Extra amount available per month to accelerate payoff (default 0)
    """
    if not debts:
        return "No debts provided. You're debt-free — invest that EMI amount instead!"

    total_balance = sum(d["balance"] for d in debts)
    total_emi = sum(d["emi"] for d in debts)
    weighted_rate = sum(d["balance"] * d["interest_rate"] for d in debts) / total_balance if total_balance > 0 else 0

    report = f"── DEBT OVERVIEW ──\n"
    report += f"Total Outstanding: ₹{total_balance:,.0f}\n"
    report += f"Total Monthly EMI: ₹{total_emi:,.0f}\n"
    report += f"Weighted Average Interest: {weighted_rate:.1f}%\n"
    if extra_monthly > 0:
        report += f"Extra Monthly Budget for Payoff: ₹{extra_monthly:,.0f}\n"
    report += f"\nYour Debts:\n"

    for d in sorted(debts, key=lambda x: x["interest_rate"], reverse=True):
        report += f"  • {d['name']}: ₹{d['balance']:,.0f} @ {d['interest_rate']}% (EMI: ₹{d['emi']:,.0f})\n"

    # Avalanche strategy (highest interest first)
    avalanche_order = sorted(debts, key=lambda x: x["interest_rate"], reverse=True)
    # Snowball strategy (smallest balance first)
    snowball_order = sorted(debts, key=lambda x: x["balance"])

    def simulate_payoff(order: list[DebtItem], extra: float) -> tuple[int, float]:
        """Simulate payoff and return (months, total_interest_paid)."""
        balances = {d["name"]: d["balance"] for d in order}
        rates = {d["name"]: d["interest_rate"] / 100 / 12 for d in order}
        emis = {d["name"]: d["emi"] for d in order}
        total_interest = 0.0
        months = 0
        max_months = 600  # 50 year cap

        while any(b > 0 for b in balances.values()) and months < max_months:
            months += 1
            extra_left = extra

            for d in order:
                name = d["name"]
                if balances[name] <= 0:
                    continue

                interest = balances[name] * rates[name]
                total_interest += interest
                balances[name] += interest

                payment = emis[name]
                # Apply extra to the priority debt
                if extra_left > 0 and name == next(
                    (x["name"] for x in order if balances[x["name"]] > 0), None
                ):
                    payment += extra_left
                    extra_left = 0

                balances[name] = max(0, balances[name] - payment)

        return months, total_interest

    avalanche_months, avalanche_interest = simulate_payoff(avalanche_order, extra_monthly)
    snowball_months, snowball_interest = simulate_payoff(snowball_order, extra_monthly)

    # No-extra baseline
    baseline_months, baseline_interest = simulate_payoff(avalanche_order, 0)

    report += f"\n── PAYOFF STRATEGIES ──\n"
    report += f"\n  Avalanche (highest interest first) — RECOMMENDED:\n"
    report += f"    Target order: {' → '.join(d['name'] for d in avalanche_order)}\n"
    report += f"    Debt-free in: {avalanche_months} months ({avalanche_months // 12}y {avalanche_months % 12}m)\n"
    report += f"    Total interest paid: ₹{avalanche_interest:,.0f}\n"

    report += f"\n  Snowball (smallest balance first) — for motivation:\n"
    report += f"    Target order: {' → '.join(d['name'] for d in snowball_order)}\n"
    report += f"    Debt-free in: {snowball_months} months ({snowball_months // 12}y {snowball_months % 12}m)\n"
    report += f"    Total interest paid: ₹{snowball_interest:,.0f}\n"

    if avalanche_interest < snowball_interest:
        saved = snowball_interest - avalanche_interest
        report += f"\n  Avalanche saves you ₹{saved:,.0f} in interest!\n"

    if extra_monthly > 0:
        saved_vs_normal = baseline_interest - avalanche_interest
        months_saved = baseline_months - avalanche_months
        report += f"\n── IMPACT OF EXTRA ₹{extra_monthly:,.0f}/MONTH ──\n"
        report += f"  Months saved: {months_saved}\n"
        report += f"  Interest saved: ₹{saved_vs_normal:,.0f}\n"
    else:
        # Suggest what extra payment could do
        suggested_extra = total_emi * 0.2  # 20% of current EMI as extra
        _, interest_with_extra = simulate_payoff(avalanche_order, suggested_extra)
        potential_savings = baseline_interest - interest_with_extra
        report += f"\n── TIP ──\n"
        report += f"  If you can add just ₹{suggested_extra:,.0f}/month extra toward debt,\n"
        report += f"  you'd save ~₹{potential_savings:,.0f} in interest.\n"

    report += f"\n── ADVISOR NOTE ──\n"
    high_interest = [d for d in debts if d["interest_rate"] > 14]
    if high_interest:
        report += f"  High-interest debts ({', '.join(d['name'] for d in high_interest)}) are costing you.\n"
        report += f"  Priority: Pay these off BEFORE increasing investments.\n"
        report += f"  Once cleared, redirect that EMI (₹{sum(d['emi'] for d in high_interest):,.0f}) into SIPs."
    else:
        report += f"  Your interest rates are reasonable. Balance debt payoff with investing —\n"
        report += f"  don't pause investments entirely while paying off low-interest debt."

    return report

