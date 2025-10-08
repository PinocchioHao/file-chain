⚙️ 与后端的集成流程
上传流程（加密+签名）

用户选择文件；

系统执行：

sig_b64 = sign_message(private_pem, file_bytes)
aes_key_b64 = generate_aes_key()
ct = aes_encrypt(aes_key_b64, file_bytes)


将密文文件（ct.ciphertext_b64）上传至 AWS 或本地 uploads/；

将以下元信息写入数据库或区块链：

{
  "hash_algo": "SHA-256",
  "sig_b64": "<签名>",
  "nonce_b64": "<AES随机数>",
  "alg": "AES-256-GCM"
}

下载与验证流程（解密+验签）

从数据库/区块链读取密文和元信息；

当访问申请被批准后，申请者获得加密的 AES 密钥；

本地执行：

plaintext = aes_decrypt(aes_key_b64, nonce_b64, ciphertext_b64)
verify_signature(uploader_pub_pem, plaintext, sig_b64)


如果返回 True，说明文件来源可信且内容未被篡改。

🧩 文件路径级辅助函数（可选）

模块中还提供了便捷的文件操作封装：

sign_file_path(private_pem, "file.txt")
encrypt_file_path("file.txt")
decrypt_file_path("file.txt.enc", aes_key_b64, nonce_b64)
verify_file_path(public_pem, "file.txt", sig_b64)


这些函数会自动读取/写入文件，方便测试和演示。

🗄️ 需保存至数据库或区块链的字段
字段名	含义
sig_b64	Base64 格式的 ECDSA 签名
hash_algo	哈希算法（SHA-256）
nonce_b64	AES-GCM 随机数
alg	加密算法（AES-256-GCM）
uploader_pub_fingerprint	可选：上传者公钥指纹或链上引用