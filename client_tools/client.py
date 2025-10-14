import base64
import hashlib
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature, decode_dss_signature
)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


# ========= 基础工具函数 =========

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.digest()


def save_pem_key(obj, filename, private=False):
    """保存 PEM 密钥文件"""
    if private:
        data = obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    else:
        data = obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    with open(filename, "wb") as f:
        f.write(data)


def load_pem_key(filename, private=False):
    """加载 PEM 密钥文件"""
    with open(filename, "rb") as f:
        data = f.read()
    if private:
        return serialization.load_pem_private_key(data, password=None, backend=default_backend())
    else:
        return serialization.load_pem_public_key(data, backend=default_backend())


def aes_encrypt_file(filepath):
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    plaintext = open(filepath, "rb").read()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # 输出加密文件名：enc_原文件名.enc
    orig_name = os.path.basename(filepath)
    enc_path = os.path.join(os.path.dirname(filepath), f"{orig_name}.enc")
    with open(enc_path, "wb") as f:
        f.write(iv + ciphertext)

    # 保存 AES Key 到独立文件：原文件名_aes_key.txt
    aes_key_b64 = base64.b64encode(key).decode()
    aes_key_file = os.path.join(os.path.dirname(filepath), f"{orig_name}_aes_key.txt")
    with open(aes_key_file, "w") as f:
        f.write(aes_key_b64)

    return enc_path, aes_key_file


def aes_decrypt_file(enc_path, aes_key_b64):
    """解密 AES 文件，输出文件名为 dec_原文件名，避免覆盖原文件"""
    aes_key = base64.b64decode(aes_key_b64)
    with open(enc_path, "rb") as f:
        iv = f.read(16)
        ciphertext = f.read()
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # 输出文件路径：dec_原文件名
    orig_name = os.path.basename(enc_path)
    if orig_name.endswith(".enc"):
        orig_name = orig_name[:-4]
    out_path = os.path.join(os.path.dirname(enc_path), f"dec_{orig_name}")

    # 以二进制写入，避免乱码
    with open(out_path, "wb") as f:
        f.write(plaintext)
    return out_path


def ecc_encrypt(public_key, aes_key_b64):
    """使用ECC公钥加密AES密钥"""
    aes_key = base64.b64decode(aes_key_b64)
    temp_priv = ec.generate_private_key(ec.SECP256R1(), default_backend())
    shared = temp_priv.exchange(ec.ECDH(), public_key)
    derived = hashlib.sha256(shared).digest()
    encrypted = bytes(a ^ b for a, b in zip(aes_key, derived[:len(aes_key)]))
    temp_pub_pem = temp_priv.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(temp_pub_pem + b"||" + encrypted).decode()


def ecc_decrypt(private_key, enc_data_b64):
    """使用ECC私钥解密AES密钥"""
    data = base64.b64decode(enc_data_b64)
    temp_pub_pem, encrypted = data.split(b"||", 1)
    temp_pub = serialization.load_pem_public_key(temp_pub_pem, backend=default_backend())
    shared = private_key.exchange(ec.ECDH(), temp_pub)
    derived = hashlib.sha256(shared).digest()
    decrypted = bytes(a ^ b for a, b in zip(encrypted, derived[:len(encrypted)]))
    return base64.b64encode(decrypted).decode()


