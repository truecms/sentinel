-- Comprehensive sample data for monitoring platform
-- This creates a realistic dataset with 8 sites and 12 modules
-- Designed to show ~62.5% compliance rate with critical issues

BEGIN;

-- Clear existing data
DELETE FROM site_modules;
DELETE FROM module_versions;
DELETE FROM sites;
DELETE FROM modules;

-- Insert sample modules with Drupal core and contrib modules only
INSERT INTO modules (machine_name, display_name, module_type, is_covered, is_active, created_at, updated_at) VALUES
('drupal', 'Drupal Core', 'core', true, true, NOW(), NOW()),
('token', 'Token', 'contrib', true, true, NOW(), NOW()),
('pathauto', 'Pathauto', 'contrib', true, true, NOW(), NOW()),
('ctools', 'Chaos Tools', 'contrib', true, true, NOW(), NOW()),
('webform', 'Webform', 'contrib', true, true, NOW(), NOW()),
('admin_toolbar', 'Admin Toolbar', 'contrib', true, true, NOW(), NOW()),
('paragraphs', 'Paragraphs', 'contrib', true, true, NOW(), NOW()),
('entity_reference_revisions', 'Entity Reference Revisions', 'contrib', true, true, NOW(), NOW()),
('field_group', 'Field Group', 'contrib', true, true, NOW(), NOW()),
('views_bulk_operations', 'Views Bulk Operations', 'contrib', true, true, NOW(), NOW()),
('metatag', 'Metatag', 'contrib', true, true, NOW(), NOW()),
('redirect', 'Redirect', 'contrib', true, true, NOW(), NOW());

-- Insert comprehensive module versions with security updates
INSERT INTO module_versions (module_id, version_string, is_security_update, is_active, created_at, updated_at) 
SELECT m.id, v.version_string, v.is_security_update, v.is_active, NOW(), NOW()
FROM (VALUES 
    -- Drupal Core versions (supporting both 10.x and 11.x)
    ('drupal', '10.0.0', false, true),
    ('drupal', '10.1.0', false, true),
    ('drupal', '10.1.1', true, true),   -- Security update
    ('drupal', '10.1.2', true, true),   -- Latest 10.1.x
    ('drupal', '10.2.0', false, true),
    ('drupal', '10.2.1', true, true),   -- Security update
    ('drupal', '10.2.2', true, true),   -- Latest 10.2.x
    ('drupal', '11.0.0', false, true),
    ('drupal', '11.0.1', true, true),   -- Latest 11.x with security
    
    -- Token module versions (critical security issue)
    ('token', '1.11.0', false, true),
    ('token', '1.12.0', true, true),  -- Security update
    ('token', '1.13.0', false, true),
    ('token', '1.13.1', true, true),  -- Latest with security fix
    
    -- Pathauto versions
    ('pathauto', '1.11.0', false, true),
    ('pathauto', '1.12.0', false, true), -- Latest
    
    -- CTools versions (high priority security)
    ('ctools', '4.0.3', false, true),
    ('ctools', '4.0.4', true, true),  -- Security update
    ('ctools', '4.0.5', false, true), -- Latest
    
    -- Webform versions (critical security issue)
    ('webform', '6.2.0', false, true),
    ('webform', '6.2.1', true, true),  -- Security update
    ('webform', '6.2.2', false, true),
    ('webform', '6.2.3', true, true),  -- Latest with security fix
    
    -- Admin Toolbar versions
    ('admin_toolbar', '3.4.0', false, true),
    ('admin_toolbar', '3.4.1', false, true), -- Latest
    
    -- Paragraphs versions
    ('paragraphs', '1.15.0', false, true),
    ('paragraphs', '1.16.0', false, true), -- Latest
    
    -- Entity Reference Revisions
    ('entity_reference_revisions', '1.10.0', false, true),
    ('entity_reference_revisions', '1.11.0', false, true), -- Latest
    
    -- Field Group versions  
    ('field_group', '3.4.0', false, true),
    ('field_group', '3.4.1', false, true), -- Latest
    
    -- Views Bulk Operations versions (security issue)
    ('views_bulk_operations', '4.2.0', false, true),
    ('views_bulk_operations', '4.2.1', true, true),  -- Security update
    ('views_bulk_operations', '4.2.2', true, true),  -- Latest with security fix
    
    -- Metatag versions
    ('metatag', '1.25.0', false, true),
    ('metatag', '1.26.0', false, true), -- Latest
    
    -- Redirect versions (security issue)
    ('redirect', '1.8.0', false, true),
    ('redirect', '1.8.1', true, true),  -- Security update
    ('redirect', '1.9.0', true, true)   -- Latest with security fix
) AS v(machine_name, version_string, is_security_update, is_active)
JOIN modules m ON m.machine_name = v.machine_name;

