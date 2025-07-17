-- Realistic sample data for monitoring platform
-- This creates a proper dataset showing version variations across 8 sites
-- Separates Drupal 10.x and 11.x properly, with realistic module distributions

BEGIN;

-- Clear existing data
DELETE FROM site_modules;
DELETE FROM module_versions;
DELETE FROM sites;
DELETE FROM modules;

-- Insert sample modules (core and contrib only)
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

-- Insert comprehensive module versions 
INSERT INTO module_versions (module_id, version_string, is_security_update, is_active, created_at, updated_at) 
SELECT m.id, v.version_string, v.is_security_update, v.is_active, NOW(), NOW()
FROM (VALUES 
    -- Drupal Core 10.x versions
    ('drupal', '10.0.0', false, true),
    ('drupal', '10.1.0', false, true),
    ('drupal', '10.1.1', true, true),   -- Security update
    ('drupal', '10.1.2', true, true),   -- Latest 10.1.x security
    ('drupal', '10.2.0', false, true),
    ('drupal', '10.2.1', true, true),   -- Security update
    ('drupal', '10.2.2', false, true),
    ('drupal', '10.2.3', true, true),   -- Latest 10.2.x security
    ('drupal', '10.3.0', false, true),
    ('drupal', '10.3.1', false, true),  -- Latest 10.3.x
    
    -- Drupal Core 11.x versions
    ('drupal', '11.0.0', false, true),
    ('drupal', '11.0.1', true, true),   -- Security update
    ('drupal', '11.0.2', false, true),  -- Latest 11.0.x
    
    -- Token module versions (many variations across sites)
    ('token', '1.9.0', false, true),    -- Older version
    ('token', '1.10.0', false, true),   -- Older version
    ('token', '1.11.0', false, true),   -- Common older version
    ('token', '1.12.0', true, true),    -- Security update
    ('token', '1.13.0', false, true),   -- Recent version
    ('token', '1.13.1', true, true),    -- Latest with security fix
    
    -- Pathauto versions (variations)
    ('pathauto', '1.10.0', false, true), -- Older
    ('pathauto', '1.11.0', false, true), -- Common
    ('pathauto', '1.11.1', true, true),  -- Security
    ('pathauto', '1.12.0', false, true), -- Latest
    
    -- CTools versions
    ('ctools', '4.0.1', false, true),   -- Old
    ('ctools', '4.0.3', false, true),   -- Common
    ('ctools', '4.0.4', true, true),    -- Security update
    ('ctools', '4.0.5', false, true),   -- Latest
    
    -- Webform versions (major variations)
    ('webform', '6.1.0', false, true),  -- Old major
    ('webform', '6.2.0', false, true),  -- Common
    ('webform', '6.2.1', true, true),   -- Security update
    ('webform', '6.2.2', false, true),  -- Recent
    ('webform', '6.2.3', true, true),   -- Latest with security fix
    
    -- Admin Toolbar versions
    ('admin_toolbar', '3.3.0', false, true), -- Old
    ('admin_toolbar', '3.4.0', false, true), -- Common
    ('admin_toolbar', '3.4.1', false, true), -- Latest
    
    -- Paragraphs versions
    ('paragraphs', '1.14.0', false, true), -- Old
    ('paragraphs', '1.15.0', false, true), -- Common
    ('paragraphs', '1.16.0', false, true), -- Latest
    
    -- Entity Reference Revisions
    ('entity_reference_revisions', '1.9.0', false, true),  -- Old
    ('entity_reference_revisions', '1.10.0', false, true), -- Common
    ('entity_reference_revisions', '1.11.0', false, true), -- Latest
    
    -- Field Group versions  
    ('field_group', '3.3.0', false, true), -- Old
    ('field_group', '3.4.0', false, true), -- Common
    ('field_group', '3.4.1', false, true), -- Latest
    
    -- Views Bulk Operations versions
    ('views_bulk_operations', '4.1.0', false, true), -- Old
    ('views_bulk_operations', '4.2.0', false, true), -- Common
    ('views_bulk_operations', '4.2.1', true, true),  -- Security update
    ('views_bulk_operations', '4.2.2', true, true),  -- Latest with security fix
    
    -- Metatag versions
    ('metatag', '1.24.0', false, true), -- Old
    ('metatag', '1.25.0', false, true), -- Common
    ('metatag', '1.26.0', false, true), -- Latest
    
    -- Redirect versions
    ('redirect', '1.7.0', false, true),  -- Old
    ('redirect', '1.8.0', false, true),  -- Common
    ('redirect', '1.8.1', true, true),   -- Security update
    ('redirect', '1.9.0', true, true)    -- Latest with security fix
) AS v(machine_name, version_string, is_security_update, is_active)
JOIN modules m ON m.machine_name = v.machine_name;

