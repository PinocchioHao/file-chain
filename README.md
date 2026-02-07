# 🔐 File-Chain: Blockchain-Integrated Secure File Management

**File-Chain** is a high-security file storage and sharing platform that integrates **Blockchain audit trails** with **End-to-End Encryption (E2EE)**. The project is designed to address data privacy in cloud storage and ensure the absolute traceability of access behaviors.

---

## 📖 Project Overview

By implementing a hybrid architecture of "Client-side Cryptography + Cloud Ciphertext Storage + Distributed Ledger Auditing," the project ensures security throughout the file lifecycle:

* **Dual-Layer Encryption**: Utilizes **AES-256 (Symmetric)** for file content and **ECC (Asymmetric)** for secure key exchange, ensuring data remains unreadable even if the cloud provider is compromised.
* **On-Chain Audit Trail**: Critical operations—including uploads, access requests, and approvals—are recorded in real-time on the **Ethereum Sepolia** testnet, providing a transparent and immutable history.
* **Local-First Security**: Adheres to the **"Zero-Knowledge"** principle; all decryption, digital signing (ECDSA), and key management occur strictly on the client side.
* **Hybrid Storage**: Files are stored as encrypted blobs on **AWS EC2**, balancing the high performance of cloud infrastructure with the decentralized trust of blockchain.

---

## 📸 System Demo & Screenshots

### Web Cloud Interface

<p align="left">
<img src="docs/screenshots/fc1.png" width="32%" />
<img src="docs/screenshots/fc2.png" width="32%" />
<img src="docs/screenshots/fc3.png" width="32%" />
<img src="docs/screenshots/fc4.png" width="32%" />
<img src="docs/screenshots/fc5.png" width="32%" />
<img src="docs/screenshots/fc6.png" width="32%" />
<img src="docs/screenshots/fc8.png" width="32%" />
</p>

### Local Client Application

<p align="left">
<img src="docs/screenshots/fc7.png" width="32%" />
</p>

### Sepolia Blockchain Records

<p align="left">
<img src="docs/screenshots/fc9.png" width="32%" />
</p>

---

## ⚙️ Tech Stack

* **Backend**: FastAPI (Python Asynchronous Framework)
* **Cryptography**: AES-256, ECC, ECDSA Digital Signatures
* **Web3/Blockchain**: Web3.py, Sepolia Testnet
* **Infrastructure**: AWS EC2, MySQL 8.0
* **Client**: Python-based cryptographic toolkit (PyCryptodome)

---

## 📌 Core Workflow

### 1. Key Generation & Account Binding

Users generate **ECC key pairs** (for key exchange) and **ECDSA key pairs** (for identity signing) via the local client. The **Public Keys** are submitted during registration, while **Private Keys are stored exclusively on the user's local machine**.

### 2. Secure File Upload

* **Sign & Encrypt**: The client signs the file using ECDSA and encrypts it with a random AES key. This AES key is then "wrapped" using the owner's public key.
* **Cloud Storage**: The encrypted ciphertext is uploaded to AWS EC2.
* **On-Chain Evidence**: Upon successful upload, the system automatically records the file metadata and hash on the blockchain.

### 3. Authorized Sharing Mechanism

* **Access Request**: A recipient browses the file and submits a request, which is logged on the Sepolia testnet.
* **Owner Approval**: The owner retrieves the recipient's ECC public key and re-encrypts the file's AES key locally.
* **Key Distribution**: The re-wrapped key is sent back via the system; the recipient uses their local private key to unwrap the AES key and restore the file.

---

## 📂 Project Structure

```bash
file-chain/
├─ client_tools/             # [Client] Local key management, signing, and crypto logic
│  └─ client.py              # GUI/CLI Entry point
├─ app/                      # [Server] FastAPI backend core
│  ├─ api/                   # API Routes: Auth, Files, Blockchain, Requests
│  ├─ core/                  # Security configs, JWT, and global settings
│  ├─ models/                # SQLAlchemy ORM models
│  ├─ schemas/               # Pydantic data validation models
│  └─ services/              # Business logic: File processing & Blockchain interaction
├─ script/                   # Database initialization scripts
├─ uploads/                  # Local storage for encrypted ciphertext
└─ requirements.txt          # Project dependencies

```

---

## 🌐 Quick Start & Deployment

### 1. Database Initialization

Execute the SQL script to set up the MySQL schema:

```bash
mysql -u your_username -p your_database < app/script/database.sql

```

### 2. Backend Setup

Install dependencies and launch the FastAPI server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload 

```

### 3. Frontend Integration

This project requires a frontend interface to function fully. Please refer to the repository below for setup instructions:
👉 **[File-Chain Frontend Project](https://github.com/PinocchioHao/file-chain-front)**

### 4. Client Tool Usage

Run the local client for cryptographic operations:

```bash
cd client_tools
python client.py

```

---

## ⚠️ Security Disclaimer

**Private Key Protection**: This project strictly separates client and server responsibilities. Private keys are used only for local cryptographic operations and are **NEVER uploaded to the server**. Users are responsible for backing up their local key files; if lost, the corresponding encrypted data cannot be recovered.

---
