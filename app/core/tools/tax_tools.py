# Tax calculation tool for Indian income tax based on the latest tax slabs and regimes.
from typing import TypedDict


class IncomeBreakdown(TypedDict, total=False):
    salary: float              # Annual salary/CTC — standard deduction applies
    rental_income: float       # Rent received from property — 30% standard deduction
    stcg_equity: float         # Short-term capital gains (equity, held < 1 year) — flat 20%
    ltcg_equity: float         # Long-term capital gains (equity/MF, held > 1 year) — 12.5% above ₹1.25L
    other_income: float        # FD interest, dividends, freelance — taxed at slab rates


class TaxDeductions(TypedDict, total=False):
    section_80c: float       # PPF, ELSS, LIC, NSC, tuition fees — max ₹1,50,000
    section_80d: float       # Health insurance premium — max ₹25,000 (₹50,000 if senior citizen)
    hra_exemption: float     # HRA exemption amount (based on rent paid, salary, city)
    nps_80ccd1b: float       # NPS self-contribution — max ₹50,000
    home_loan_interest: float  # Section 24 — max ₹2,00,000
    lta: float               # Leave Travel Allowance exemption


def register_tax_tools(mcp):
    @mcp.tool()
    async def calculate_tax(income: IncomeBreakdown, deductions: TaxDeductions = None, regime: str = "both") -> str:
        """
        Calculate estimated Indian income tax for an individual.
        Handles multiple income heads with their specific tax treatment:
        - Salary: slab rates with standard deduction
        - Rental income: 30% standard deduction, then slab rates
        - STCG (equity): flat 20%
        - LTCG (equity): 12.5% above ₹1.25L exemption
        - Other income (FD, dividends): slab rates

        IMPORTANT: Before calling this tool, ask the user about ALL their income
        sources (salary, rent, stocks/MF gains, FD interest) and all deductions
        they claim. Gather complete data first, then call once for accurate results.

        When regime is "both", compares new and old regime side-by-side and
        recommends the better one. Deductions apply only to old regime.

        Args:
            income: Breakdown of income by source (salary, rental_income, stcg_equity, ltcg_equity, other_income) in INR
            deductions: Breakdown of deductions (section_80c, section_80d, hra_exemption, nps_80ccd1b, home_loan_interest, lta) in INR — only applies to old regime
            regime: Tax regime - "new", "old", or "both" (default "both" for comparison)
        """

        # --- Parse income breakdown ---
        salary = income.get("salary", 0)
        rental_income = income.get("rental_income", 0)
        stcg_equity = income.get("stcg_equity", 0)
        ltcg_equity = income.get("ltcg_equity", 0)
        other_income = income.get("other_income", 0)

        gross_total = salary + rental_income + stcg_equity + ltcg_equity + other_income

        # Rental income: 30% standard deduction under both regimes
        rental_taxable = rental_income * 0.70

        # Capital gains — taxed separately at special rates
        ltcg_exempt = min(ltcg_equity, 125000)  # First ₹1.25L exempt
        ltcg_taxable = max(0, ltcg_equity - 125000)
        ltcg_tax = ltcg_taxable * 0.125  # 12.5%
        stcg_tax = stcg_equity * 0.20    # Flat 20%

        # Legal caps for each deduction section
        caps = {
            "section_80c": 150000,
            "section_80d": 50000,
            "hra_exemption": float("inf"),  # No fixed cap, depends on calculation
            "nps_80ccd1b": 50000,
            "home_loan_interest": 200000,
            "lta": float("inf"),  # Depends on actual travel
        }

        # Process deductions with caps
        deduction_details = {}
        total_deductions = 0.0
        if deductions:
            for key, cap in caps.items():
                claimed = deductions.get(key, 0)
                allowed = min(claimed, cap)
                deduction_details[key] = {"claimed": claimed, "allowed": allowed}
                total_deductions += allowed

        def _compute_tax(sal: float, rental_tax: float, other: float, ded: float, reg: str) -> dict:
            """Compute slab tax on salary + rental + other income. Capital gains handled separately."""
            if reg == "new":
                slabs = [
                    (300000, 0.0),
                    (400000, 0.05),
                    (500000, 0.10),
                    (600000, 0.15),
                    (700000, 0.20),
                    (float("inf"), 0.30),
                ]
                std_ded = 75000
            else:
                slabs = [
                    (250000, 0.0),
                    (500000, 0.05),
                    (1000000, 0.20),
                    (float("inf"), 0.30),
                ]
                std_ded = 50000

            applicable_ded = ded if reg == "old" else 0.0
            # Standard deduction applies only to salary income
            salary_after_std = max(0, sal - std_ded)
            taxable = max(0, salary_after_std + rental_tax + other - applicable_ded)

            slab_tax = 0.0
            prev_limit = 0
            for limit, rate in slabs:
                bracket = min(taxable, limit) - prev_limit
                if bracket <= 0:
                    break
                slab_tax += bracket * rate
                prev_limit = limit

            # Total tax = slab tax + capital gains tax
            total_base_tax = slab_tax + stcg_tax + ltcg_tax
            cess = total_base_tax * 0.04
            total_tax = total_base_tax + cess

            return {
                "regime": reg,
                "std_ded": std_ded,
                "deductions": applicable_ded,
                "taxable_slab": taxable,
                "slab_tax": slab_tax,
                "stcg_tax": stcg_tax,
                "ltcg_tax": ltcg_tax,
                "cess": cess,
                "total_tax": total_tax,
                "monthly_tax": total_tax / 12,
                "in_hand_monthly": (gross_total / 12) - (total_tax / 12),
            }

        def _format_regime(data: dict) -> str:
            report = f"── {data['regime'].upper()} REGIME ──\n"
            report += f"  Gross Total Income: ₹{gross_total:,.0f}\n"
            if salary:
                report += f"    Salary: ₹{salary:,.0f}\n"
                report += f"    (-) Standard Deduction: ₹{data['std_ded']:,.0f}\n"
            if rental_income:
                report += f"    Rental Income: ₹{rental_income:,.0f} → Taxable: ₹{rental_taxable:,.0f} (30% std deduction)\n"
            if other_income:
                report += f"    Other Income (FD/dividends): ₹{other_income:,.0f}\n"
            if data["regime"] == "old" and data["deductions"] > 0:
                report += f"    (-) Deductions: ₹{data['deductions']:,.0f}\n"
            report += f"  ─────────────────\n"
            report += f"  Taxable Income (slab): ₹{data['taxable_slab']:,.0f}\n"
            report += f"  Slab Tax: ₹{data['slab_tax']:,.0f}\n"
            if stcg_equity:
                report += f"  STCG Tax (₹{stcg_equity:,.0f} @ 20%): ₹{data['stcg_tax']:,.0f}\n"
            if ltcg_equity:
                report += f"  LTCG Tax (₹{ltcg_equity:,.0f}, exempt ₹{ltcg_exempt:,.0f}, @ 12.5%): ₹{data['ltcg_tax']:,.0f}\n"
            report += f"  (+) 4% Cess: ₹{data['cess']:,.0f}\n"
            report += f"  Total Tax: ₹{data['total_tax']:,.0f}\n"
            report += f"  Monthly In-hand: ₹{data['in_hand_monthly']:,.0f}\n"
            return report

        def _format_deductions() -> str:
            if not deduction_details:
                return ""
            labels = {
                "section_80c": "80C (PPF/ELSS/LIC)",
                "section_80d": "80D (Health Insurance)",
                "hra_exemption": "HRA Exemption",
                "nps_80ccd1b": "NPS (80CCD1B)",
                "home_loan_interest": "Home Loan Interest (Sec 24)",
                "lta": "LTA",
            }
            report = f"\n── DEDUCTIONS BREAKDOWN (Old Regime) ──\n"
            for key, detail in deduction_details.items():
                if detail["claimed"] > 0:
                    cap_note = ""
                    if detail["claimed"] > detail["allowed"]:
                        cap_note = f" (capped from ₹{detail['claimed']:,.0f})"
                    report += f"  {labels[key]}: ₹{detail['allowed']:,.0f}{cap_note}\n"
            report += f"  ─────────────────\n"
            report += f"  Total Deductions: ₹{total_deductions:,.0f}\n"
            return report

        if regime in ("new", "old"):
            data = _compute_tax(salary, rental_taxable, other_income, total_deductions, regime)
            report = f"── TAX CALCULATION ({regime.upper()} REGIME) ──\n\n"
            report += f"  Gross Total Income: ₹{gross_total:,.0f}\n"
            if salary:
                report += f"    Salary: ₹{salary:,.0f}\n"
                report += f"    (-) Standard Deduction: ₹{data['std_ded']:,.0f}\n"
            if rental_income:
                report += f"    Rental Income: ₹{rental_income:,.0f} → Taxable: ₹{rental_taxable:,.0f} (30% std deduction)\n"
            if other_income:
                report += f"    Other Income (FD/dividends): ₹{other_income:,.0f}\n"
            if regime == "old" and data["deductions"] > 0:
                report += f"    (-) Deductions: ₹{data['deductions']:,.0f}\n"
            report += f"  ─────────────────\n"
            report += f"  Taxable Income (slab): ₹{data['taxable_slab']:,.0f}\n\n"
            report += f"  Slab Tax: ₹{data['slab_tax']:,.0f}\n"
            if stcg_equity:
                report += f"  STCG Tax (₹{stcg_equity:,.0f} @ 20%): ₹{data['stcg_tax']:,.0f}\n"
            if ltcg_equity:
                report += f"  LTCG Tax (₹{ltcg_equity:,.0f}, exempt ₹{ltcg_exempt:,.0f}, @ 12.5%): ₹{data['ltcg_tax']:,.0f}\n"
            report += f"  (+) 4% Cess: ₹{data['cess']:,.0f}\n"
            report += f"  Total Tax: ₹{data['total_tax']:,.0f}\n\n"
            report += f"── MONTHLY VIEW ──\n"
            report += f"  Monthly Income: ₹{gross_total / 12:,.0f}\n"
            report += f"  Monthly Tax: ₹{data['monthly_tax']:,.0f}\n"
            report += f"  In-hand (approx): ₹{data['in_hand_monthly']:,.0f}\n"

            if regime == "old" and deduction_details:
                report += _format_deductions()

            if regime == "new":
                report += f"\n── NOTE ──\n"
                report += f"  New regime does NOT exempt: HRA, LTA, meal vouchers,\n"
                report += f"  telephone reimbursement, or 80C/80D deductions.\n"
                report += f"  Only standard deduction (₹{data['std_ded']:,.0f}) is allowed on salary."
            else:
                report += f"\n── TIP ──\n"
                report += f"  Old regime allows: 80C (₹1.5L), 80D (₹25K-₹50K), HRA, LTA,\n"
                report += f"  NPS (₹50K extra), home loan interest (₹2L).\n"
                report += f"  Maximize these to reduce tax further."

            if stcg_equity or ltcg_equity:
                report += f"\n\n── CAPITAL GAINS NOTE ──\n"
                report += f"  Capital gains tax is the same in both regimes.\n"
                if ltcg_equity:
                    report += f"  LTCG: First ₹1.25L is exempt. Above that taxed at 12.5%.\n"
                if stcg_equity:
                    report += f"  STCG (equity): Flat 20%. Consider holding > 1 year for lower LTCG rate."
            return report

        # regime == "both" — compare and recommend
        new_data = _compute_tax(salary, rental_taxable, other_income, total_deductions, "new")
        old_data = _compute_tax(salary, rental_taxable, other_income, total_deductions, "old")

        report = f"── TAX COMPARISON ──\n"
        report += f"  Gross Total Income: ₹{gross_total:,.0f}/year (₹{gross_total / 12:,.0f}/month)\n"
        if salary:
            report += f"    Salary: ₹{salary:,.0f}\n"
        if rental_income:
            report += f"    Rental Income: ₹{rental_income:,.0f}\n"
        if stcg_equity:
            report += f"    STCG (equity): ₹{stcg_equity:,.0f}\n"
        if ltcg_equity:
            report += f"    LTCG (equity): ₹{ltcg_equity:,.0f}\n"
        if other_income:
            report += f"    Other (FD/dividends): ₹{other_income:,.0f}\n"
        report += f"\n"

        report += _format_regime(new_data)
        report += f"\n"
        report += _format_regime(old_data)

        if deduction_details:
            report += _format_deductions()

        # Recommendation
        savings = abs(new_data["total_tax"] - old_data["total_tax"])
        monthly_savings = savings / 12

        report += f"\n── RECOMMENDATION ──\n"
        if new_data["total_tax"] < old_data["total_tax"]:
            report += f"  ✅ NEW regime saves you ₹{savings:,.0f}/year (₹{monthly_savings:,.0f}/month)\n"
            report += f"  Go with NEW regime — simpler, no documentation needed."
        elif old_data["total_tax"] < new_data["total_tax"]:
            report += f"  ✅ OLD regime saves you ₹{savings:,.0f}/year (₹{monthly_savings:,.0f}/month)\n"
            report += f"  Go with OLD regime — make sure to submit investment proofs to employer."
        else:
            report += f"  Both regimes result in same tax (₹{new_data['total_tax']:,.0f}).\n"
            report += f"  Go with NEW regime for simplicity — no proofs needed."

        if not deductions:
            report += f"\n\n── NOTE ──\n"
            report += f"  You haven't provided deductions. Common ones to check:\n"
            report += f"  • 80C: PPF, ELSS mutual funds, LIC premium (max ₹1.5L)\n"
            report += f"  • 80D: Health insurance premium (max ₹25K-₹50K)\n"
            report += f"  • HRA: If you pay rent and get HRA in salary\n"
            report += f"  • NPS: Extra ₹50K deduction under 80CCD(1B)\n"
            report += f"  • Home Loan: Interest up to ₹2L under Section 24\n"
            report += f"  • LTA: Leave travel allowance (actual travel expenses)\n"
            report += f"  Tell me which of these apply to you for an accurate comparison."

        return report

    @mcp.tool()
    async def prepare_itr_summary(
        income: IncomeBreakdown,
        deductions: TaxDeductions = None,
        regime: str = "new",
        fy: str = "2025-26",
    ) -> str:
        """
        Prepare an ITR-ready summary that maps calculated tax data to actual
        ITR form fields. Helps user file their return by telling them exactly
        which form to use and what values to enter in each section.

        IMPORTANT: Before calling this tool, ensure you have already gathered
        the user's complete income and deduction details. This tool generates
        the filing guide — call calculate_tax first if user wants to see the
        tax breakdown.

        Args:
            income: Breakdown of income by source (salary, rental_income, stcg_equity, ltcg_equity, other_income) in INR
            deductions: Breakdown of deductions — only relevant if regime is "old"
            regime: Which regime user has chosen to file under - "new" or "old"
            fy: Financial year (default "2025-26")
        """

        # --- Parse income ---
        salary = income.get("salary", 0)
        rental_income = income.get("rental_income", 0)
        stcg_equity = income.get("stcg_equity", 0)
        ltcg_equity = income.get("ltcg_equity", 0)
        other_income = income.get("other_income", 0)

        has_capital_gains = stcg_equity > 0 or ltcg_equity > 0
        has_multiple_property = False  # Could be extended later

        # --- Determine ITR form ---
        if has_capital_gains:
            itr_form = "ITR-2"
            form_reason = "You have capital gains income — requires ITR-2"
        elif rental_income > 0 and salary > 0:
            itr_form = "ITR-1 (Sahaj)"
            form_reason = "Salary + one house property income — eligible for ITR-1"
        elif salary > 0 and other_income > 0 and not rental_income:
            itr_form = "ITR-1 (Sahaj)"
            form_reason = "Salary + other income (FD/dividend) — eligible for ITR-1"
        elif salary > 0:
            itr_form = "ITR-1 (Sahaj)"
            form_reason = "Salary income only — simplest form"
        else:
            itr_form = "ITR-2"
            form_reason = "Non-salary income sources — use ITR-2"

        # --- Compute values for form fields ---
        rental_taxable = rental_income * 0.70
        ltcg_exempt = min(ltcg_equity, 125000)
        ltcg_taxable = max(0, ltcg_equity - 125000)

        std_ded = 75000 if regime == "new" else 50000

        # Process deductions
        caps = {
            "section_80c": 150000,
            "section_80d": 50000,
            "hra_exemption": float("inf"),
            "nps_80ccd1b": 50000,
            "home_loan_interest": 200000,
            "lta": float("inf"),
        }
        total_deductions = 0.0
        ded_breakdown = {}
        if deductions and regime == "old":
            for key, cap in caps.items():
                claimed = deductions.get(key, 0)
                allowed = min(claimed, cap)
                if allowed > 0:
                    ded_breakdown[key] = allowed
                    total_deductions += allowed

        # Assessment year
        fy_parts = fy.split("-")
        ay = f"{int(fy_parts[0]) + 1}-{int(fy_parts[1]) + 1}"

        # --- Build the summary ---
        report = f"══════════════════════════════════════\n"
        report += f"  ITR FILING GUIDE — FY {fy} (AY {ay})\n"
        report += f"══════════════════════════════════════\n\n"

        report += f"  PAN: <YOUR_PAN_NUMBER>\n"
        report += f"  Regime: {regime.upper()}\n"
        report += f"  Form: {itr_form}\n"
        report += f"  Reason: {form_reason}\n\n"

        # --- Section-wise field mapping ---
        report += f"── INCOME DETAILS (Form Fields) ──\n\n"

        if salary:
            report += f"  📋 Section: Income from Salary\n"
            report += f"     Gross Salary: ₹{salary:,.0f}\n"
            report += f"     Standard Deduction (16(ia)): ₹{std_ded:,.0f}\n"
            report += f"     Net Salary: ₹{max(0, salary - std_ded):,.0f}\n\n"

        if rental_income:
            report += f"  📋 Section: Income from House Property\n"
            report += f"     Gross Rent Received: ₹{rental_income:,.0f}\n"
            report += f"     Less: 30% Standard Deduction: ₹{rental_income * 0.30:,.0f}\n"
            if deductions and regime == "old" and deductions.get("home_loan_interest", 0) > 0:
                hl = min(deductions["home_loan_interest"], 200000)
                report += f"     Less: Home Loan Interest (Sec 24): ₹{hl:,.0f}\n"
                report += f"     Net HP Income: ₹{max(0, rental_taxable - hl):,.0f}\n\n"
            else:
                report += f"     Net HP Income: ₹{rental_taxable:,.0f}\n\n"

        if has_capital_gains:
            report += f"  📋 Section: Capital Gains (Schedule CG)\n"
            if stcg_equity:
                report += f"     STCG (equity, section 111A): ₹{stcg_equity:,.0f}\n"
                report += f"     Tax Rate: 20%\n"
            if ltcg_equity:
                report += f"     LTCG (equity, section 112A): ₹{ltcg_equity:,.0f}\n"
                report += f"     Exempt up to ₹1,25,000: ₹{ltcg_exempt:,.0f}\n"
                report += f"     Taxable LTCG: ₹{ltcg_taxable:,.0f}\n"
                report += f"     Tax Rate: 12.5%\n"
            report += f"\n"

        if other_income:
            report += f"  📋 Section: Income from Other Sources\n"
            report += f"     FD Interest / Dividends / Other: ₹{other_income:,.0f}\n\n"

        # --- Deductions (old regime only) ---
        if regime == "old" and ded_breakdown:
            report += f"── DEDUCTIONS (Chapter VI-A) ──\n\n"
            labels = {
                "section_80c": "80C (PPF/ELSS/LIC/NSC)",
                "section_80d": "80D (Health Insurance)",
                "hra_exemption": "HRA Exemption (10(13A))",
                "nps_80ccd1b": "80CCD(1B) — NPS",
                "home_loan_interest": "Sec 24 — Home Loan Interest",
                "lta": "LTA Exemption (10(5))",
            }
            for key, amount in ded_breakdown.items():
                report += f"     {labels[key]}: ₹{amount:,.0f}\n"
            report += f"     ─────────────────\n"
            report += f"     Total Deductions: ₹{total_deductions:,.0f}\n\n"

        # --- Tax payable summary ---
        gross_total = salary + rental_income + stcg_equity + ltcg_equity + other_income
        report += f"── GROSS TOTAL INCOME ──\n"
        report += f"     ₹{gross_total:,.0f}\n\n"

        # --- Filing steps ---
        report += f"── HOW TO FILE ──\n\n"
        report += f"  1. Go to: https://www.incometax.gov.in\n"
        report += f"  2. Login with PAN + password (or Aadhaar OTP)\n"
        report += f"  3. e-File → Income Tax Returns → File ITR\n"
        report += f"  4. Select: AY {ay}, {itr_form}, Filing Type: Original\n"
        report += f"  5. Choose: {regime.upper()} regime\n"
        report += f"  6. Fill sections using values above\n"
        report += f"  7. Verify → Submit → e-Verify (Aadhaar OTP recommended)\n\n"

        # --- Deadlines ---
        report += f"── DEADLINES ──\n"
        report += f"  Due Date: 31 July {int(fy_parts[0]) + 1}\n"
        report += f"  Late Fee: ₹5,000 (if income > ₹5L) or ₹1,000 (if income ≤ ₹5L)\n"
        report += f"  Revised Return: Can be filed until 31 Dec {int(fy_parts[0]) + 1}\n\n"

        # --- Documents checklist ---
        report += f"── DOCUMENTS TO KEEP READY ──\n"
        docs = ["Form 16 (from employer)"]
        if rental_income:
            docs.append("Rent agreement / receipts")
        if has_capital_gains:
            docs.append("Broker P&L statement / Capital gains statement")
        if other_income:
            docs.append("Bank interest certificates / Form 16A")
        if regime == "old":
            if ded_breakdown.get("section_80c"):
                docs.append("80C proofs (PPF passbook, ELSS statement, LIC receipt)")
            if ded_breakdown.get("section_80d"):
                docs.append("Health insurance premium receipt")
            if ded_breakdown.get("nps_80ccd1b"):
                docs.append("NPS contribution statement")
            if ded_breakdown.get("home_loan_interest"):
                docs.append("Home loan interest certificate from bank")
        docs.append("Bank account details (for refund credit)")
        docs.append("Aadhaar linked to PAN (for e-verification)")

        for doc in docs:
            report += f"  • {doc}\n"

        report += f"\n── TIP ──\n"
        report += f"  Download AIS (Annual Information Statement) from the portal.\n"
        report += f"  It shows pre-filled income data the IT dept already has.\n"
        report += f"  Match your numbers with AIS to avoid mismatch notices."

        return report
