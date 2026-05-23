# FinPilot AI 🇮🇳

**Your personal finance agent — built for the common Indian investor.**

A multi-agent AI system that plans your budget, suggests investments, tackles debt strategically, compares tax regimes, and guides you through ITR filing — all through natural conversation.

> **Philosophy:** *"Investment is not what you put after leftovers — first take the investment amount from income, then plan the rest for spending."*

---

## What Can FinPilot Do?

| Capability | What It Does |
|---|---|
| **Budget Planning** | Invest-first allocation, spending health flags, 50-35-15 framework |
| **Financial Health Score** | 1-10 score with priority actions — emergency fund, debt, savings, investment |
| **Debt Payoff Strategy** | Avalanche vs Snowball comparison, interest savings projection |
| **Investment Allocation** | Age & risk-based strategy, SIP planning, goal-based projections |
| **Compounding Visualizer** | Year-by-year wealth growth to show the power of staying invested |
| **Tax Calculator** | New vs Old regime comparison, multi-head income, deduction optimization |
| **ITR Filing Guide** | Form recommendation, field-by-field mapping, document checklist, deadlines |

---

## How It Works

FinPilot runs as an MCP (Model Context Protocol) server — it exposes financial tools that any LLM agent can call. You talk naturally, and the agent figures out which tool to use.

```
You: "I earn 12 lakh, pay 15K rent, have 2L in PPF. Which tax regime is better?"

FinPilot:
  ── TAX COMPARISON ──
    Gross Total Income: ₹12,00,000
      Salary: ₹12,00,000

  ── NEW REGIME ──
    Taxable Income (slab): ₹11,25,000
    Total Tax: ₹1,04,000
    Monthly In-hand: ₹91,333

  ── OLD REGIME ──
    Taxable Income (slab): ₹8,00,000
    Total Tax: ₹72,800
    Monthly In-hand: ₹93,933

  ── RECOMMENDATION ──
    ✅ OLD regime saves you ₹31,200/year (₹2,600/month)
```

---

## Example Conversations

### 1. Monthly Budget Planning

```
You: "I earn ₹80,000/month. Here's my expenses — rent 20K, groceries 8K, 
      EMI 12K, utilities 3K, insurance 2K, entertainment 5K, transport 4K, misc 3K"

FinPilot:
  💰 Monthly Income: ₹80,000

  ── INVEST FIRST ──
  Your investment (15% of income): ₹12,000/month
    → In 5 years this grows to: ~₹9,93,000
    → In 10 years this grows to: ~₹27,85,000
  Remaining for expenses: ₹68,000

  ── WHERE YOUR MONEY GOES ──
    Rent: ₹20,000 (25.0% of income) ✅
    Loan EMI: ₹12,000 (15.0% of income) ✅
    Groceries: ₹8,000 (10.0% of income) ✅
    Entertainment: ₹5,000 (6.3% of income) ✅
    ...
    Total: ₹57,000 (71% of income)

  ── BOTTOM LINE ──
  After investing and all expenses, you have ₹11,000 spare.
  Priority: Build an emergency fund of ₹2,28,000 (4 months of expenses).
```

### 2. Financial Health Check

```
You: "Check my financial health — I earn 1L/month, spend 65K, EMI is 20K, 
      have 1.5L savings, 8L total debt, and invest 5K/month"

FinPilot:
  ── FINANCIAL HEALTH CHECK ──
  Score: 4.5/10 — Needs attention. Let's fix the basics first.

  ── BREAKDOWN ──
    Emergency Fund: 2.3 months covered (1.5/2.5)
      → Target: 4 months (₹2,60,000)
    Debt-to-Income: 0.7x annual income (1.0/2.5)
      → EMI is 20% of income (keep under 40%) ✅
    Savings Rate: 35% (2.5/2.5) ✅
    Investment Rate: 5% (1.0/2.5)
      → Target: 15-20% of income

  ── PRIORITY ACTIONS ──
    1. GROW EMERGENCY FUND — Add ₹1,10,000 to reach 4 months
    2. INCREASE INVESTMENTS — You're at 5%, aim for 15% (₹15,000/month)
```

### 3. Debt Payoff Strategy

```
You: "I have 3 loans — personal loan 2L at 14%, credit card 50K at 36%, 
      car loan 4L at 9%. I can put an extra ₹5,000/month toward payoff."

FinPilot:
  ── DEBT OVERVIEW ──
  Total Outstanding: ₹6,50,000
  Weighted Average Interest: 12.8%

  ── PAYOFF STRATEGIES ──

    Avalanche (highest interest first) — RECOMMENDED:
      Target order: Credit Card → Personal Loan → Car Loan
      Debt-free in: 42 months (3y 6m)
      Total interest paid: ₹1,18,000

    Snowball (smallest balance first):
      Target order: Credit Card → Personal Loan → Car Loan
      Debt-free in: 44 months (3y 8m)
      Total interest paid: ₹1,31,000

    Avalanche saves you ₹13,000 in interest!
    Extra ₹5,000/month saves ₹47,000 vs minimum payments only.
```

