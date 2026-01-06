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
from database import SessionLocal
from utils.memory_graph import record_denial_pattern, get_pattern_suggestions

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
    workflow.add_node("negotiator_agent", run_negotiator_agent)
    workflow.add_node("auditor_agent", run_auditor_agent)
    
    # Define Edges (Linear Flow)
    workflow.set_entry_point("policy_agent")
    
    workflow.add_edge("policy_agent", "medical_agent")
    workflow.add_edge("medical_agent", "legal_agent")
    workflow.add_edge("legal_agent", "negotiator_agent")
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

def run_appeal_workflow(ocr_data: dict, insurance_rules: dict, db_session: SessionLocal = None) -> str:
    """
    Entry point to run the entire graph.
    """
    print("\n🔗 STARTING MULTI-AGENT APPEAL WORKFLOW 🔗")
    print("---------------------------------------------")
    
    # Memory / Learning Step (Context Retrieval)
    past_pattern = None
    local_session = False
    if db_session is None:
        db_session = SessionLocal()
        local_session = True
        
    try:
        # Extract keys for pattern matching
        denial_doc = ocr_data.get("denial", {}).get("structured", {})
        bill_doc = ocr_data.get("bill", {}).get("structured", {})
        
        insurance = denial_doc.get("insurer") or bill_doc.get("patient_insurance")
        denial_code = denial_doc.get("denial_code")
        procedure = denial_doc.get("procedure") or bill_doc.get("procedure_name")
        cpt_code = bill_doc.get("cpt_code")
        
        if insurance and denial_code:
            suggestion = get_pattern_suggestions(db_session, insurance, denial_code, procedure)
            if suggestion.get("found"):
                print(f"🧠 MEMORY: Found past pattern! {suggestion.get('message')}")
                past_pattern = suggestion
            else:
                print("🧠 MEMORY: No matching past patterns found.")
    except Exception as e:
        print(f"⚠️ Memory Retrieval Failed: {e}")
        past_pattern = None

    app = create_appeal_graph()
    
    # Initial State
    initial_state = {
        "ocr_data": ocr_data,
        "insurance_rules": insurance_rules,
        "iteration_count": 0,
        "audit_feedback": [],
        "past_pattern_context": past_pattern 
    }
    
    # Run Graph
    # We iterate over steps to print progress as requested
    final_output = None
    
    # For logging purposes only
    for event in app.stream(initial_state):
        for key, value in event.items():
            print(f"✅ Agent Completed: {key}")
            # print(f"   Output keys: {list(value.keys())}")
            
    print("---------------------------------------------")
    print("🏁 WORKFLOW COMPLETE 🏁\n")
    
    # Get final state
    final_state = app.invoke(initial_state)
    
    # Record Pattern (Learning Step)
    try:
        if insurance and denial_code:
            # Infer missing docs from Policy Agent
            policy_analysis = final_state.get("policy_analysis", {})
            findings = policy_analysis.get("findings", []) if policy_analysis else []
            missing_docs = [f.issue for f in findings if "Missing" in f.issue]
            
            # Infer resolution from Medical Agent (just a heuristic for now)
            # In a real system, this would come from user outcome feedback
            medical_analysis = final_state.get("medical_analysis", {})
            resolved_by = []
            if medical_analysis and "key_findings" in medical_analysis:
                 resolved_by.append("Clinical Justification")
            
            record_denial_pattern(
                db_session,
                insurance=insurance,
                procedure=procedure,
                cpt_code=cpt_code,
                denial_code=denial_code,
                missing_docs=missing_docs,
                resolved_by=resolved_by
            )
            print("🧠 MEMORY: Pattern recorded/updated.")
    except Exception as e:
         print(f"⚠️ Memory Store Failed: {e}")

    if local_session:
        db_session.close()

    return final_state.get("appeal_draft", "Error: No draft generated.")
