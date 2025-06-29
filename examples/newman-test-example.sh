#!/bin/bash

# Newman test example using mock Drupal data
# This script demonstrates how to use the mock JSON data with the Postman collection

echo "Newman Test Example - Using Mock Drupal Data"
echo "==========================================="

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    echo "Error: Newman is not installed. Please install it with: npm install -g newman"
    exit 1
fi

# Base directory
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
POSTMAN_DIR="$BASE_DIR/postman"
EXAMPLES_DIR="$BASE_DIR/examples"

echo "Base directory: $BASE_DIR"
echo ""

# Test with minimal site data
echo "1. Testing with minimal site data (8 modules)..."
echo "------------------------------------------------"
newman run "$POSTMAN_DIR/Module_Sync_Collection.postman_collection.json" \
  --environment "$POSTMAN_DIR/environment.json" \
  --iteration-data "$EXAMPLES_DIR/drupal-submissions/minimal-site.json" \
  --reporters cli,json \
  --reporter-json-export "$BASE_DIR/newman-results-minimal.json" \
  --suppress-exit-code

echo ""

# Test with standard site data
echo "2. Testing with standard site data (52 modules)..."
echo "-------------------------------------------------"
newman run "$POSTMAN_DIR/Module_Sync_Collection.postman_collection.json" \
  --environment "$POSTMAN_DIR/environment.json" \
  --iteration-data "$EXAMPLES_DIR/drupal-submissions/standard-site.json" \
  --reporters cli,json \
  --reporter-json-export "$BASE_DIR/newman-results-standard.json" \
  --suppress-exit-code

echo ""

# Test with large site data
echo "3. Testing with large site data (135 modules)..."
echo "------------------------------------------------"
newman run "$POSTMAN_DIR/Module_Sync_Collection.postman_collection.json" \
  --environment "$POSTMAN_DIR/environment.json" \
  --iteration-data "$EXAMPLES_DIR/drupal-submissions/large-site.json" \
  --reporters cli,json \
  --reporter-json-export "$BASE_DIR/newman-results-large.json" \
  --suppress-exit-code

echo ""
echo "Newman tests completed!"
echo "Results saved to:"
echo "  - newman-results-minimal.json"
echo "  - newman-results-standard.json"
echo "  - newman-results-large.json"