-- Insert sample sites with mixed Drupal versions
INSERT INTO sites (name, url, site_uuid, api_token, drupal_core_version, is_active, created_at, updated_at, organization_id) VALUES
-- Drupal 10.x sites (6 sites)
('Main Corporate Site', 'https://example.com', 'site-uuid-1', 'token-1', '10.1.0', true, NOW(), NOW(), 1),
('Marketing Site', 'https://marketing.example.com', 'site-uuid-2', 'token-2', '10.2.0', true, NOW(), NOW(), 1),
('Support Portal', 'https://support.example.com', 'site-uuid-3', 'token-3', '10.1.2', true, NOW(), NOW(), 1),
('Blog Site', 'https://blog.example.com', 'site-uuid-4', 'token-4', '10.2.3', true, NOW(), NOW(), 2),
('E-commerce Site', 'https://shop.example.com', 'site-uuid-5', 'token-5', '10.2.1', true, NOW(), NOW(), 2),
('Documentation Site', 'https://docs.example.com', 'site-uuid-6', 'token-6', '10.3.1', true, NOW(), NOW(), 2),

-- Drupal 11.x sites (2 sites)
('Development Site', 'https://dev.example.com', 'site-uuid-7', 'token-7', '11.0.0', true, NOW(), NOW(), 1),
('Staging Site', 'https://staging.example.com', 'site-uuid-8', 'token-8', '11.0.2', true, NOW(), NOW(), 1);

-- Insert realistic site modules with version variations
-- Each module appears on multiple sites with different versions
INSERT INTO site_modules (site_id, module_id, current_version_id, latest_version_id, enabled, update_available, security_update_available, created_at, updated_at)
SELECT s.id, m.id, 
       cv.id as current_version_id, 
       lv.id as latest_version_id,
       sm.enabled, 
       -- Calculate update_available dynamically
       CASE WHEN sm.current_version < sm.latest_version THEN true ELSE false END as update_available,
       -- Calculate security_update_available dynamically
       CASE 
           WHEN sm.current_version < sm.latest_version AND lv.is_security_update THEN true 
           ELSE false 
       END as security_update_available,
       NOW(), NOW()