### 4. Power of Compounding

```
You: "Show me what happens if I invest ₹10,000/month for 20 years"

FinPilot:
  Monthly Investment: ₹10,000
  CAGR: 12% (compounded yearly)
  Duration: 20 years

  Year   Invested        Corpus          Gains
  --------------------------------------------------
  1      ₹1,20,000      ₹1,34,400      ₹14,400
  5      ₹6,00,000      ₹8,11,000      ₹2,11,000
  10     ₹12,00,000     ₹21,06,000     ₹9,06,000
  15     ₹18,00,000     ₹44,74,000     ₹26,74,000
  20     ₹24,00,000     ₹89,15,000     ₹65,15,000

  Total Invested: ₹24,00,000
  Final Corpus: ₹89,15,000
  Wealth Multiplier: 3.7x

  → You invested ₹24L, market gave you ₹65L free. That's compounding.
```

### 5. Goal-Based Investment

```
You: "I want ₹1 crore in 15 years for my kid's education"

FinPilot:
  Goal: ₹1,00,00,000 in 15 years
  CAGR: 12%
  Required Monthly Investment: ₹21,200

  Year   Invested        Corpus        Progress
  ------------------------------------------------
  5      ₹12,72,000     ₹17,18,000      17.2%
  10     ₹25,44,000     ₹47,78,000      47.8%
  15     ₹38,16,000     ₹1,00,00,000   100.0%

  Total You Invest: ₹38,16,000
  Gains from Compounding: ₹61,84,000
  → Market does 62% of the work. You just need to stay consistent.
```

### 6. Tax Regime Comparison (Multi-head Income)

```
You: "My salary is 15L, I get 2.4L rent, sold stocks for 80K STCG, 
      and have 30K FD interest. I claim 1.5L under 80C and 25K health insurance."

FinPilot:
  ── TAX COMPARISON ──
    Gross Total Income: ₹18,30,000/year
      Salary: ₹15,00,000
      Rental Income: ₹2,40,000
      STCG (equity): ₹80,000
      Other (FD/dividends): ₹30,000

  ── NEW REGIME ──
    Taxable Income (slab): ₹16,43,000
    Slab Tax: ₹2,58,600
    STCG Tax (₹80,000 @ 20%): ₹16,000
    Total Tax: ₹2,85,588

  ── OLD REGIME ──
    Taxable Income (slab): ₹13,43,000
    Slab Tax: ₹1,98,600
    STCG Tax (₹80,000 @ 20%): ₹16,000
    Total Tax: ₹2,23,188

  ── RECOMMENDATION ──
    ✅ OLD regime saves you ₹62,400/year (₹5,200/month)
```

### 7. ITR Filing Guide

```
You: "Help me file my ITR"

FinPilot:
  ══════════════════════════════════════
    ITR FILING GUIDE — FY 2025-26 (AY 2026-27)
  ══════════════════════════════════════

  PAN: <YOUR_PAN_NUMBER>
  Regime: NEW
  Form: ITR-2
  Reason: You have capital gains income — requires ITR-2

  ── INCOME DETAILS (Form Fields) ──

    📋 Section: Income from Salary
       Gross Salary: ₹15,00,000
       Standard Deduction (16(ia)): ₹75,000
       Net Salary: ₹14,25,000

    📋 Section: Income from House Property
       Gross Rent Received: ₹2,40,000
       Less: 30% Standard Deduction: ₹72,000
       Net HP Income: ₹1,68,000

    📋 Section: Capital Gains (Schedule CG)
       STCG (equity, section 111A): ₹80,000
       Tax Rate: 20%

  ── HOW TO FILE ──
    1. Go to: https://www.incometax.gov.in
    2. Login with PAN + password (or Aadhaar OTP)
    3. e-File → Income Tax Returns → File ITR
    4. Select: AY 2026-27, ITR-2, Filing Type: Original
    5. Choose: NEW regime
    6. Fill sections using values above
    7. Verify → Submit → e-Verify (Aadhaar OTP recommended)

  ── DEADLINES ──
    Due Date: 31 July 2026
    Late Fee: ₹5,000 (if income > ₹5L)

  ── DOCUMENTS TO KEEP READY ──
    • Form 16 (from employer)
    • Rent agreement / receipts
    • Broker P&L statement / Capital gains statement
    • Bank interest certificates / Form 16A
    • Bank account details (for refund credit)
    • Aadhaar linked to PAN (for e-verification)

  ── TIP ──
    Download AIS (Annual Information Statement) from the portal.
    Match your numbers with AIS to avoid mismatch notices.
```

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                   User (Chat)                    │
└────────────────────────┬─────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────┐
│              LLM Agent (Supervisor)              │
│   Understands intent → Gathers data → Calls     │
│   the right tool with complete information       │
└────────────────────────┬─────────────────────────┘
                         │ MCP Protocol
