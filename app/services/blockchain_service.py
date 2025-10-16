# app/services/blockchain_service.py
from web3 import Web3
from sqlalchemy.orm import Session
from app.models.blockchain import BlockchainRecord
from app.core.config import settings
import json

w3 = Web3(Web3.HTTPProvider(settings.ETH_NODE_URL))

def push_to_blockchain(action: str, user_id: int, user_name: str, related_id: int, payload: dict) -> str:
    """推送到区块链并返回 tx_hash"""
    message = json.dumps({
        "action": action,
        "related_id": related_id,
        "payload": payload
    }, ensure_ascii=False)

    tx = {
        "nonce": w3.eth.get_transaction_count(settings.ETH_SENDER_ADDRESS),
        "to": settings.ETH_RECEIVER_ADDRESS,
        "value": 0,
        "gas": 50000,
        "gasPrice": w3.eth.gas_price,
        "chainId": settings.ETH_CHAIN_ID,
        "data": w3.to_hex(text=message)
    }

    signed_tx = w3.eth.account.sign_transaction(tx, settings.ETH_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)


def record_blockchain(db: Session, action: str, user_id: int, user_name: str, related_id: int, payload: dict):
    """记录区块链交易到数据库并返回 tx_hash"""
    tx_hash = push_to_blockchain(action, user_id, user_name, related_id, payload)
    record = BlockchainRecord(
        tx_hash=tx_hash,
        user_id=user_id,
        user_name=user_name,
        action=action,
        payload=payload
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record, tx_hash


# ---- 封装业务场景 ----
def record_file_upload(db: Session, file_id: int, user_id: int, user_name: str, file_hash: str, file_name: str, signature: str):
    payload = {
        "owner_id": user_id,
        "owner_name": user_name,
        "file_id": file_id,
        "file_name": file_name,
        "file_hash": file_hash,
        "signature": signature
    }
    _, tx_hash = record_blockchain(db, "upload", user_id, user_name, file_id, payload)
    return tx_hash


def record_request_submit(db: Session, request_id: int, requester_id: int, requester_name: str, owner_id: int, file_id: int):
    payload = {
        "request_id": request_id,
        "requester_id": requester_id,
        "requester_name": requester_name,
        "owner_id": owner_id,
        "file_id": file_id
    }
    _, tx_hash = record_blockchain(db, "request_submit", requester_id, requester_name, request_id, payload)
    return tx_hash


def record_request_approve(db: Session, request_id: int, owner_id: int, owner_name: str, status: str, encrypted_aes_key: str):
    payload = {
        "request_id": request_id,
        "owner_id": owner_id,
        "owner_name": owner_name,
        "status": status,
        "encrypted_aes_key": encrypted_aes_key
    }
    _, tx_hash = record_blockchain(db, "request_approve", owner_id, owner_name, request_id, payload)
    return tx_hash
