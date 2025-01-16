BEGIN;

-- Ensure pgcrypto extension is available
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Insert initial roles
INSERT INTO roles (name, description) VALUES
('admin', 'Organization administrator with full permissions'),
('user', 'Standard organization user with limited permissions'),
('viewer', 'Read-only access to organization data')
ON CONFLICT (name) DO NOTHING;

-- Insert initial users with bcrypt hashed passwords
-- admin123 hashed with bcrypt
INSERT INTO users (email, hashed_password, is_superuser, is_active) VALUES
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKxpCmGsSTwAgz.', TRUE, TRUE),
('user@example.com', '$2b$12$dWGj4.wOqgLrLxOAZCJTB.4IEK1.YQgLGZxwYn3WEtMxm6CkNS76.', FALSE, TRUE)
ON CONFLICT (email) DO UPDATE 
SET hashed_password = EXCLUDED.hashed_password,
    is_superuser = EXCLUDED.is_superuser,
    is_active = EXCLUDED.is_active;

-- Insert initial organization
INSERT INTO organizations (name, created_by) VALUES
('Example Organization', 1)
ON CONFLICT (name) DO NOTHING;

-- Assign users to organization
INSERT INTO user_organizations (user_id, organization_id) VALUES
(1, 1),
(2, 1)
ON CONFLICT (user_id, organization_id) DO NOTHING;

-- Assign roles to users
INSERT INTO user_roles (user_id, role_id) VALUES
(1, 1),  -- admin role for admin user
(2, 2)   -- user role for regular user
ON CONFLICT (user_id, role_id) DO NOTHING;

COMMIT;