┌────────────────────────▼─────────────────────────┐
│           FinPilot MCP Tool Server               │
├──────────────────────────────────────────────────┤
│  budget_tools.py    │ allocate_monthly_finances  │
│                     │ assess_financial_health    │
├─────────────────────┼────────────────────────────┤
│  debt_tools.py      │ plan_debt_payoff           │
├─────────────────────┼────────────────────────────┤
│  investment_tools.py│ suggest_investment_strategy │
│                     │ calculate_compounding      │
│                     │ plan_goal_investment       │
├─────────────────────┼────────────────────────────┤
│  tax_tools.py       │ calculate_tax              │
│                     │ prepare_itr_summary        │
└─────────────────────┴────────────────────────────┘
```

---

## Tools Reference

### Budget & Health

| Tool | Purpose | Key Params |
|---|---|---|
| `allocate_monthly_finances` | Invest-first budget planner with spending flags | `income`, `expenses` (8 categories), `investment_percent` |
| `assess_financial_health` | Health score 1-10 with priority action steps | `monthly_income`, `monthly_expenses`, `monthly_emi`, `existing_savings`, `total_debt`, `monthly_investment` |

### Debt

| Tool | Purpose | Key Params |
|---|---|---|
| `plan_debt_payoff` | Avalanche vs Snowball comparison with simulation | `debts` (list of name, balance, rate, EMI), `extra_monthly` |

### Investment

| Tool | Purpose | Key Params |
|---|---|---|
| `suggest_investment_strategy` | Risk-based allocation across asset classes | `age`, `risk_tolerance`, `savings` |
| `calculate_compounding` | Year-by-year wealth projection (power of SIP) | `monthly_investment`, `years`, `cagr` |
| `plan_goal_investment` | "How much SIP do I need for X goal in Y years?" | `target_amount`, `years`, `cagr` |

### Tax & ITR

| Tool | Purpose | Key Params |
|---|---|---|
| `calculate_tax` | Multi-head income tax with regime comparison | `income` (salary, rental, STCG, LTCG, other), `deductions` (80C, 80D, HRA, NPS, home loan, LTA), `regime` |
| `prepare_itr_summary` | ITR form guide with field mapping & checklist | `income`, `deductions`, `regime`, `fy` |

---

## Design Principles

1. **Invest First, Spend Later** — Every budget starts by setting aside investment, not treating it as leftovers.

2. **Educate, Don't Just Calculate** — Tools explain *why* (e.g., "LTCG is taxed at 12.5% above ₹1.25L") so users learn as they plan.

3. **Indian Context Native** — INR, Indian tax slabs (FY 2025-26), 80C/80D/HRA, New vs Old regime, ITR-1/ITR-2 forms.

4. **Gather First, Compute Once** — The agent asks about all income sources and deductions upfront, then calls the tool once with complete data. No half-baked results.

5. **Legal Caps Enforced** — Deductions are auto-capped (80C at ₹1.5L, 80D at ₹50K, etc.) with warnings shown to user.

6. **No Sensitive Data Stored** — PAN is never collected or stored. The tool uses `<YOUR_PAN_NUMBER>` as a placeholder.

---

## Quick Start

```bash
# Clone and setup
cd "FinPilot AI"
pip install -r requirements.txt

# Run the MCP server
python mcp_server/server.py
```

The server exposes all tools via FastMCP at the `/finance` endpoint.

---

## Tech Stack

- **Python 3.11+** with async/await
- **FastMCP** — Model Context Protocol server for tool registration
- **Starlette + Uvicorn** — ASGI server for HTTP transport
- **LangGraph** — Agent workflow orchestration
- **Streamlit** — Chat UI
- **Docker** — Containerized deployment

---

## Project Structure

```
app/core/tools/
├── budget_tools.py       # Budget allocation + financial health scoring
├── debt_tools.py         # Debt payoff strategy (Avalanche/Snowball)
├── investment_tools.py   # Investment allocation + compounding + goal planning
└── tax_tools.py          # Tax calculation + regime comparison + ITR guide

mcp_server/
└── server.py             # FastMCP server registering all tools

ui/
└── streamlit_app.py      # Chat interface
```

---

## Who Is This For?

- **Salaried professionals** who want to understand where their money goes
- **First-time investors** who need to see *why* SIP works (compounding visualization)
- **People with multiple loans** who want a clear payoff strategy
- **Anyone confused by New vs Old tax regime** — see the exact savings
- **ITR filers** who don't want to pay a CA ₹2,000 for a straightforward return

---

## Roadmap

- [ ] Mutual fund SIP tracker integration
- [ ] Insurance adequacy calculator (term life, health)
- [ ] Retirement corpus planner (with inflation adjustment)
- [ ] AIS data parser (upload your AIS PDF, auto-fill tax tool)
- [ ] Multi-year tax planning (project deductions to optimize regime choice)
- [ ] NPS tier-1 vs PPF comparison tool

---

## License

MIT

---

*Built for every Indian who deserves a financial advisor — not just the top 1%.*
