
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    ecc_public_key TEXT NOT NULL,
    ecdsa_public_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    hash VARCHAR(64) NOT NULL,
    signature TEXT NOT NULL,           -- 文件签名（ECDSA），Base64(ASN.1 DER)
    file_ecc_aes_key TEXT NOT NULL,    -- ECIES封装后的AES密钥(JSON: ephemeral_pub_der_b64, nonce_b64, ciphertext_b64)
    owner_id INT NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    file_id INT NOT NULL,
    requester_id INT NOT NULL,
    owner_id INT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    owner_ecc_public_key TEXT,
    encrypted_aes_key TEXT,            -- 与 files.file_ecc_aes_key 同结构的 JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

