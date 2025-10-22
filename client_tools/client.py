import base64
import hashlib
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature, decode_dss_signature
)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# ========= Basic Utility Functions =========

def hash_file(filepath):
    """Compute SHA-256 hash of a file"""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.digest()

def save_pem_key(obj, filename, private=False):
    """Save PEM key to a file"""
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
    """Load PEM key from a file"""
    with open(filename, "rb") as f:
        data = f.read()
    if private:
        return serialization.load_pem_private_key(data, password=None, backend=default_backend())
    else:
        return serialization.load_pem_public_key(data, backend=default_backend())

def aes_encrypt_file(filepath):
    """Encrypt a file with AES and save the key separately"""
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    plaintext = open(filepath, "rb").read()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Save encrypted file
    orig_name = os.path.basename(filepath)
    enc_path = os.path.join(os.path.dirname(filepath), f"{orig_name}.enc")
    with open(enc_path, "wb") as f:
        f.write(iv + ciphertext)

    # Save AES key to a separate file
    aes_key_b64 = base64.b64encode(key).decode()
    aes_key_file = os.path.join(os.path.dirname(filepath), f"{orig_name}_aes_key.txt")
    with open(aes_key_file, "w") as f:
        f.write(aes_key_b64)

    return enc_path, aes_key_file

def aes_decrypt_file(enc_path, aes_key_b64):
    """Decrypt AES file and save as dec_<original_filename>"""
    aes_key = base64.b64decode(aes_key_b64)
    with open(enc_path, "rb") as f:
        iv = f.read(16)
        ciphertext = f.read()
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    orig_name = os.path.basename(enc_path)
    if orig_name.endswith(".enc"):
        orig_name = orig_name[:-4]
    out_path = os.path.join(os.path.dirname(enc_path), f"dec_{orig_name}")

    with open(out_path, "wb") as f:
        f.write(plaintext)
    return out_path

def ecc_encrypt(public_key, aes_key_b64):
    """Encrypt AES key with ECC public key"""
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
    """Decrypt AES key using ECC private key"""
    data = base64.b64decode(enc_data_b64)
    temp_pub_pem, encrypted = data.split(b"||", 1)
    temp_pub = serialization.load_pem_public_key(temp_pub_pem, backend=default_backend())
    shared = private_key.exchange(ec.ECDH(), temp_pub)
    derived = hashlib.sha256(shared).digest()
    decrypted = bytes(a ^ b for a, b in zip(encrypted, derived[:len(encrypted)]))
    return base64.b64encode(decrypted).decode()

def ecdsa_sign(private_key, file_path):
    """Sign a file using ECDSA"""
    file_hash = hash_file(file_path)
    sig = private_key.sign(file_hash, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(sig)
    signature = {"r": r, "s": s}
    sig_file = os.path.join(os.path.dirname(file_path), f"{os.path.basename(file_path)}_signature.json")
    json.dump(signature, open(sig_file, "w"))
    return signature, sig_file

def ecdsa_verify(public_key, file_path, signature_json):
    """Verify ECDSA signature"""
    sig_data = json.load(open(signature_json))
    der_sig = encode_dss_signature(sig_data["r"], sig_data["s"])
    file_hash = hash_file(file_path)
    try:
        public_key.verify(der_sig, file_hash, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False

# ========= GUI Application =========

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 File Security Tool (ECC + ECDSA + AES)")
        self.root.geometry("850x720")

        self.text = tk.Text(root, height=25, width=100)
        self.text.pack(pady=5)

        buttons = [
            ("Generate ECC Key Pair", self.gen_ecc_keys),
            ("Generate ECDSA Key Pair", self.gen_ecdsa_keys),
            ("Sign File", self.sign_file),
            ("Verify File", self.verify_file),
            ("Encrypt File (AES)", self.encrypt_file),
            ("Decrypt File (AES)", self.decrypt_file),
            ("Encrypt AES with ECC Public Key", self.ecc_encrypt_aes),
            ("Decrypt AES with ECC Private Key", self.ecc_decrypt_aes)
        ]

        for name, cmd in buttons:
            tk.Button(root, text=name, width=40, command=cmd).pack(pady=3)

    def log(self, msg):
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    def select_file(self, prompt="Select File"):
        path = filedialog.askopenfilename(title=prompt)
        if not path:
            messagebox.showerror("Error", f"{prompt} failed")
            return None
        self.log(f"📄 Selected file: {path}")
        return path

    def gen_ecc_keys(self):
        priv = ec.generate_private_key(ec.SECP256R1(), default_backend())
        pub = priv.public_key()
        save_pem_key(priv, "ecc_private.pem", True)
        save_pem_key(pub, "ecc_public.pem", False)
        self.log("✅ ECC key pair generated")

    def gen_ecdsa_keys(self):
        priv = ec.generate_private_key(ec.SECP256R1(), default_backend())
        pub = priv.public_key()
        save_pem_key(priv, "ecdsa_private.pem", True)
        save_pem_key(pub, "ecdsa_public.pem", False)
        self.log("✅ ECDSA key pair generated")

    def sign_file(self):
        file_path = self.select_file("Sign File")
        if not file_path:
            return
        priv_path = filedialog.askopenfilename(title="Select ECDSA Private Key (.pem)")
        if not priv_path:
            return
        priv = load_pem_key(priv_path, True)
        sig = ecdsa_sign(priv, file_path)
        self.log(f"✅ File signed: {sig}")

    def verify_file(self):
        file_path = self.select_file("Verify File")
        if not file_path:
            return
        pub_path = filedialog.askopenfilename(title="Select ECDSA Public Key (.pem)")
        sig_path = filedialog.askopenfilename(title="Select Signature File (.json)")
        pub = load_pem_key(pub_path, False)
        valid = ecdsa_verify(pub, file_path, sig_path)
        self.log("✅ Verification result: " + ("✔ Valid" if valid else "❌ Invalid"))

    def encrypt_file(self):
        file_path = self.select_file("Encrypt File")
        if not file_path:
            return
        enc_path, aes_key_file = aes_encrypt_file(file_path)
        aes_key_b64 = open(aes_key_file).read()
        self.log(f"✅ Encryption done: {enc_path}\n🔑 AES Key (base64) saved: {aes_key_file}\nAES Key: {aes_key_b64}")

    def decrypt_file(self):
        file_path = self.select_file("Decrypt File (.enc)")
        if not file_path:
            return
        aes_b64 = simpledialog.askstring("Enter AES Key", "Enter Base64 encoded AES key:")
        if not aes_b64:
            return
        out = aes_decrypt_file(file_path, aes_b64)
        self.log(f"✅ Decryption done: {out}")

    def ecc_encrypt_aes(self):
        pub_path = filedialog.askopenfilename(title="Select ECC Public Key (.pem)")
        pub = load_pem_key(pub_path, False)
        aes_b64 = simpledialog.askstring("AES Key Input", "Enter Base64 encoded AES key:")
        enc = ecc_encrypt(pub, aes_b64)
        open("aes_key.enc", "w").write(enc)
        self.log("✅ AES key encrypted -> aes_key.enc")

    def ecc_decrypt_aes(self):
        priv_path = filedialog.askopenfilename(title="Select ECC Private Key (.pem)")
        priv = load_pem_key(priv_path, True)
        enc_path = filedialog.askopenfilename(title="Select Encrypted AES Key File (aes_key.enc)")
        enc_b64 = open(enc_path).read()
        aes_b64 = ecc_decrypt(priv, enc_b64)
        self.log(f"✅ Decrypted AES Key (base64): {aes_b64}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
