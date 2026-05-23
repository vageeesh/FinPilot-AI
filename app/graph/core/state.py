""" One common global state:
    To check later: Should we keep seperate independent states: - like one state per agent and then one global state for the environment? 
"""
from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    user_query: str

    # Plan-and-Execute
    plan: List[List[str]]          # phases: e.g., [["budget_agent", "tax_agent"], ["investment_agent"]]
    current_phase: int             # index into plan
    plan_reasoning: str
    iteration: int                 # supervisor call count (guards infinite loops)

    # All agent outputs — generic, scales to any number of agents
    results: Dict[str, Any]

    # Execution trace
    intermediate_steps: List[Dict[str, Any]]

    # Final
    final_answer: Optional[str]
    done: bool
    error: Optional[str]
