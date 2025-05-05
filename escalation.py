import logging
from db import create_help_request
from datetime import datetime
from firebase_init import db

logger = logging.getLogger("escalation")

def escalate_question(question: str, caller_id: str) -> str:
    """Escalate question to supervisor with proper logging and real-time update."""
    try:
        request_id = create_help_request(question, caller_id)
        
        db.collection("notifications").add({
            "type": "help_request",
            "request_id": request_id,
            "caller_id": caller_id,
            "question": question,
            "timestamp": datetime.utcnow(),
            "status": "unread"
        })
        
        log_msg = (
            f"\n=== SUPERVISOR NOTIFICATION ===\n"
            f"New help request ({request_id})\n"
            f"Caller: {caller_id}\n"
            f"Question: {question}\n"
            f"Time: {datetime.utcnow().isoformat()}\n"
            f"Please respond at http://localhost:5000/respond/{request_id}\n"
            f"============================="
        )
        
        logger.info(log_msg)
        return request_id
    except Exception as e:
        logger.error(f"Failed to escalate question: {e}")
        raise