FROM (VALUES
    -- === DRUPAL CORE (separate 10.x and 11.x) ===
    -- Drupal 10.x sites - latest available is 10.3.1
    ('site-uuid-1', 'drupal', '10.1.0', '10.3.1', true),  -- Needs major update
    ('site-uuid-2', 'drupal', '10.2.0', '10.3.1', true),  -- Needs update
    ('site-uuid-3', 'drupal', '10.1.2', '10.3.1', true),  -- Needs major update
    ('site-uuid-4', 'drupal', '10.2.3', '10.3.1', true),  -- Needs minor update
    ('site-uuid-5', 'drupal', '10.2.1', '10.3.1', true),  -- Needs update
    ('site-uuid-6', 'drupal', '10.3.1', '10.3.1', true),  -- Up to date
    
    -- Drupal 11.x sites - latest available is 11.0.2
    ('site-uuid-7', 'drupal', '11.0.0', '11.0.2', true),  -- Needs update
    ('site-uuid-8', 'drupal', '11.0.2', '11.0.2', true),  -- Up to date
    
    -- === TOKEN MODULE (appears on 7 sites with different versions) ===
    ('site-uuid-1', 'token', '1.11.0', '1.13.1', true),   -- Old version, needs security update
    ('site-uuid-2', 'token', '1.12.0', '1.13.1', true),   -- Has security issue
    ('site-uuid-3', 'token', '1.11.0', '1.13.1', true),   -- Old version
    ('site-uuid-4', 'token', '1.13.1', '1.13.1', true),   -- Up to date
    ('site-uuid-5', 'token', '1.10.0', '1.13.1', true),   -- Very old
    ('site-uuid-7', 'token', '1.13.0', '1.13.1', true),   -- Recent but not latest
    ('site-uuid-8', 'token', '1.13.1', '1.13.1', true),   -- Up to date
    
    -- === PATHAUTO MODULE (appears on 6 sites) ===
    ('site-uuid-1', 'pathauto', '1.11.0', '1.12.0', true), -- Needs update
    ('site-uuid-2', 'pathauto', '1.10.0', '1.12.0', true), -- Old version
    ('site-uuid-4', 'pathauto', '1.12.0', '1.12.0', true), -- Up to date
    ('site-uuid-5', 'pathauto', '1.11.0', '1.12.0', true), -- Needs update
    ('site-uuid-6', 'pathauto', '1.11.1', '1.12.0', true), -- Security version but needs update
    ('site-uuid-8', 'pathauto', '1.12.0', '1.12.0', true), -- Up to date
    
    -- === CTOOLS MODULE (appears on 5 sites) ===
    ('site-uuid-1', 'ctools', '4.0.3', '4.0.5', true),    -- Needs update
    ('site-uuid-2', 'ctools', '4.0.3', '4.0.5', true),    -- Needs update
    ('site-uuid-3', 'ctools', '4.0.1', '4.0.5', true),    -- Very old
    ('site-uuid-5', 'ctools', '4.0.4', '4.0.5', true),    -- Security version but needs update
    ('site-uuid-7', 'ctools', '4.0.5', '4.0.5', true),    -- Up to date
    
    -- === WEBFORM MODULE (appears on 6 sites) ===
    ('site-uuid-1', 'webform', '6.2.0', '6.2.3', true),   -- Needs security update
    ('site-uuid-2', 'webform', '6.1.0', '6.2.3', true),   -- Old major version
    ('site-uuid-4', 'webform', '6.2.3', '6.2.3', true),   -- Up to date
    ('site-uuid-5', 'webform', '6.2.0', '6.2.3', true),   -- Needs security update
    ('site-uuid-6', 'webform', '6.2.2', '6.2.3', true),   -- Needs update
    ('site-uuid-8', 'webform', '6.2.3', '6.2.3', true),   -- Up to date
    
    -- === ADMIN TOOLBAR MODULE (appears on 5 sites) ===
    ('site-uuid-2', 'admin_toolbar', '3.4.1', '3.4.1', true), -- Up to date
    ('site-uuid-3', 'admin_toolbar', '3.4.0', '3.4.1', true), -- Needs update
    ('site-uuid-5', 'admin_toolbar', '3.3.0', '3.4.1', true), -- Old version
    ('site-uuid-6', 'admin_toolbar', '3.4.1', '3.4.1', true), -- Up to date
    ('site-uuid-8', 'admin_toolbar', '3.4.0', '3.4.1', true), -- Needs update
    
    -- === PARAGRAPHS MODULE (appears on 4 sites) ===
    ('site-uuid-4', 'paragraphs', '1.16.0', '1.16.0', true), -- Up to date
    ('site-uuid-5', 'paragraphs', '1.14.0', '1.16.0', true), -- Old version
    ('site-uuid-6', 'paragraphs', '1.15.0', '1.16.0', true), -- Needs update
    ('site-uuid-8', 'paragraphs', '1.16.0', '1.16.0', true), -- Up to date
    
    -- === ENTITY REFERENCE REVISIONS (appears on 3 sites) ===
    ('site-uuid-4', 'entity_reference_revisions', '1.11.0', '1.11.0', true), -- Up to date
    ('site-uuid-6', 'entity_reference_revisions', '1.10.0', '1.11.0', true), -- Needs update
    ('site-uuid-8', 'entity_reference_revisions', '1.11.0', '1.11.0', true), -- Up to date
    
    -- === FIELD GROUP MODULE (appears on 4 sites) ===
    ('site-uuid-3', 'field_group', '3.3.0', '3.4.1', true), -- Old version
    ('site-uuid-6', 'field_group', '3.4.1', '3.4.1', true), -- Up to date
    ('site-uuid-7', 'field_group', '3.4.0', '3.4.1', true), -- Needs update
    ('site-uuid-8', 'field_group', '3.4.1', '3.4.1', true), -- Up to date
    
    -- === VIEWS BULK OPERATIONS (appears on 4 sites) ===
    ('site-uuid-1', 'views_bulk_operations', '4.2.0', '4.2.2', true), -- Needs security update
    ('site-uuid-3', 'views_bulk_operations', '4.1.0', '4.2.2', true), -- Very old
    ('site-uuid-5', 'views_bulk_operations', '4.2.0', '4.2.2', true), -- Needs security update
    ('site-uuid-7', 'views_bulk_operations', '4.2.2', '4.2.2', true), -- Up to date
    
    -- === METATAG MODULE (appears on 5 sites) ===
    ('site-uuid-2', 'metatag', '1.26.0', '1.26.0', true), -- Up to date
    ('site-uuid-4', 'metatag', '1.26.0', '1.26.0', true), -- Up to date
    ('site-uuid-5', 'metatag', '1.24.0', '1.26.0', true), -- Old version
    ('site-uuid-6', 'metatag', '1.25.0', '1.26.0', true), -- Needs update
    ('site-uuid-8', 'metatag', '1.26.0', '1.26.0', true), -- Up to date
    
    -- === REDIRECT MODULE (appears on 6 sites) ===
    ('site-uuid-1', 'redirect', '1.8.0', '1.9.0', true),  -- Needs security update
    ('site-uuid-3', 'redirect', '1.8.0', '1.9.0', true),  -- Needs security update
    ('site-uuid-4', 'redirect', '1.9.0', '1.9.0', true),  -- Up to date
    ('site-uuid-5', 'redirect', '1.7.0', '1.9.0', true),  -- Very old
    ('site-uuid-6', 'redirect', '1.8.1', '1.9.0', true),  -- Security version but needs update
    ('site-uuid-8', 'redirect', '1.9.0', '1.9.0', true)   -- Up to date
    
) AS sm(site_uuid, module_machine_name, current_version, latest_version, enabled)
JOIN sites s ON s.site_uuid = sm.site_uuid
JOIN modules m ON m.machine_name = sm.module_machine_name
JOIN module_versions cv ON cv.module_id = m.id AND cv.version_string = sm.current_version
JOIN module_versions lv ON lv.module_id = m.id AND lv.version_string = sm.latest_version;

COMMIT;