def ecdsa_sign(private_key, file_path):
    file_hash = hash_file(file_path)
    sig = private_key.sign(file_hash, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(sig)
    signature = {"r": r, "s": s}

    sig_file = os.path.join(os.path.dirname(file_path), f"{os.path.basename(file_path)}_signature.json")
    json.dump(signature, open(sig_file, "w"))
    return signature, sig_file


def ecdsa_verify(public_key, file_path, signature_json):
    sig_data = json.load(open(signature_json))
    der_sig = encode_dss_signature(sig_data["r"], sig_data["s"])
    file_hash = hash_file(file_path)
    try:
        public_key.verify(der_sig, file_hash, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


# ========= GUI 主程序 =========

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 文件安全工具 (ECC + ECDSA + AES)")
        self.root.geometry("850x720")

        self.text = tk.Text(root, height=25, width=100)
        self.text.pack(pady=5)

        btns = [
            ("生成 ECC 密钥对", self.gen_ecc_keys),
            ("生成 ECDSA 密钥对", self.gen_ecdsa_keys),
            ("文件签名", self.sign_file),
            ("文件验签", self.verify_file),
            ("文件加密 (AES)", self.encrypt_file),
            ("文件解密 (AES)", self.decrypt_file),
            ("使用 ECC 公钥加密 AES", self.ecc_encrypt_aes),
            ("使用 ECC 私钥解密 AES", self.ecc_decrypt_aes)
        ]
        for name, cmd in btns:
            tk.Button(root, text=name, width=40, command=cmd).pack(pady=3)

    def log(self, msg):
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    def select_file(self, msg="选择文件"):
        path = filedialog.askopenfilename()
        if not path:
            messagebox.showerror("错误", f"{msg}失败")
            return None
        self.log(f"📄 选中文件: {path}")
        return path

    def gen_ecc_keys(self):
        priv = ec.generate_private_key(ec.SECP256R1(), default_backend())
        pub = priv.public_key()
        save_pem_key(priv, "ecc_private.pem", True)
        save_pem_key(pub, "ecc_public.pem", False)
        self.log("✅ ECC 密钥对已生成")

    def gen_ecdsa_keys(self):
        priv = ec.generate_private_key(ec.SECP256R1(), default_backend())
        pub = priv.public_key()
        save_pem_key(priv, "ecdsa_private.pem", True)
        save_pem_key(pub, "ecdsa_public.pem", False)
        self.log("✅ ECDSA 密钥对已生成")

    def sign_file(self):
        file_path = self.select_file("签名文件")
        if not file_path:
            return
        priv_path = filedialog.askopenfilename(title="选择 ECDSA 私钥 (.pem)")
        if not priv_path:
            return
        priv = load_pem_key(priv_path, True)
        sig = ecdsa_sign(priv, file_path)
        self.log(f"✅ 签名完成: {sig}")

    def verify_file(self):
        file_path = self.select_file("验签文件")
        if not file_path:
            return
        pub_path = filedialog.askopenfilename(title="选择 ECDSA 公钥 (.pem)")
        sig_path = filedialog.askopenfilename(title="选择签名文件 (signature.json)")
        pub = load_pem_key(pub_path, False)
        valid = ecdsa_verify(pub, file_path, sig_path)
        self.log("✅ 验签结果: " + ("✔ 有效" if valid else "❌ 无效"))

    def encrypt_file(self):
        file_path = self.select_file("加密文件")
        if not file_path:
            return
        enc_path, aes_key_file = aes_encrypt_file(file_path)
        # 读取 AES Key 并打印
        aes_key_b64 = open(aes_key_file).read()
        self.log(f"✅ 加密完成: {enc_path}\n🔑 AES Key(base64) 已保存: {aes_key_file}\n AES密钥为: {aes_key_b64}")

    def decrypt_file(self):
        file_path = self.select_file("解密文件 (.enc)")
        if not file_path:
            return
        aes_b64 = tk.simpledialog.askstring("输入AES密钥", "请输入Base64编码的AES密钥:")
        if not aes_b64:
            return
        out = aes_decrypt_file(file_path, aes_b64)
        self.log(f"✅ 解密完成: {out}")

    def ecc_encrypt_aes(self):
        pub_path = filedialog.askopenfilename(title="选择 ECC 公钥 (.pem)")
        pub = load_pem_key(pub_path, False)
        aes_b64 = tk.simpledialog.askstring("输入AES密钥", "请输入Base64编码的AES密钥:")
        enc = ecc_encrypt(pub, aes_b64)
        open("aes_key.enc", "w").write(enc)
        self.log("✅ AES密钥已加密 -> aes_key.enc")

    def ecc_decrypt_aes(self):
        priv_path = filedialog.askopenfilename(title="选择 ECC 私钥 (.pem)")
        priv = load_pem_key(priv_path, True)
        enc_path = filedialog.askopenfilename(title="选择加密AES文件 (aes_key.enc)")
        enc_b64 = open(enc_path).read()
        aes_b64 = ecc_decrypt(priv, enc_b64)
        self.log(f"✅ 解密得到 AES Key(base64): {aes_b64}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
