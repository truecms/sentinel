-- Sample data for dashboard demonstration
BEGIN;

-- Insert sample modules
INSERT INTO modules (machine_name, display_name, module_type, is_covered, is_active, created_at, updated_at) VALUES
('views', 'Views', 'core', true, true, NOW(), NOW()),
('node', 'Node', 'core', true, true, NOW(), NOW()),
('user', 'User', 'core', true, true, NOW(), NOW()),
('token', 'Token', 'contrib', true, true, NOW(), NOW()),
('pathauto', 'Pathauto', 'contrib', true, true, NOW(), NOW()),
('ctools', 'Chaos Tools', 'contrib', true, true, NOW(), NOW()),
('webform', 'Webform', 'contrib', true, true, NOW(), NOW()),
('admin_toolbar', 'Admin Toolbar', 'contrib', true, true, NOW(), NOW());

-- Get module IDs for versions
INSERT INTO module_versions (module_id, version_string, is_security_update, is_active, created_at, updated_at) 
SELECT m.id, v.version_string, v.is_security_update, v.is_active, NOW(), NOW()
FROM (VALUES 
    -- Views module versions
    ('views', '9.5.0', false, true),
    ('views', '9.5.1', true, true),
    ('views', '9.5.2', false, true),
    -- Node module versions  
    ('node', '10.1.0', false, true),
    ('node', '10.1.1', true, true),
    -- User module versions
    ('user', '10.1.0', false, true),
    ('user', '10.1.1', false, true),
    -- Token module versions
    ('token', '1.11.0', false, true),
    ('token', '1.12.0', true, true),
    ('token', '1.13.0', false, true),
    -- Pathauto versions
    ('pathauto', '1.11.0', false, true),
    ('pathauto', '1.12.0', false, true),
    -- CTools versions
    ('ctools', '4.0.3', false, true),
    ('ctools', '4.0.4', true, true),
    -- Webform versions
    ('webform', '6.2.0', false, true),
    ('webform', '6.2.1', true, true),
    ('webform', '6.2.2', false, true),
    -- Admin Toolbar versions
    ('admin_toolbar', '3.4.0', false, true),
    ('admin_toolbar', '3.4.1', false, true)
) AS v(machine_name, version_string, is_security_update, is_active)
JOIN modules m ON m.machine_name = v.machine_name;

-- Insert sample sites
INSERT INTO sites (name, url, site_uuid, api_token, drupal_core_version, is_active, created_at, updated_at, organization_id) VALUES
('Main Corporate Site', 'https://example.com', 'site-uuid-1', 'token-1', '10.1.0', true, NOW(), NOW(), 1),
('Marketing Site', 'https://marketing.example.com', 'site-uuid-2', 'token-2', '10.1.0', true, NOW(), NOW(), 1),
('Support Portal', 'https://support.example.com', 'site-uuid-3', 'token-3', '9.5.0', true, NOW(), NOW(), 1),
('Blog Site', 'https://blog.example.com', 'site-uuid-4', 'token-4', '10.1.0', true, NOW(), NOW(), 2),
('E-commerce Site', 'https://shop.example.com', 'site-uuid-5', 'token-5', '10.1.0', true, NOW(), NOW(), 2);

-- Insert sample site modules with realistic version mappings
INSERT INTO site_modules (site_id, module_id, current_version_id, latest_version_id, enabled, update_available, security_update_available, created_at, updated_at)
SELECT s.id, m.id, 
       cv.id as current_version_id, 
       lv.id as latest_version_id,
       sm.enabled, sm.update_available, sm.security_update_available,
       NOW(), NOW()
FROM (VALUES
    -- Main Corporate Site
    ('site-uuid-1', 'views', '9.5.0', '9.5.2', true, true, true),
    ('site-uuid-1', 'node', '10.1.0', '10.1.1', true, true, true),
    ('site-uuid-1', 'user', '10.1.0', '10.1.1', true, true, false),
    ('site-uuid-1', 'token', '1.11.0', '1.13.0', true, true, true),
    ('site-uuid-1', 'pathauto', '1.11.0', '1.12.0', true, true, false),
    
    -- Marketing Site
    ('site-uuid-2', 'views', '9.5.1', '9.5.2', true, true, true),
    ('site-uuid-2', 'node', '10.1.0', '10.1.1', true, true, true),
    ('site-uuid-2', 'token', '1.11.0', '1.13.0', true, true, true),
    ('site-uuid-2', 'ctools', '4.0.3', '4.0.4', true, true, true),
    ('site-uuid-2', 'webform', '6.2.0', '6.2.2', true, true, true),
    
    -- Support Portal
    ('site-uuid-3', 'views', '9.5.0', '9.5.2', true, true, true),
    ('site-uuid-3', 'user', '10.1.0', '10.1.1', true, true, false),
    ('site-uuid-3', 'token', '1.12.0', '1.13.0', true, true, false),
    ('site-uuid-3', 'admin_toolbar', '3.4.0', '3.4.1', true, true, false),
    
    -- Blog Site (mostly up to date)
    ('site-uuid-4', 'views', '9.5.2', '9.5.2', true, false, false),
    ('site-uuid-4', 'node', '10.1.1', '10.1.1', true, false, false),
    ('site-uuid-4', 'user', '10.1.1', '10.1.1', true, false, false),
    ('site-uuid-4', 'webform', '6.2.1', '6.2.2', true, true, true),
    
    -- E-commerce Site
    ('site-uuid-5', 'views', '9.5.0', '9.5.2', true, true, true),
    ('site-uuid-5', 'node', '10.1.0', '10.1.1', true, true, true),
    ('site-uuid-5', 'token', '1.11.0', '1.13.0', true, true, true),
    ('site-uuid-5', 'ctools', '4.0.3', '4.0.4', true, true, true),
    ('site-uuid-5', 'webform', '6.2.0', '6.2.2', true, true, true),
    ('site-uuid-5', 'admin_toolbar', '3.4.0', '3.4.1', true, true, false)
) AS sm(site_uuid, module_machine_name, current_version, latest_version, enabled, update_available, security_update_available)
JOIN sites s ON s.site_uuid = sm.site_uuid
JOIN modules m ON m.machine_name = sm.module_machine_name
JOIN module_versions cv ON cv.module_id = m.id AND cv.version_string = sm.current_version
JOIN module_versions lv ON lv.module_id = m.id AND lv.version_string = sm.latest_version;

COMMIT;