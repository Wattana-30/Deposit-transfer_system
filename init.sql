CREATE DATABASE IF NOT EXISTS banking_db;

USE banking_db;

-- ตารางผู้ใช้
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

-- ตารางธุรกรรม
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    target_user_id INT NULL, -- ฟิลด์นี้บันทึกข้อมูลผู้ใช้ที่รับเงินในกรณีโอนเงิน
    transaction_type ENUM('deposit', 'withdraw', 'transfer') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    direction ENUM('inbound', 'outbound') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (target_user_id) REFERENCES users(id) -- ความสัมพันธ์กับผู้ใช้ที่รับโอนเงิน
);
