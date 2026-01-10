"""
Orchestrator: LangGraph Workflow Definition.
Wires together all agents into a cohesive state machine.
"""
from langgraph.graph import StateGraph, END
import logging

from agents.state import ClaimState
from agents.policy_agent import run_policy_agent
from agents.medical_agent import run_medical_agent
from agents.legal_agent import run_legal_agent
from agents.negotiator_agent import run_negotiator_agent
from agents.auditor_agent import run_auditor_agent
from agents.simulator_agent import run_simulator_agent

logger = logging.getLogger(__name__)

def should_continue(state: ClaimState) -> str:
    """
    Determine if the workflow should end or loop back.
    """
    feedback = state.get("audit_feedback", [])
    iteration = state.get("iteration_count", 0)

    # If no major issues or max iterations reached, end
    if not feedback or iteration >= 3:
        if iteration >= 3:
            print(">>> [LOOP] Max iterations reached. Accepting output.")
        else:
            print(">>> [LOOP] Audit passed. Finalizing appeal.")
        return "end"

    print(f">>> [LOOP] Audit failed with {len(feedback)} issues. Retrying... (Iteration {iteration})")
    return "retry"

def create_appeal_graph():
    """
    Build the LangGraph state machine.
    """
    # Initialize Graph
    workflow = StateGraph(ClaimState)

    # Add Nodes
    workflow.add_node("policy_agent", run_policy_agent)
    workflow.add_node("medical_agent", run_medical_agent)
    workflow.add_node("legal_agent", run_legal_agent)
    workflow.add_node("simulator_agent", run_simulator_agent)
    workflow.add_node("negotiator_agent", run_negotiator_agent)
    workflow.add_node("auditor_agent", run_auditor_agent)

    # Define Edges (Linear Flow)
    workflow.set_entry_point("policy_agent")

    workflow.add_edge("policy_agent", "medical_agent")
    workflow.add_edge("medical_agent", "legal_agent")
    workflow.add_edge("medical_agent", "simulator_agent") # Run Simulator after Medical data is available
    workflow.add_edge("legal_agent", "negotiator_agent")
    workflow.add_edge("simulator_agent", "negotiator_agent") # Simulator feeds into Negotiator
    workflow.add_edge("negotiator_agent", "auditor_agent")

    # Conditional Edge from Auditor
    workflow.add_conditional_edges(
        "auditor_agent",
        should_continue,
        {
            "end": END,
            "retry": "negotiator_agent"
        }
    )

    return workflow.compile()

def run_appeal_workflow(ocr_data: dict, insurance_rules: dict) -> dict:
    """
    Entry point to run the entire graph.
    Returns the full final state.
    """
    print("\n🔗 STARTING MULTI-AGENT APPEAL WORKFLOW 🔗")
    print("---------------------------------------------")

    app = create_appeal_graph()

    # Initial State
    initial_state = {
        "ocr_data": ocr_data,
        "insurance_rules": insurance_rules,
        "iteration_count": 0,
        "audit_feedback": []
    }

    # Run Graph
    # We iterate over steps to print progress as requested
    final_output = None

    for event in app.stream(initial_state):
        for key, value in event.items():
            print(f"✅ Agent Completed: {key}")
            # print(f"   Output keys: {list(value.keys())}")
            final_output = value

    print("---------------------------------------------")
    print("🏁 WORKFLOW COMPLETE 🏁\n")
    
    final_state = app.invoke(initial_state)
    return final_state