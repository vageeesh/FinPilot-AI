from typing_extensions import TypedDict


class MonthlyExpenses(TypedDict):
    rent: float
    loan_emi: float
    groceries: float
    utilities: float
    insurance: float
    entertainment: float
    transportation: float
    miscellaneous: float



async def allocate_monthly_finances(
    income: float, expenses: MonthlyExpenses, investment_percent: float = 15.0
) -> str:
    """
    Act as a personal finance advisor for the user. Analyzes monthly income
    and expenses using the 'invest first' approach, flags unhealthy spending
    patterns, and motivates the user to invest by showing growth projections.

    Args:
        income: Monthly net income in INR
        expenses: Monthly expenses breakdown (rent, loan_emi, groceries, utilities, insurance, entertainment, transportation, miscellaneous) in INR
        investment_percent: Percentage of income to invest first (default 15%)
    """
    # Healthy spending benchmarks (% of income)
    benchmarks = {
        "rent": 30.0,
        "loan_emi": 20.0,
        "groceries": 15.0,
        "utilities": 5.0,
        "insurance": 5.0,
        "entertainment": 10.0,
        "transportation": 10.0,
        "miscellaneous": 5.0,
    }

    investment_amount = income * (investment_percent / 100)
    spendable_income = income - investment_amount
    total_expenses = sum(expenses.values())
    surplus = spendable_income - total_expenses

    # --- Build report ---
    report = f"💰 Monthly Income: ₹{income:,.0f}\n"

    # Invest first section
    report += f"\n── INVEST FIRST ──\n"
    report += f"Your investment ({investment_percent:.0f}% of income): ₹{investment_amount:,.0f}/month\n"

    # Growth projection (12% annual return, compounded monthly)
    annual_rate = 0.12
    monthly_rate = annual_rate / 12
    years_5 = investment_amount * (((1 + monthly_rate) ** 60 - 1) / monthly_rate)
    years_10 = investment_amount * (((1 + monthly_rate) ** 120 - 1) / monthly_rate)
    report += f"  → In 5 years this grows to: ~₹{years_5:,.0f}\n"
    report += f"  → In 10 years this grows to: ~₹{years_10:,.0f}\n"
    report += f"Remaining for expenses: ₹{spendable_income:,.0f}\n"

    # Expenses with health check
    report += f"\n── WHERE YOUR MONEY GOES ──\n"
    warnings = []
    for category, amount in expenses.items():
        pct = (amount / income) * 100
        limit = benchmarks.get(category, 10.0)
        flag = " ⚠️ HIGH" if pct > limit else ""
        report += f"  {category.replace('_', ' ').capitalize()}: ₹{amount:,.0f} ({pct:.1f}% of income){flag}\n"
        if pct > limit:
            warnings.append(
                f"  • {category.replace('_', ' ').capitalize()} is {pct:.0f}% of income — try to keep it under {limit:.0f}%"
            )
    report += f"  ─────────────────\n"
    report += f"  Total: ₹{total_expenses:,.0f} ({(total_expenses / income * 100):.0f}% of income)\n"

    # Needs vs Wants breakdown (50-30-20 framework)
    needs = sum(expenses.get(k, 0) for k in ["rent", "loan_emi", "groceries", "utilities", "insurance"])
    wants = sum(expenses.get(k, 0) for k in ["entertainment", "transportation", "miscellaneous"])
    needs_pct = (needs / income) * 100
    wants_pct = (wants / income) * 100

    report += f"\n── 50-35-15 CHECK ──\n"
    report += f"  Needs (rent, EMI, groceries, utilities, insurance): {needs_pct:.0f}% of income"
    report += f" {'✅' if needs_pct <= 50 else ' ⚠️ over 50%'}\n"
    report += f"  Wants (entertainment, transport, misc): {wants_pct:.0f}% of income"
    report += f" {'✅' if wants_pct <= 35 else ' ⚠️ over 35%'}\n"
    report += f"  Invest/Save: {investment_percent:.0f}% of income"
    report += f" {'✅' if investment_percent >= 15 else ' (aim for 15%)'}\n"

    # Advisor observations
    if warnings:
        report += f"\n── ADVISOR NOTES ──\n"
        for w in warnings:
            report += f"{w}\n"

    # Summary
    report += f"\n── BOTTOM LINE ──\n"
    if surplus >= 0:
        report += f"After investing and all expenses, you have ₹{surplus:,.0f} spare.\n"
        emergency_target = total_expenses * 4
        report += f"Priority: Build an emergency fund of ₹{emergency_target:,.0f} (4 months of expenses) before adding more to investments.\n"
        if surplus < total_expenses * 0.1:
            report += f"Your margin is thin — avoid lifestyle inflation and protect this surplus."
    else:
        min_invest_pct = max(0, (income - total_expenses) / income * 100)
        report += (
            f"Shortfall: Your expenses exceed what's left after investing by ₹{-surplus:,.0f}.\n"
            f"To fix this:\n"
            f"  1. Cut discretionary spending (entertainment, miscellaneous) first\n"
            f"  2. If stuck, invest at least {min_invest_pct:.0f}% (₹{income - total_expenses:,.0f}) — even small amounts compound over time\n"
            f"  3. Never invest 0% — that's how people stay in the same place for decades"
        )

    return report


