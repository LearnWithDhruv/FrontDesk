from firebase_init import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("firebase_db")
REQUEST_TIMEOUT = timedelta(minutes=30)

def create_help_request(question: str, caller_id: str) -> str:
    try:
        doc_ref = db.collection("help_requests").add({
            "question": question,
            "caller_id": caller_id,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + REQUEST_TIMEOUT,
            "last_updated": datetime.utcnow()
        })
        logger.info(f"Created help request ID: {doc_ref[1].id}")
        return doc_ref[1].id
    except Exception as e:
        logger.error(f"Failed to create help request: {e}")
        raise

def get_pending_requests():
    try:
        now = datetime.utcnow()
        requests = []
        
        pending = db.collection("help_requests") \
            .where("status", "==", "pending") \
            .stream()
        
        for doc in pending:
            data = doc.to_dict()
            if data.get("expires_at", now) > now:
                requests.append({"id": doc.id, **data})
            else:
                db.collection("help_requests").document(doc.id).update({
                    "status": "expired",
                    "last_updated": datetime.utcnow()
                })
        
        return requests
    except Exception as e:
        logger.error(f"Failed to get pending requests: {e}")
        return []

def update_help_request(request_id: str, answer: str):
    try:
        db.collection("help_requests").document(request_id).update({
            "answer": answer,
            "status": "resolved",
            "resolved_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        })
        
        request = db.collection("help_requests").document(request_id).get().to_dict()
        db.collection("learned_answers").add({
            "question": request["question"],
            "answer": answer,
            "learned_at": datetime.utcnow(),
            "source_request": request_id
        })
        
        logger.info(f"Updated help request {request_id} and added to knowledge base")
    except Exception as e:
        logger.error(f"Failed to update help request: {e}")
        raise

def get_learned_answers(limit: int = 50):
    try:
        return [
            {"id": doc.id, **doc.to_dict()}
            for doc in db.collection("learned_answers")
                .order_by("learned_at", direction="DESCENDING")
                .limit(limit)
                .stream()
        ]
    except Exception as e:
        logger.error(f"Failed to get learned answers: {e}")
        return []