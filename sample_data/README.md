# Sample Data for Monitoring Dashboard

This directory contains comprehensive sample data for the monitoring dashboard, designed to showcase realistic metrics and demonstrate the full functionality of the application.

## 🗂️ Directory Structure

```
sample_data/
├── sql/
│   └── comprehensive_sample_data.sql    # Complete sample database
├── scripts/
│   ├── load_sample_data.py             # Python script to load data
│   └── load_sample_data.sh             # Shell script for Docker
├── tests/
│   └── test_sample_data.py             # Test script to verify data
└── README.md                           # This file
```

## 📊 Sample Data Overview

The sample data includes:

### Sites (8 total)
- **Main Corporate Site**: Outdated with multiple security issues
- **Marketing Site**: Mixed compliance status
- **Support Portal**: Legacy system with critical updates needed
- **Blog Site**: Fully compliant and up-to-date
- **E-commerce Site**: Critical security vulnerabilities
- **Development Site**: Mostly compliant with one regular update
- **Staging Site**: Fully compliant
- **Documentation Site**: Fully compliant

### Modules (12 total)
- **Core modules**: views, node, user, media
- **Contrib modules**: token, pathauto, ctools, webform, admin_toolbar, paragraphs, entity_reference_revisions, field_group
- **Mixed update status**: Some with security updates, some up-to-date

### Realistic Metrics
- **Compliance Rate**: ~62.5% (5 out of 8 sites compliant)
- **Security Updates**: Multiple sites with critical security issues
- **Vulnerability Distribution**: Critical, high, medium, and low severity issues
- **Update Patterns**: Realistic mix of security and regular updates

## 🚀 Loading Sample Data

### Method 1: Using Docker (Recommended)
```bash
# Make sure Docker Compose is running
docker-compose up -d

# Load sample data
./sample_data/scripts/load_sample_data.sh
```

### Method 2: Using Python Script
```bash
# Set database connection
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"

# Load sample data
python3 ./sample_data/scripts/load_sample_data.py

# Reset database first (optional)
python3 ./sample_data/scripts/load_sample_data.py --reset
```

### Method 3: Direct SQL
```bash
# Connect to database and run SQL file
psql -U postgres -d postgres -f sample_data/sql/comprehensive_sample_data.sql
```

## 🧪 Testing Sample Data

Run the test script to verify that sample data is loaded correctly:

```bash
python3 ./sample_data/tests/test_sample_data.py
```

The test script verifies:
- ✅ Correct data counts (8 sites, 12 modules, 40+ site modules)
- ✅ Security updates are present
- ✅ Realistic compliance rate (between 0-100%)
- ✅ Module versions are properly linked
- ✅ Site variety (compliant, partially compliant, non-compliant)

## 📈 Expected Dashboard Metrics

After loading the sample data, you should see:

### Overview Cards
- **Active Sites**: 8
- **Security Updates**: 15+ (varies by site)
- **Compliance Rate**: ~62.5%
- **Critical Issues**: 3 (sites with 4+ security updates)

### Module Status Overview
- Mix of modules with security updates and regular updates
- Different version statuses across sites
- Realistic update patterns

### Security Metrics
- **Critical**: 3 sites (E-commerce, Main Corporate, Support Portal)
- **High**: 1 site (Marketing)
- **Medium**: 1 site (Development)
- **Low**: 3 sites (fully compliant sites)

## 🔄 Updating Sample Data

To update the sample data:

1. Edit `sql/comprehensive_sample_data.sql`
2. Run the loading script to refresh the database
3. Run the test script to verify changes
4. Update this README if metrics change significantly

## 🎯 Use Cases

This sample data demonstrates:

1. **Security Monitoring**: Critical vulnerabilities across multiple sites
2. **Compliance Tracking**: Mix of compliant and non-compliant sites
3. **Update Management**: Various update scenarios and priorities
4. **Risk Assessment**: Different severity levels and site impacts
5. **Real-time Updates**: WebSocket integration with live data
6. **Reporting**: Comprehensive metrics for decision-making

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check that PostgreSQL is running
   - Verify DATABASE_URL is correct
   - Ensure database exists

2. **Sample Data Not Loading**
   - Check file permissions (`chmod +x scripts/*`)
   - Verify Docker containers are running
   - Check database user permissions

3. **Dashboard Shows Zero Values**
   - Ensure API is running and accessible
   - Check authentication is working
   - Verify WebSocket connections

### Getting Help

If you encounter issues:
1. Run the test script to verify data integrity
2. Check API logs: `docker-compose logs api`
3. Check database connectivity: `docker-compose exec db psql -U postgres`
4. Verify frontend is connecting to correct API endpoint

## 📝 Notes

- Sample data is designed to be realistic but not production-ready
- Use only in development and testing environments
- Data includes realistic security scenarios for testing
- Module versions and update patterns follow Drupal conventions