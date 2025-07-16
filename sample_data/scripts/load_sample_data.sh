#!/bin/bash
# Load sample data using Docker Compose

set -e

echo "🚀 Loading sample data..."

# Check if Docker Compose is running
if ! docker-compose ps | grep -q "api.*Up"; then
    echo "❌ API container is not running. Please start with: docker-compose up -d"
    exit 1
fi

# Load the sample data directly into the database
echo "📦 Loading comprehensive sample data..."
docker-compose exec -T db psql -U postgres -d postgres < "$(dirname "$0")/../sql/comprehensive_sample_data.sql"

echo "✅ Sample data loaded successfully!"

# Run verification
echo "🧪 Verifying sample data..."
docker-compose exec -T db psql -U postgres -d postgres -c "
SELECT 
    'Sites' as type, COUNT(*) as count 
FROM sites
UNION ALL
SELECT 
    'Modules' as type, COUNT(*) as count 
FROM modules
UNION ALL
SELECT 
    'Site Modules' as type, COUNT(*) as count 
FROM site_modules
UNION ALL
SELECT 
    'Security Updates' as type, COUNT(*) as count 
FROM site_modules 
WHERE security_update_available = true;
"

echo "🎉 Sample data loading completed!"
echo ""
echo "💡 You can now:"
echo "   1. Visit http://localhost:3000 to see the dashboard"
echo "   2. Check the Module Status Overview table"
echo "   3. View security alerts and compliance data"
echo "   4. Test the real-time WebSocket updates"