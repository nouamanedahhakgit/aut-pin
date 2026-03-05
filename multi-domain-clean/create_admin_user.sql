-- Create First Admin User
-- Run this after registering your first user through the web interface

-- Make the first user an admin
UPDATE users SET is_admin = 1, is_active = 1 WHERE id = 1;

-- Or create an admin user directly (password: "admin123" - CHANGE THIS!)
-- Password hash is SHA-256 of "admin123"
INSERT INTO users (username, password_hash, email, is_admin, is_active)
VALUES (
    'admin',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    'admin@example.com',
    1,
    1
);

-- Assign all existing domains to the admin user
INSERT INTO user_domains (user_id, domain_id)
SELECT 1, id FROM domains
WHERE NOT EXISTS (
    SELECT 1 FROM user_domains WHERE user_id = 1 AND domain_id = domains.id
);

-- View all users
SELECT id, username, email, is_admin, is_active, created_at FROM users;

-- View user domain assignments
SELECT 
    u.username,
    COUNT(ud.domain_id) as domain_count
FROM users u
LEFT JOIN user_domains ud ON ud.user_id = u.id
GROUP BY u.id, u.username;