-- Insert sample sites with varied update status
INSERT INTO sites (name, url, site_uuid, api_token, drupal_core_version, is_active, created_at, updated_at, organization_id) VALUES
('Main Corporate Site', 'https://example.com', 'site-uuid-1', 'token-1', '10.1.0', true, NOW(), NOW(), 1),
('Marketing Site', 'https://marketing.example.com', 'site-uuid-2', 'token-2', '10.2.0', true, NOW(), NOW(), 1),
('Support Portal', 'https://support.example.com', 'site-uuid-3', 'token-3', '10.1.0', true, NOW(), NOW(), 1),
('Blog Site', 'https://blog.example.com', 'site-uuid-4', 'token-4', '10.2.2', true, NOW(), NOW(), 2),
('E-commerce Site', 'https://shop.example.com', 'site-uuid-5', 'token-5', '10.1.0', true, NOW(), NOW(), 2),
('Development Site', 'https://dev.example.com', 'site-uuid-6', 'token-6', '11.0.0', true, NOW(), NOW(), 1),
('Staging Site', 'https://staging.example.com', 'site-uuid-7', 'token-7', '11.0.1', true, NOW(), NOW(), 1),
('Documentation Site', 'https://docs.example.com', 'site-uuid-8', 'token-8', '10.2.2', true, NOW(), NOW(), 2);

-- Insert sample site modules with realistic scenarios
-- This creates a mix of up-to-date, outdated, and sites with security issues
INSERT INTO site_modules (site_id, module_id, current_version_id, latest_version_id, enabled, update_available, security_update_available, created_at, updated_at)
SELECT s.id, m.id, 
       cv.id as current_version_id, 
       lv.id as latest_version_id,
       sm.enabled, sm.update_available, sm.security_update_available,
       NOW(), NOW()
