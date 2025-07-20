-- Sample data for testing
-- This file is used in CI/CD to populate test database with realistic data
BEGIN;

-- Insert test organization
INSERT INTO organizations (id, name, is_active, is_deleted, created_at, updated_at, created_by, updated_by) VALUES
(1, 'Test Organization', true, false, NOW(), NOW(), 1, 1);

-- Insert sample modules with timestamps
INSERT INTO modules (machine_name, display_name, module_type, is_covered, is_active, is_deleted, created_at, updated_at, created_by, updated_by) VALUES
('views', 'Views', 'core', true, true, false, NOW(), NOW(), 1, 1),
('node', 'Node', 'core', true, true, false, NOW(), NOW(), 1, 1),
('user', 'User', 'core', true, true, false, NOW(), NOW(), 1, 1),
('system', 'System', 'core', true, true, false, NOW(), NOW(), 1, 1),
('webform', 'Webform', 'contrib', true, true, false, NOW(), NOW(), 1, 1),
('pathauto', 'Pathauto', 'contrib', true, true, false, NOW(), NOW(), 1, 1),
('token', 'Token', 'contrib', true, true, false, NOW(), NOW(), 1, 1),
('metatag', 'Metatag', 'contrib', true, true, false, NOW(), NOW(), 1, 1),
('custom_auth', 'Custom Authentication', 'custom', true, true, false, NOW(), NOW(), 1, 1);

-- Get module IDs and insert versions with proper timestamps
INSERT INTO module_versions (module_id, version_string, is_security_update, is_deleted, release_date, created_at, updated_at, created_by, updated_by) VALUES
-- Core modules - all up to date
((SELECT id FROM modules WHERE machine_name = 'views'), '10.1.0', false, false, '2023-06-01', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'node'), '10.1.0', false, false, '2023-06-01', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'user'), '10.1.0', false, false, '2023-06-01', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'system'), '10.1.0', false, false, '2023-06-01', NOW(), NOW(), 1, 1),
-- Contrib modules with various versions
((SELECT id FROM modules WHERE machine_name = 'webform'), '6.0.3', false, false, '2023-07-15', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'webform'), '6.0.4', false, false, '2023-08-01', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'webform'), '6.0.5', true, false, '2023-08-15', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'pathauto'), '1.0.2', false, false, '2023-06-01', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'pathauto'), '1.0.3', true, false, '2023-08-01', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'token'), '1.0.11', false, false, '2023-07-01', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'metatag'), '2.0.14', false, false, '2023-06-01', NOW(), NOW(), 1, 1),
((SELECT id FROM modules WHERE machine_name = 'metatag'), '2.0.15', true, false, '2023-08-10', NOW(), NOW(), 1, 1),
-- Custom modules
((SELECT id FROM modules WHERE machine_name = 'custom_auth'), '1.0.0', false, false, '2023-01-01', NOW(), NOW(), 1, 1);

-- Insert sites for testing organization (ID=1)
INSERT INTO sites (name, url, organization_id, security_score, total_modules_count, security_updates_count, non_security_updates_count, is_active, is_deleted, created_at, updated_at, created_by, updated_by) VALUES
('Test Production Site', 'https://production.test.com/', 1, 92, 9, 0, 2, true, false, NOW(), NOW(), 1, 1),
('Test Staging Site', 'https://staging.test.com/', 1, 78, 9, 2, 3, true, false, NOW(), NOW(), 1, 1),
('Test Development Site', 'https://dev.test.com/', 1, 65, 9, 3, 4, true, false, NOW(), NOW(), 1, 1);

-- Insert site modules for Test Production Site
INSERT INTO site_modules (site_id, module_id, current_version_id, enabled, update_available, security_update_available, created_at, updated_at, created_by, updated_by) VALUES
-- Core modules (all up to date)
((SELECT id FROM sites WHERE name = 'Test Production Site'), (SELECT id FROM modules WHERE machine_name = 'views'), 
 (SELECT id FROM module_versions WHERE module_id = (SELECT id FROM modules WHERE machine_name = 'views') AND version_string = '10.1.0'), 
 true, false, false, NOW(), NOW(), 1, 1),
((SELECT id FROM sites WHERE name = 'Test Production Site'), (SELECT id FROM modules WHERE machine_name = 'node'), 
 (SELECT id FROM module_versions WHERE module_id = (SELECT id FROM modules WHERE machine_name = 'node') AND version_string = '10.1.0'), 
 true, false, false, NOW(), NOW(), 1, 1),
-- Contrib modules (some updates available)
((SELECT id FROM sites WHERE name = 'Test Production Site'), (SELECT id FROM modules WHERE machine_name = 'webform'), 
 (SELECT id FROM module_versions WHERE module_id = (SELECT id FROM modules WHERE machine_name = 'webform') AND version_string = '6.0.4'), 
 true, true, false, NOW(), NOW(), 1, 1),  -- Has non-security update available
((SELECT id FROM sites WHERE name = 'Test Production Site'), (SELECT id FROM modules WHERE machine_name = 'pathauto'), 
 (SELECT id FROM module_versions WHERE module_id = (SELECT id FROM modules WHERE machine_name = 'pathauto') AND version_string = '1.0.3'), 
 true, false, false, NOW(), NOW(), 1, 1); -- Latest version

-- Insert site modules for Test Staging Site
INSERT INTO site_modules (site_id, module_id, current_version_id, enabled, update_available, security_update_available, created_at, updated_at, created_by, updated_by) VALUES
((SELECT id FROM sites WHERE name = 'Test Staging Site'), (SELECT id FROM modules WHERE machine_name = 'webform'), 
 (SELECT id FROM module_versions WHERE module_id = (SELECT id FROM modules WHERE machine_name = 'webform') AND version_string = '6.0.3'), 
 true, true, true, NOW(), NOW(), 1, 1),  -- Has security update available
((SELECT id FROM sites WHERE name = 'Test Staging Site'), (SELECT id FROM modules WHERE machine_name = 'pathauto'), 
 (SELECT id FROM module_versions WHERE module_id = (SELECT id FROM modules WHERE machine_name = 'pathauto') AND version_string = '1.0.2'), 
 true, true, true, NOW(), NOW(), 1, 1);  -- Has security update available

-- Insert site modules for Test Development Site
INSERT INTO site_modules (site_id, module_id, current_version_id, enabled, update_available, security_update_available, created_at, updated_at, created_by, updated_by) VALUES
((SELECT id FROM sites WHERE name = 'Test Development Site'), (SELECT id FROM modules WHERE machine_name = 'webform'), 
 (SELECT id FROM module_versions WHERE module_id = (SELECT id FROM modules WHERE machine_name = 'webform') AND version_string = '6.0.3'), 
 true, true, true, NOW(), NOW(), 1, 1),  -- Has security update available
((SELECT id FROM sites WHERE name = 'Test Development Site'), (SELECT id FROM modules WHERE machine_name = 'metatag'), 
 (SELECT id FROM module_versions WHERE module_id = (SELECT id FROM modules WHERE machine_name = 'metatag') AND version_string = '2.0.14'), 
 true, true, true, NOW(), NOW(), 1, 1);  -- Has security update available

COMMIT;