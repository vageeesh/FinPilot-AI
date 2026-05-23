"""
Investment suggestion tools for Indian users, including strategy allocation, compounding effects, and goal-based planning.
"""

async def suggest_investment_strategy(age: int, risk_tolerance: str, savings: float) -> str:
    """
    Suggest how to allocate monthly savings across investments, emergency fund, and insurance.

    Args:
        age: Age of the individual
        risk_tolerance: "low", "medium", or "high"
        savings: Monthly savings available for allocation in INR (e.g., from allocate_monthly_finances)
    """
    # Step 1: Split savings into emergency fund, insurance, and investments
    emergency_pct = 0.20
    insurance_pct = 0.10
    investment_pct = 0.70

    emergency_amount = savings * emergency_pct
    insurance_amount = savings * insurance_pct
    investable_amount = savings * investment_pct

    # Step 2: Investment allocation based on risk tolerance
    if risk_tolerance == "low":
        strategy = "70% in bonds, 20% in large-cap stocks, 10% in cash"
        splits = {"Bonds": 0.70, "Large-cap Stocks": 0.20, "Cash": 0.10}
    elif risk_tolerance == "medium":
        strategy = "50% in stocks (mix of large-cap and mid-cap), 30% in bonds, 20% in cash"
        splits = {"Stocks (large + mid-cap)": 0.50, "Bonds": 0.30, "Cash": 0.20}
    else:  # high risk tolerance
        strategy = "80% in stocks (including small-cap), 10% in bonds, 10% in cash"
        splits = {"Stocks (incl. small-cap)": 0.80, "Bonds": 0.10, "Cash": 0.10}

    result = f"Monthly Savings: ₹{savings:,.0f}\n\n"
    result += f"Recommended Allocation:\n"
    result += f"  - Emergency Fund (20%): ₹{emergency_amount:,.0f}\n"
    result += f"  - Insurance (10%): ₹{insurance_amount:,.0f}\n"
    result += f"  - Investments (70%): ₹{investable_amount:,.0f}\n\n"
    result += (
        f"Investment Strategy (age {age}, {risk_tolerance} risk):\n{strategy}\n\n"
    )
    result += f"Investment Breakdown (₹{investable_amount:,.0f}):\n"
    for category, pct in splits.items():
        result += f"  - {category}: ₹{investable_amount * pct:,.0f}\n"

    return result


async def calculate_compounding(
    monthly_investment: float, years: int, cagr: float = 12.0
) -> str:
    """
    Show the power of compounding by projecting investment growth over time with yearly compounding.

    Args:
        monthly_investment: Monthly investment amount in INR
        years: Number of years to invest
        cagr: Expected annual rate of return in percentage (default 12%)
    """
    rate = cagr / 100
    total_invested = 0.0
    corpus = 0.0
    yearly_investment = monthly_investment * 12

    result = f"Monthly Investment: ₹{monthly_investment:,.0f}\n"
    result += f"CAGR: {cagr}% (compounded yearly)\n"
    result += f"Duration: {years} years\n\n"
    result += f"{'Year':<6} {'Invested':>14} {'Corpus':>14} {'Gains':>14}\n"
    result += f"{'-'*50}\n"

    for year in range(1, years + 1):
        total_invested += yearly_investment
        corpus = (corpus + yearly_investment) * (1 + rate)
        gains = corpus - total_invested
        result += (
            f"{year:<6} ₹{total_invested:>12,.0f} ₹{corpus:>12,.0f} ₹{gains:>12,.0f}\n"
        )

    total_gains = corpus - total_invested
    result += f"\nTotal Invested: ₹{total_invested:,.0f}\n"
    result += f"Final Corpus: ₹{corpus:,.0f}\n"
    result += f"Total Gains: ₹{total_gains:,.0f}\n"
    result += f"Wealth Multiplier: {corpus / total_invested:.1f}x"

    return result


async def plan_goal_investment(
    target_amount: float, years: int, cagr: float = 12.0
) -> str:
    """
    Calculate the monthly investment (SIP) needed to reach a financial goal, assuming yearly compounding.

    Args:
        target_amount: The target corpus amount the user wants to achieve in INR
        years: Number of years to reach the goal
        cagr: Expected annual rate of return in percentage (default 12%)
    """
    rate = cagr / 100

    # Formula: target = yearly_inv * (1+r) * [(1+r)^n - 1] / r
    # So:      yearly_inv = target * r / ((1+r) * [(1+r)^n - 1])
    growth_factor = (1 + rate) ** years
    yearly_investment = target_amount * rate / ((1 + rate) * (growth_factor - 1))
    monthly_investment = yearly_investment / 12
    total_invested = yearly_investment * years

    # Build year-by-year projection
    corpus = 0.0
    result = f"Goal: ₹{target_amount:,.0f} in {years} years\n"
    result += f"CAGR: {cagr}% (compounded yearly)\n"
    result += f"Required Monthly Investment: ₹{monthly_investment:,.0f}\n\n"
    result += f"{'Year':<6} {'Invested':>14} {'Corpus':>14} {'Progress':>10}\n"
    result += f"{'-'*46}\n"

    for year in range(1, years + 1):
        corpus = (corpus + yearly_investment) * (1 + rate)
        invested_so_far = yearly_investment * year
        progress = (corpus / target_amount) * 100
        result += (
            f"{year:<6} ₹{invested_so_far:>12,.0f} ₹{corpus:>12,.0f} {progress:>8.1f}%\n"
        )

    result += f"\nTotal You Invest: ₹{total_invested:,.0f}\n"
    result += f"Gains from Compounding: ₹{target_amount - total_invested:,.0f}\n"
    result += f"Final Corpus: ₹{corpus:,.0f}"

    return result
