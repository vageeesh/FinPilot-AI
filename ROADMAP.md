# 🚀 Future Vision & Roadmap

This document outlines the strategic vision and upcoming capabilities for the LangGraph + MCP Fintech Web App. Our goal is to transition from a deterministic financial calculator to an autonomous, context-aware financial co-pilot.

---

## 📈 Business Use Cases (Alpha-Generating Skills)

### 1. Advanced Personalization & Context
- [ ] **Episodic User Memory:** Integrate vector storage (e.g., `pgvector`) to retain user risk tolerance, tax brackets, and goals across sessions.
- [ ] **Financial Health Scorecard:** A background supervisor agent to periodically assess debt-to-income ratios and emergency runway.

### 2. Specialized Financial Intelligence Agents
- [ ] **The Corporate Analyst Agent:** Read and analyze Mutual Fund factsheets, SEBI/regulatory filings, and earnings call transcripts.
- [ ] **The Multimodal Chart-Reader:** Leverage Vision LLMs to analyze stock graphs, candlestick patterns, and technical indicators.
- [ ] **Tax-Loss Harvesting Agent:** (India-specific) Automatically analyze portfolios to suggest capital gains tax optimization before March 31st.

---

## 🛠️ Technical Infrastructure Usecases

### 1. Architecture & Multi-Agent Orchestration
- [ ] **Dynamic Supervisor Routing:** Implement a LangGraph supervisor pattern to dynamically activate dormant worker agents on the fly based on intent.
- [ ] **Deterministic Financial Guardrails:** Implement strict Pydantic validation / NeMo Guardrails to mathematically verify agent outputs (e.g., EMI calculations).

### 2. Security, DevOps & Observability
- [ ] **Build Optimization:** Add `.dockerignore` to keep builds lightweight and secure.
- [ ] **Secrets Governance:** Migrate API keys and DB credentials to an external Secrets Manager.
- [ ] **LLM Observability Dashboard:** Integrate Langfuse or Arize Phoenix to track token usage, cost, latency, and agent trace logs.
- [ ] **Admin Control Panel:** Build a secure dashboard for system-level monitoring and access control.
