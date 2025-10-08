# app/core/crypto_local.py
from __future__ import annotations

import base64
import hashlib
from typing import Tuple

from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError


def generate_ecdsa_keypair() -> Tuple[str, str]:
    """
    生成 ECDSA SECP256k1 密钥对（PEM 格式字符串）
    返回: (private_pem, public_pem)
    """
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()
    return sk.to_pem().decode("utf-8"), vk.to_pem().decode("utf-8")


def sign_message(private_pem: str, data: bytes) -> str:
    """
    对 data 的 SHA-256 摘要做 ECDSA 签名。
    返回 base64 字符串（便于传输/存库）
    """
    digest = hashlib.sha256(data).digest()
    sk = SigningKey.from_pem(private_pem)
    signature = sk.sign_deterministic(digest)  # RFC6979，确定性签名
    return base64.b64encode(signature).decode("utf-8")


def verify_signature(public_pem: str, data: bytes, signature_b64: str) -> bool:
    """
    验证签名（base64）。
    """
    digest = hashlib.sha256(data).digest()
    sig = base64.b64decode(signature_b64)
    vk = VerifyingKey.from_pem(public_pem)
    try:
        return vk.verify(sig, digest)
    except BadSignatureError:
        return False
    # === AES-GCM (对称加密 / 解密) ===
from dataclasses import dataclass
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

@dataclass
class AesCiphertext:
    nonce_b64: str
    ciphertext_b64: str  # AESGCM 会把 auth tag 拼接在密文末尾

def generate_aes_key() -> str:
    """
    生成 256-bit AES 密钥，返回 Base64 字符串，便于存储/传输
    """
    key = os.urandom(32)  # 256-bit
    return base64.b64encode(key).decode("utf-8")

def aes_encrypt(key_b64: str, plaintext: bytes, aad: bytes | None = None) -> AesCiphertext:
    """
    使用 AES-GCM 加密。返回随机 12 字节 nonce 与密文（均为 base64）。
    可选 aad 作为附加认证数据（不加密但参与认证）。
    """
    key = base64.b64decode(key_b64)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 推荐 12 字节
    ct = aesgcm.encrypt(nonce, plaintext, aad)
    return AesCiphertext(
        nonce_b64=base64.b64encode(nonce).decode("utf-8"),
        ciphertext_b64=base64.b64encode(ct).decode("utf-8"),
    )

def aes_decrypt(key_b64: str, nonce_b64: str, ciphertext_b64: str, aad: bytes | None = None) -> bytes:
    """
    AES-GCM 解密。若认证失败（密文/nonce/aad 被篡改）会抛 InvalidTag 异常。
    """
    key = base64.b64decode(key_b64)
    nonce = base64.b64decode(nonce_b64)
    ct = base64.b64decode(ciphertext_b64)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, aad)


from pathlib import Path

def sign_file_path(private_pem: str, file_path: str) -> str:
    data = Path(file_path).read_bytes()
    return sign_message(private_pem, data)

def verify_file_path(public_pem: str, file_path: str, signature_b64: str) -> bool:
    data = Path(file_path).read_bytes()
    return verify_signature(public_pem, data, signature_b64)

def encrypt_file_path(file_path: str) -> dict:
    data = Path(file_path).read_bytes()
    aes_key_b64 = generate_aes_key()
    ct = aes_encrypt(aes_key_b64, data)
    # 默认把密文落盘为 .enc
    out = file_path + ".enc"
    Path(out).write_bytes(base64.b64decode(ct.ciphertext_b64))
    return {"aes_key_b64": aes_key_b64, "nonce_b64": ct.nonce_b64, "cipher_path": out}

def decrypt_file_path(cipher_path: str, aes_key_b64: str, nonce_b64: str, out_path: str|None=None) -> str:
    cipher_bytes = Path(cipher_path).read_bytes()
    plain = aes_decrypt(aes_key_b64, nonce_b64, base64.b64encode(cipher_bytes).decode())
    out_path = out_path or cipher_path.replace(".enc", "")
    Path(out_path).write_bytes(plain)
    return out_path
