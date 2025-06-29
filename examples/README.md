# Mock JSON Data Examples

This directory contains standardized mock JSON data that represents what Drupal modules will be sending to the monitoring platform.

## Directory Structure

- `drupal-submissions/` - Example JSON payloads from Drupal sites
  - `minimal-site.json` - Basic example with 5-10 modules
  - `standard-site.json` - Standard Drupal site with ~50 modules
  - `large-site.json` - Large site with 100+ modules
  - `schema.json` - JSON Schema for validation

## Data Structure

Each JSON file follows this structure:

```json
{
  "site": {
    "url": "https://example.com",
    "name": "Example Drupal Site",
    "token": "site-auth-token-123"
  },
  "drupal_info": {
    "core_version": "10.5.0",
    "php_version": "8.3.2",
    "ip_address": "195.12.13.14"
  },
  "modules": [
    {
      "machine_name": "views",
      "display_name": "Views",
      "module_type": "core",
      "enabled": true,
      "version": "10.1.6"
    }
  ]
}
```

## Usage with Newman

These JSON files can be used with Newman for data-driven testing:

```bash
# Run tests with specific data file
newman run postman/FastAPI_Monitoring_Platform.postman_collection.json \
  --environment postman/FastAPI_Testing_Environment.postman_environment.json \
  --iteration-data examples/drupal-submissions/minimal-site.json
```

## Module Types

- `core` - Drupal core modules
- `contrib` - Community contributed modules
- `custom` - Site-specific custom modules