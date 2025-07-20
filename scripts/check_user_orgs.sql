-- Check users and their organizations
SELECT 
    u.id as user_id,
    u.email,
    u.role as user_role_field,
    u.is_superuser,
    u.organization_id,
    o.name as org_name,
    o.is_default,
    o.created_by,
    o.is_active as org_active
FROM users u
LEFT JOIN organizations o ON u.organization_id = o.id
ORDER BY u.id DESC;

-- Check user-organization associations
SELECT 
    uo.user_id,
    uo.organization_id,
    uo.is_default,
    u.email,
    o.name as org_name
FROM user_organizations uo
JOIN users u ON uo.user_id = u.id
JOIN organizations o ON uo.organization_id = o.id
ORDER BY uo.user_id DESC;

-- Check user roles
SELECT 
    ur.user_id,
    u.email,
    r.name as role_name,
    ur.organization_id,
    o.name as org_name
FROM user_roles ur
JOIN users u ON ur.user_id = u.id
JOIN roles r ON ur.role_id = r.id
LEFT JOIN organizations o ON ur.organization_id = o.id
ORDER BY ur.user_id DESC;