async def assess_financial_health(
    monthly_income: float,
    monthly_expenses: float,
    monthly_emi: float,
    existing_savings: float,
    total_debt: float,
    monthly_investment: float,
) -> str:
    """
    Give the user a financial health score (1-10) and actionable priority steps.
    Evaluates emergency fund coverage, debt-to-income ratio, savings rate,
    and investment habit to tell the user exactly what to fix first.

    Args:
        monthly_income: Monthly net income in INR
        monthly_expenses: Total monthly expenses in INR
        monthly_emi: Total monthly EMI payments in INR
        existing_savings: Total liquid savings (bank + FD + liquid funds) in INR
        total_debt: Total outstanding debt (all loans combined) in INR
        monthly_investment: Current monthly investment amount in INR
    """
    # Key ratios
    emergency_months = existing_savings / monthly_expenses if monthly_expenses > 0 else 0
    debt_to_income = (total_debt / (monthly_income * 12)) if monthly_income > 0 else 0
    emi_to_income = (monthly_emi / monthly_income * 100) if monthly_income > 0 else 0
    savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0
    investment_rate = (monthly_investment / monthly_income * 100) if monthly_income > 0 else 0

    # Scoring (each category out of 2.5, total 10)
    score = 0.0

    # Emergency fund score (0-2.5)
    if emergency_months >= 4:
        ef_score = 2.5
    elif emergency_months >= 2:
        ef_score = 1.5
    elif emergency_months >= 1:
        ef_score = 0.75
    else:
        ef_score = 0.0
    score += ef_score

    # Debt score (0-2.5) — lower debt-to-income is better
    if debt_to_income == 0:
        debt_score = 2.5
    elif debt_to_income < 0.5:
        debt_score = 2.0
    elif debt_to_income < 1.0:
        debt_score = 1.0
    else:
        debt_score = 0.0
    score += debt_score

    # Savings rate score (0-2.5)
    if savings_rate >= 30:
        sr_score = 2.5
    elif savings_rate >= 20:
        sr_score = 2.0
    elif savings_rate >= 10:
        sr_score = 1.0
    else:
        sr_score = 0.0
    score += sr_score

    # Investment score (0-2.5)
    if investment_rate >= 20:
        inv_score = 2.5
    elif investment_rate >= 15:
        inv_score = 2.0
    elif investment_rate >= 5:
        inv_score = 1.0
    else:
        inv_score = 0.0
    score += inv_score

    # Build report
    report = f"── FINANCIAL HEALTH CHECK ──\n\n"
    report += f"Score: {score:.1f}/10"
    if score >= 8:
        report += " — Excellent! You're on a strong path.\n"
    elif score >= 6:
        report += " — Good, but there's room to improve.\n"
    elif score >= 4:
        report += " — Needs attention. Let's fix the basics first.\n"
    else:
        report += " — Critical. Immediate action needed.\n"

    report += f"\n── BREAKDOWN ──\n"
    report += f"  Emergency Fund: {emergency_months:.1f} months covered ({ef_score}/2.5)\n"
    report += f"    → Target: 4 months (₹{monthly_expenses * 4:,.0f})\n"
    report += f"  Debt-to-Income Ratio: {debt_to_income:.1f}x annual income ({debt_score}/2.5)\n"
    report += f"    → EMI is {emi_to_income:.0f}% of income (keep under 40%)\n"
    report += f"  Savings Rate: {savings_rate:.0f}% ({sr_score}/2.5)\n"
    report += f"    → Target: 20-30% of income\n"
    report += f"  Investment Rate: {investment_rate:.0f}% ({inv_score}/2.5)\n"
    report += f"    → Target: 15-20% of income\n"

    # Priority actions
    report += f"\n── PRIORITY ACTIONS (do in this order) ──\n"
    priorities = []

    if emergency_months < 1:
        priorities.append("1. BUILD EMERGENCY FUND — You have less than 1 month of expenses saved. "
                         f"Save ₹{monthly_expenses * 2 - existing_savings:,.0f} to reach 2 months minimum.")
    elif emergency_months < 2:
        priorities.append(f"1. GROW EMERGENCY FUND — You have {emergency_months:.1f} months. "
                         f"Add ₹{monthly_expenses * 4 - existing_savings:,.0f} to reach 4 months.")

    if emi_to_income > 50:
        priorities.append(f"2. REDUCE DEBT BURDEN — EMIs consume {emi_to_income:.0f}% of income. "
                         "This is dangerously high. Consider debt consolidation or prepaying highest-interest loans.")
    elif emi_to_income > 40:
        priorities.append(f"2. MANAGE DEBT — EMIs at {emi_to_income:.0f}% of income is high. "
                         "Aggressively prepay your highest-interest debt.")

    if investment_rate < 5:
        priorities.append("3. START INVESTING — Even ₹500/month in a mutual fund SIP builds the habit. "
                         "Start today, increase later.")
    elif investment_rate < 15:
        priorities.append(f"3. INCREASE INVESTMENTS — {investment_rate:.0f}% is a start, but aim for 15-20%. "
                         f"Try adding ₹{(monthly_income * 0.15 - monthly_investment):,.0f}/month more.")

    if savings_rate < 10:
        priorities.append("4. CUT EXPENSES — You're saving less than 10% of income. "
                         "Review entertainment and miscellaneous spending.")

    if not priorities:
        priorities.append("You're in great shape! Focus on increasing investments or planning for specific goals "
                         "(house, retirement, children's education).")

    for p in priorities:
        report += f"  {p}\n"

    return report
