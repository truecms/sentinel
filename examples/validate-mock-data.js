#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Load and validate all mock data files
const mockDataDir = path.join(__dirname, 'drupal-submissions');
const mockFiles = ['minimal-site.json', 'standard-site.json', 'large-site.json'];

console.log('Validating Mock Data Files\n' + '='.repeat(40));

mockFiles.forEach(filename => {
    const filePath = path.join(mockDataDir, filename);
    
    try {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        console.log(`\n✓ ${filename}`);
        console.log(`  - Site: ${data.site.name} (${data.site.url})`);
        console.log(`  - Token: ${data.site.token.substring(0, 20)}...`);
        console.log(`  - Drupal: ${data.drupal_info.core_version} / PHP ${data.drupal_info.php_version}`);
        console.log(`  - Modules: ${data.modules.length} total`);
        
        // Count by type
        const typeCounts = data.modules.reduce((acc, mod) => {
            acc[mod.module_type] = (acc[mod.module_type] || 0) + 1;
            return acc;
        }, {});
        
        Object.entries(typeCounts).forEach(([type, count]) => {
            console.log(`    - ${type}: ${count}`);
        });
        
        // Count enabled/disabled
        const enabledCount = data.modules.filter(m => m.enabled).length;
        console.log(`  - Enabled: ${enabledCount}, Disabled: ${data.modules.length - enabledCount}`);
        
        // Validate required fields
        const requiredSiteFields = ['url', 'name', 'token'];
        const requiredDrupalFields = ['core_version', 'php_version'];
        const requiredModuleFields = ['machine_name', 'display_name', 'module_type', 'enabled', 'version'];
        
        let valid = true;
        
        requiredSiteFields.forEach(field => {
            if (!data.site[field]) {
                console.log(`  ❌ Missing site.${field}`);
                valid = false;
            }
        });
        
        requiredDrupalFields.forEach(field => {
            if (!data.drupal_info[field]) {
                console.log(`  ❌ Missing drupal_info.${field}`);
                valid = false;
            }
        });
        
        data.modules.forEach((module, index) => {
            requiredModuleFields.forEach(field => {
                if (module[field] === undefined) {
                    console.log(`  ❌ Missing modules[${index}].${field}`);
                    valid = false;
                }
            });
        });
        
        if (valid) {
            console.log(`  ✅ All required fields present`);
        }
        
    } catch (error) {
        console.log(`\n❌ ${filename}: ${error.message}`);
    }
});

console.log('\n' + '='.repeat(40));
console.log('\nNewman Usage Example:');
console.log('newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \\');
console.log('  --environment postman/environment.json \\');
console.log('  --iteration-data examples/drupal-submissions/minimal-site.json');