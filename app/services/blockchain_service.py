import os
import json
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "chain_log.jsonl")

def _append_event(event: dict):
    event_with_ts = {"ts": datetime.utcnow().isoformat() + "Z", **event}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event_with_ts, ensure_ascii=False) + "\n")

def record_file_upload(file_id: int, owner_id: int, hash_hex: str):
    _append_event({
        "type": "file_upload",
        "file_id": file_id,
        "owner_id": owner_id,
        "hash": hash_hex,
    })

def record_request_submit(request_id: int, file_id: int, requester_id: int, owner_id: int):
    _append_event({
        "type": "request_submit",
        "request_id": request_id,
        "file_id": file_id,
        "requester_id": requester_id,
        "owner_id": owner_id,
    })

def record_request_approve(request_id: int, decision: str):
    _append_event({
        "type": "request_approve",
        "request_id": request_id,
        "decision": decision,
    })


