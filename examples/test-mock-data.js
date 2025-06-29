#!/usr/bin/env node

const newman = require('newman');
const fs = require('fs');
const path = require('path');

// Load mock data
const mockDataPath = path.join(__dirname, 'drupal-submissions/minimal-site.json');
const mockData = JSON.parse(fs.readFileSync(mockDataPath, 'utf8'));

console.log('Mock Data Loaded:');
console.log(`- Site: ${mockData.site.name} (${mockData.site.url})`);
console.log(`- Drupal Core: ${mockData.drupal_info.core_version}`);
console.log(`- Modules Count: ${mockData.modules.length}`);
console.log(`- Module Types: ${[...new Set(mockData.modules.map(m => m.module_type))].join(', ')}`);

// This script demonstrates how the mock data can be used with Newman
console.log('\nTo use this data with Newman, run:');
console.log(`newman run "postman/FastAPI Monitoring Platform.postman_collection.json" \\`);
console.log(`  --environment postman/environment.json \\`);
console.log(`  --iteration-data ${mockDataPath}`);

// Validate the structure matches our schema
const schemaPath = path.join(__dirname, 'drupal-submissions/schema.json');
if (fs.existsSync(schemaPath)) {
    console.log('\nSchema validation file found at:', schemaPath);
}