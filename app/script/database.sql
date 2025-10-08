
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    ecc_public_key TEXT NOT NULL,
    ecc_private_key TEXT NOT NULL,
    ecdsa_public_key TEXT NOT NULL,
    ecdsa_private_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    hash VARCHAR(64) NOT NULL,
    signature TEXT NOT NULL,           -- 文件签名（ECC）
    file_ecc_aes_key TEXT NOT NULL,    -- ECC加密后的AES密钥
    owner_id INT NOT NULL,
    owner_name VARCHAR(100),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    file_id INT NOT NULL,
    requester_id INT NOT NULL,
    owner_id INT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    owner_ecc_public_key TEXT,
    encrypted_aes_key TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

