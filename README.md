
# File-Chain Project Documentation

## 📖 Overview

**File-Chain** is a secure file storage and sharing platform that combines **blockchain** and **cryptographic technologies**.

* The project ensures **security, traceability, and tamper-resistance** throughout the entire file lifecycle — including **uploading, storing, sharing, and access approval**.
* **AES (symmetric encryption)** is used for file content encryption, and **ECDSA (digital signature)** is used for signing and verification.
* Each file’s AES key is encrypted with the user’s **ECC public key**, ensuring secure key exchange.
* **Blockchain** records key actions such as file uploads, access requests, and approvals — providing transparency and immutability.
* Files are physically stored on **AWS EC2**, while **decryption, verification, and key management** occur locally on the client side — balancing **performance and security**.

---

## 📌 Workflow

### 1. Key Generation on the Client

* Users use the **client program** (`client_tools/client.py`) to generate:

  * **ECC key pair** – for encrypting/decrypting AES keys.
  * **ECDSA key pair** – for signing and verifying files.
* The **private key** is used locally by the user for encryption and decryption operations and must be stored securely.
* The **public key** is used for interactions with the platform (e.g., encryption and verification).

### 2. User Registration & Login

* Users register **online** in the system and submit their **ECC/ECDSA public keys**.
* After logging in, users can view, upload, download, and request access to files.

### 3. File Operations

* Using the client program, users can perform:

  * **File signing** (ECDSA)
  * **File encryption/decryption** (AES)
  * **AES key encryption/decryption** (ECC)
* Encrypted files and their corresponding signatures can then be uploaded to the platform.

### 4. File Access & Request Process

* Users can browse available files on the platform, download their own files, or **submit access requests** for others’ files.
* File owners can **approve or reject** incoming requests:

  * **Approve** → The owner retrieves the requester’s ECC public key via the online system, uses the client to encrypt the AES key locally, and then sends it back through the system.
  * **Reject** → The request is closed.
* Once approved, the requester can decrypt the AES key locally and use it to decrypt the file content.

### 5. Blockchain Integration

* The following operations are **recorded on the Sepolia testnet blockchain**:

  * Successful file uploads
  * File access requests
  * Approval or rejection of requests
* After each blockchain transaction, users can view related information via a popup in the system:

  * Search and filter blockchain records by condition
  * View detailed record data
  * Jump directly to the **Sepolia Etherscan** page for transaction verification

> ⚠️ Private keys are **never uploaded** to the server. They are stored locally and only used within the client application to ensure maximum security.

---

## 📂 Project Structure

```bash
file-chain
├─ requirements.txt          # Project dependencies
├─ uploads                   # Local directory for uploaded files
├─ client_tools              # Local client application
│  └─ client.py              # GUI/CLI client for key generation, signing, verification, AES/ECC encryption & decryption
└─ app
   ├─ db.py                  # Database connection and session management
   ├─ main.py                # Project entry point (FastAPI application)
   │
   ├─ api                    # API layer for request routing
   │  ├─ auth.py             # Login, registration, and JWT authentication endpoints
   │  ├─ file.py             # File upload and query endpoints
   │  ├─ blockchain.py       # Blockchain query endpoints
   │  └─ request.py          # File access request and approval endpoints
   │
   ├─ core                   # Core utilities and configuration
   │  ├─ config.py           # Global settings (DB, keys, etc.)
   │  └─ security.py         # JWT handling and authentication
   │
   ├─ models                 # ORM models (database table mapping)
   │  ├─ file.py             # File table definition
   │  ├─ blockchain.py       # Blockchain record table
   │  ├─ request.py          # File request table
   │  └─ user.py             # User table definition
   │
   ├─ schemas                # Pydantic schemas for request/response validation
   │  ├─ file.py             # File-related schemas
   │  ├─ blockchain.py       # Blockchain-related schemas
   │  ├─ request.py          # Request-related schemas
   │  └─ user.py             # User-related schemas
   │
   ├─ script                 
   │  └─ database.sql        # Database initialization script
   │
   └─ services               # Business logic layer
      ├─ file_service.py        # File upload and query logic
      ├─ request_service.py     # Request submission and approval logic
      ├─ blockchain_service.py  # Blockchain recording and query logic
      └─ user_service.py        # User registration and login logic
```