FROM (VALUES
    -- Main Corporate Site (OUTDATED - has security issues)
    ('site-uuid-1', 'drupal', '10.1.0', '10.1.2', true, true, true),                 -- Drupal core security update
    ('site-uuid-1', 'token', '1.11.0', '1.13.1', true, true, true),                  -- Critical security issue
    ('site-uuid-1', 'pathauto', '1.11.0', '1.12.0', true, true, false),              -- Regular update
    ('site-uuid-1', 'webform', '6.2.0', '6.2.3', true, true, true),                  -- Critical security issue
    ('site-uuid-1', 'views_bulk_operations', '4.2.0', '4.2.2', true, true, true),    -- Security update
    ('site-uuid-1', 'redirect', '1.8.0', '1.9.0', true, true, true),                 -- Security update
    
    -- Marketing Site (MIXED - some up to date, some outdated)
    ('site-uuid-2', 'drupal', '10.2.0', '10.2.2', true, true, true),                 -- Drupal core security update
    ('site-uuid-2', 'token', '1.12.0', '1.13.1', true, true, true),                  -- Security update available
    ('site-uuid-2', 'ctools', '4.0.3', '4.0.5', true, true, true),                   -- Security update available
    ('site-uuid-2', 'admin_toolbar', '3.4.1', '3.4.1', true, false, false),          -- Up to date
    ('site-uuid-2', 'metatag', '1.26.0', '1.26.0', true, false, false),              -- Up to date
    
    -- Support Portal (OUTDATED - legacy system)
    ('site-uuid-3', 'drupal', '10.1.0', '10.1.2', true, true, true),                 -- Drupal core security update
    ('site-uuid-3', 'token', '1.11.0', '1.13.1', true, true, true),                  -- Critical security issue
    ('site-uuid-3', 'admin_toolbar', '3.4.0', '3.4.1', true, true, false),           -- Regular update
    ('site-uuid-3', 'redirect', '1.8.0', '1.9.0', true, true, true),                 -- Security update
    
    -- Blog Site (FULLY UP TO DATE - compliant)
    ('site-uuid-4', 'drupal', '10.2.2', '10.2.2', true, false, false),               -- Up to date
    ('site-uuid-4', 'token', '1.13.1', '1.13.1', true, false, false),                -- Up to date
    ('site-uuid-4', 'webform', '6.2.3', '6.2.3', true, false, false),                -- Up to date
    ('site-uuid-4', 'paragraphs', '1.16.0', '1.16.0', true, false, false),           -- Up to date
    ('site-uuid-4', 'metatag', '1.26.0', '1.26.0', true, false, false),              -- Up to date
    
    -- E-commerce Site (CRITICAL - multiple security issues)
    ('site-uuid-5', 'drupal', '10.1.0', '10.1.2', true, true, true),                 -- Drupal core security update
    ('site-uuid-5', 'token', '1.11.0', '1.13.1', true, true, true),                  -- Critical security issue
    ('site-uuid-5', 'ctools', '4.0.3', '4.0.5', true, true, true),                   -- Security update available
    ('site-uuid-5', 'webform', '6.2.0', '6.2.3', true, true, true),                  -- Critical security issue
    ('site-uuid-5', 'admin_toolbar', '3.4.0', '3.4.1', true, true, false),           -- Regular update
    ('site-uuid-5', 'views_bulk_operations', '4.2.0', '4.2.2', true, true, true),    -- Security update
    
    -- Development Site (MOSTLY UP TO DATE - good compliance)
    ('site-uuid-6', 'drupal', '11.0.0', '11.0.1', true, true, true),                 -- Minor security update
    ('site-uuid-6', 'token', '1.13.1', '1.13.1', true, false, false),                -- Up to date
    ('site-uuid-6', 'pathauto', '1.11.0', '1.12.0', true, true, false),              -- Only one regular update
    ('site-uuid-6', 'field_group', '3.4.1', '3.4.1', true, false, false),            -- Up to date
    ('site-uuid-6', 'ctools', '4.0.5', '4.0.5', true, false, false),                 -- Up to date
    
    -- Staging Site (FULLY UP TO DATE - compliant)
    ('site-uuid-7', 'drupal', '11.0.1', '11.0.1', true, false, false),               -- Up to date
    ('site-uuid-7', 'token', '1.13.1', '1.13.1', true, false, false),                -- Up to date
    ('site-uuid-7', 'ctools', '4.0.5', '4.0.5', true, false, false),                 -- Up to date
    ('site-uuid-7', 'webform', '6.2.3', '6.2.3', true, false, false),                -- Up to date
    ('site-uuid-7', 'admin_toolbar', '3.4.1', '3.4.1', true, false, false),          -- Up to date
    
    -- Documentation Site (FULLY UP TO DATE - compliant)
    ('site-uuid-8', 'drupal', '10.2.2', '10.2.2', true, false, false),               -- Up to date
    ('site-uuid-8', 'paragraphs', '1.16.0', '1.16.0', true, false, false),           -- Up to date
    ('site-uuid-8', 'entity_reference_revisions', '1.11.0', '1.11.0', true, false, false), -- Up to date
    ('site-uuid-8', 'field_group', '3.4.1', '3.4.1', true, false, false),            -- Up to date
    ('site-uuid-8', 'metatag', '1.26.0', '1.26.0', true, false, false)               -- Up to date
) AS sm(site_uuid, module_machine_name, current_version, latest_version, enabled, update_available, security_update_available)
JOIN sites s ON s.site_uuid = sm.site_uuid
JOIN modules m ON m.machine_name = sm.module_machine_name
JOIN module_versions cv ON cv.module_id = m.id AND cv.version_string = sm.current_version
JOIN module_versions lv ON lv.module_id = m.id AND lv.version_string = sm.latest_version;

COMMIT;