from sqlalchemy.orm import Session
from datetime import datetime
from database import DenialPattern
import logging

logger = logging.getLogger(__name__)

def record_denial_pattern(
    db: Session,
    insurance: str,
    procedure: str,
    cpt_code: str,
    denial_code: str,
    missing_docs: list,
    resolved_by: list
):
    """
    Store or update a denial pattern in the knowledge graph (database).
    """
    # Normalize inputs
    insurance = insurance or "Unknown"
    procedure = procedure or "Unknown"
    cpt_code = cpt_code or "Unknown"
    denial_code = denial_code or "Unknown"
    
    # Try to find existing pattern
    # We match on Insurance + Denial Code + Procedure combination
    existing = db.query(DenialPattern).filter(
        DenialPattern.insurance == insurance,
        DenialPattern.denial_code == denial_code,
        DenialPattern.procedure == procedure
    ).first()
    
    if existing:
        existing.occurrence_count += 1
        existing.last_seen = datetime.utcnow()
        
        # Merge missing_docs (unique)
        current_missing = set(existing.missing_docs or [])
        current_missing.update(missing_docs or [])
        existing.missing_docs = list(current_missing)
        
        # Merge resolved_by (unique)
        current_resolved = set(existing.resolved_by or [])
        current_resolved.update(resolved_by or [])
        existing.resolved_by = list(current_resolved)
        
        logger.info(f"Updated denial pattern. Count: {existing.occurrence_count}")
    else:
        new_pattern = DenialPattern(
            insurance=insurance,
            procedure=procedure,
            cpt_code=cpt_code,
            denial_code=denial_code,
            missing_docs=missing_docs or [],
            resolved_by=resolved_by or [],
            occurrence_count=1,
            last_seen=datetime.utcnow()
        )
        db.add(new_pattern)
        logger.info("Created new denial pattern.")
    
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Failed to commit denial pattern: {e}")
        db.rollback()

def get_pattern_suggestions(
    db: Session, 
    insurance: str, 
    denial_code: str, 
    procedure: str = None, 
    threshold: int = 3
) -> dict:
    """
    Retrieve suggestions based on past resolved cases if occurrence threshold is met.
    """
    query = db.query(DenialPattern).filter(
        DenialPattern.insurance == insurance,
        DenialPattern.denial_code == denial_code
    )
    
    if procedure:
        query = query.filter(DenialPattern.procedure == procedure)
        
    pattern = query.first()
    
    if pattern and pattern.occurrence_count >= threshold:
        return {
            "found": True,
            "occurrence_count": pattern.occurrence_count,
            "suggested_solution": pattern.resolved_by,
            "common_missing_docs": pattern.missing_docs,
            "message": f"This denial pattern has occurred {pattern.occurrence_count} times. The most successful fix was: {', '.join(pattern.resolved_by)}"
        }
    
    return {"found": False}
