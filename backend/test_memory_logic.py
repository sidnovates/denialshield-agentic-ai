import sys
import os

# Add backend directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db, DenialPattern
from utils.memory_graph import record_denial_pattern, get_pattern_suggestions
import uuid

def test_memory_logic():
    print("\n🧪 TESTING DENIAL PATTERN MEMORY LOGIC 🧪")
    print("===========================================")
    
    # 1. Setup DB
    # Ensure tables exist
    init_db()
    db = SessionLocal()
    
    # Generate random ID to avoid conflicts with existing real data
    unique_id = str(uuid.uuid4())[:6]
    test_insurance = f"TestIns_{unique_id}"
    test_procedure = "MRI Lumbar"
    test_denial = "CO-50"
    
    print(f"📝 Creating test scenario:")
    print(f"   Insurance: {test_insurance}")
    print(f"   Denial: {test_denial}")
    print(f"   Threshold: 3")

    # 2. Simulate 3 occurrences (Learning Phase)
    print("\nPhase 1: Learning Loop (Simulating 3 previous denials)...")
    for i in range(3):
        record_denial_pattern(
            db,
            insurance=test_insurance,
            procedure=test_procedure,
            cpt_code="72148",
            denial_code=test_denial,
            missing_docs=["PT Notes", "X-Ray"],
            resolved_by=["Added Neuro Exam"]
        )
        print(f"   ✅ Recorded occurrence {i+1}")

    # 3. Simulate the 4th Case (Retrieval Phase)
    print("\nPhase 2: Verifying functionality for the 4th case...")
    print("   Querying memory for suggestions...")
    
    # This simulates what happens inside orchestrator.py before the agents run
    suggestion = get_pattern_suggestions(
        db, 
        insurance=test_insurance, 
        denial_code=test_denial,
        procedure=test_procedure,
        threshold=3
    )
    
    if suggestion["found"]:
        print("\n🎉 SUCCESS! Memory System Triggered.")
        print(f"   Stats: Seen {suggestion['occurrence_count']} times.")
        print(f"   AI Hint Generated: \"{suggestion['message']}\"")
        print(f"   Suggested Documents: {suggestion['common_missing_docs']}")
        print(f"   Suggested Fix: {suggestion['suggested_solution']}")
    else:
        print("\n❌ FAILED. Memory did not return a suggestion.")
        print(f"   Found status: {suggestion.get('found')}")

    # 4. Cleanup
    print("\nPhase 3: Cleanup")
    deleted = db.query(DenialPattern).filter(DenialPattern.insurance == test_insurance).delete()
    db.commit()
    db.close()
    print("   Test data removed.")
    print("===========================================")

if __name__ == "__main__":
    test_memory_logic()
