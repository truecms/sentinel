-- Simple sample data for dashboard demonstration
BEGIN;

-- Insert sample sites first
INSERT INTO sites (name, url, site_uuid, api_token, drupal_core_version, is_active, created_at, updated_at, organization_id) VALUES
('Main Corporate Site', 'https://example.com', 'site-uuid-1', 'token-1', '10.1.0', true, NOW(), NOW(), 1),
('Marketing Site', 'https://marketing.example.com', 'site-uuid-2', 'token-2', '10.1.0', true, NOW(), NOW(), 1),
('Support Portal', 'https://support.example.com', 'site-uuid-3', 'token-3', '9.5.0', true, NOW(), NOW(), 1),
('Blog Site', 'https://blog.example.com', 'site-uuid-4', 'token-4', '10.1.0', true, NOW(), NOW(), 2),
('E-commerce Site', 'https://shop.example.com', 'site-uuid-5', 'token-5', '10.1.0', true, NOW(), NOW(), 2);

-- Insert more sample modules
INSERT INTO modules (machine_name, display_name, module_type, is_covered, is_active, created_at, updated_at) VALUES
('node', 'Node', 'core', true, true, NOW(), NOW()),
('user', 'User', 'core', true, true, NOW(), NOW()),
('token', 'Token', 'contrib', true, true, NOW(), NOW()),
('pathauto', 'Pathauto', 'contrib', true, true, NOW(), NOW()),
('ctools', 'Chaos Tools', 'contrib', true, true, NOW(), NOW()),
('webform', 'Webform', 'contrib', true, true, NOW(), NOW()),
('admin_toolbar', 'Admin Toolbar', 'contrib', true, true, NOW(), NOW());

COMMIT;