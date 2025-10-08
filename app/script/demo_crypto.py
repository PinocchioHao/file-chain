# app/script/day3_demo_crypto.py
from app.core.crypto_local import (
    generate_ecdsa_keypair, sign_message, verify_signature,
    generate_aes_key, aes_encrypt, aes_decrypt
)

def main():
    # === 数据准备 ===
    plaintext = b"top secret data for file-chain day3"
    aad = b"file-chain:demo"  # 可选：把 user_id / file_id 放这里提升安全性

    # === AES-GCM 加密 / 解密 ===
    key_b64 = generate_aes_key()
    ct = aes_encrypt(key_b64, plaintext, aad=aad)
    recovered = aes_decrypt(key_b64, ct.nonce_b64, ct.ciphertext_b64, aad=aad)

    print("AES decrypted ok:", recovered == plaintext)
    # 打个摘要看下
    print("nonce_b64:", ct.nonce_b64)
    print("ciphertext_b64:", ct.ciphertext_b64[:40] + "...")

    # === ECDSA 签名 / 验签（对原文或指纹）===
    priv_pem, pub_pem = generate_ecdsa_keypair()
    sig_b64 = sign_message(priv_pem, recovered)   # 对解密后的明文签名（真实业务可对文件指纹签）
    ok = verify_signature(pub_pem, recovered, sig_b64)

    print("ECDSA verify:", ok)

    # === 篡改演示（应失败）===
    tampered = recovered + b"!"
    ok2 = verify_signature(pub_pem, tampered, sig_b64)
    print("verify after tamper:", ok2)

if __name__ == "__main__":
    main()