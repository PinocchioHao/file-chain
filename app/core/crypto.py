# app/core/crypto.py
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature  # 保留原有导入，避免影响其他文件
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os
import base64

# TODO 相关加密逻辑未实现或有bug未调通（已实现：ECC/ECDSA生成与序列化、签名/验签、AES-GCM、简化ECIES封装）

def generate_ecc_keypair():
    """生成 ECC 私钥 + 公钥（保持原曲线 SECP256R1，不改动你们设定）"""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_private_key(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

def serialize_private_key_der_b64(private_key):
    """将私钥序列化为 DER 后再做 Base64，便于存入较短的字符串字段。"""
    der_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return base64.b64encode(der_bytes).decode()

def serialize_public_key_der_b64(public_key):
    """将公钥序列化为 DER 后再做 Base64，便于存入较短的字符串字段。"""
    der_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return base64.b64encode(der_bytes).decode()

def sign_data(private_key, data: bytes):
    """
    使用 ECDSA(SHA-256) 对数据签名。
    返回 cryptography 默认的 DER 编码签名（r、s 已封装）。
    """
    signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    return signature

# ===== 下面是可选工具函数：不影响现有调用，按需使用 =====

def verify_signature(public_key, data: bytes, signature: bytes) -> bool:
    """
    验证 ECDSA 签名（DER 编码）。验证通过返回 True，否则 False。
    """
    try:
        public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

def load_private_key_from_pem(pem_str: str):
    """从PEM字符串加载私钥（如从数据库读取后需要还原为对象）"""
    return serialization.load_pem_private_key(pem_str.encode(), password=None)

def load_public_key_from_pem(pem_str: str):
    """从PEM字符串加载公钥"""
    return serialization.load_pem_public_key(pem_str.encode())

def load_private_key_from_der_b64(b64_str: str):
    """从 Base64(DER) 字符串恢复私钥对象。"""
    der_bytes = base64.b64decode(b64_str.encode())
    return serialization.load_der_private_key(der_bytes, password=None)

def load_public_key_from_der_b64(b64_str: str):
    """从 Base64(DER) 字符串恢复公钥对象。"""
    der_bytes = base64.b64decode(b64_str.encode())
    return serialization.load_der_public_key(der_bytes)

# ===== 对称加密：AES-GCM =====

def aes_gcm_encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    """使用 AES-GCM 加密，返回 (nonce, ciphertext)。ciphertext 已包含 GCM tag。"""
    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must be 128/192/256-bit")
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    return nonce, ciphertext

def aes_gcm_decrypt(nonce: bytes, ciphertext: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None)

# ===== ECIES（简化版）：用接收方 ECC 公钥封装对称密钥 =====

def ecies_encrypt_for_public_key(recipient_public_key, data: bytes) -> dict:
    """
    使用 ECDH + HKDF(SHA-256) 派生 256-bit 密钥，然后用 AES-GCM 加密 data。
    返回包含临时公钥、nonce、ciphertext 的字典（全部 base64）。
    接收方用自己的 ECC 私钥 + 临时公钥即可解封。
    """
    # 1) 生成临时密钥对
    ephemeral_private = ec.generate_private_key(ec.SECP256R1())
    ephemeral_public = ephemeral_private.public_key()

    # 2) ECDH 共享密钥
    shared_secret = ephemeral_private.exchange(ec.ECDH(), recipient_public_key)

    # 3) HKDF 派生对称密钥
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"file-chain-ecies",
    )
    aes_key = hkdf.derive(shared_secret)

    # 4) AES-GCM 加密数据
    nonce, ciphertext = aes_gcm_encrypt(data, aes_key)

    return {
        "ephemeral_pub_der_b64": serialize_public_key_der_b64(ephemeral_public),
        "nonce_b64": base64.b64encode(nonce).decode(),
        "ciphertext_b64": base64.b64encode(ciphertext).decode(),
    }
