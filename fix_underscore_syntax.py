#!/usr/bin/env python3
"""Fix underscore syntax errors in test files."""

import re
import os
from pathlib import Path

# Define patterns and replacements
PATTERNS = [
    # Organization patterns
    (r'(\s+)_=("Test.*Org.*"),', r'\1name=\2,'),
    
    # User patterns  
    (r'(\s+)_=("hashed_password"),', r'\1hashed_password=\2,'),
    (r'(\s+)_=(org\.id),', r'\1organization_id=\2,'),
    (r'(\s+)_=("user"),', r'\1role=\2,'),
    (r'(\s+)_=(False),\s*# is_superuser', r'\1is_superuser=\2,'),
    (r'(\s+)_=(True),\s*# is_active', r'\1is_active=\2,'),
    
    # Module patterns
    (r'(\s+)_=("https://drupal\.org/.*"),', r'\1drupal_org_link=\2,'),
    (r'(\s+)_=(".*test.*module.*"),\s*# machine_name', r'\1machine_name=\2,'),
    (r'(\s+)_=(".*Test.*Module.*"),\s*# display_name', r'\1display_name=\2,'),
    (r'(\s+)_=("custom"|"contrib"|"core"),', r'\1module_type=\2,'),
    (r'(\s+)_=(".*description.*"),', r'\1description=\2,'),
    
    # ModuleVersion patterns
    (r'(\s+)_=(.*\.id),\s*# module_id', r'\1module_id=\2,'),
    (r'(\s+)_=("\d+\.\d+\.\d+"),\s*# version_string', r'\1version_string=\2,'),
    (r'(\s+)_=(datetime.*),\s*# release_date', r'\1release_date=\2,'),
    (r'(\s+)_=(False|True),\s*# is_security_update', r'\1is_security_update=\2,'),
    (r'(\s+)_=("https://drupal\.org/.*/releases/.*"),', r'\1release_notes_link=\2,'),
    (r'(\s+)_=(\[.*\]),\s*# drupal_core_compatibility', r'\1drupal_core_compatibility=\2,'),
    
    # Site patterns
    (r'(\s+)_=("https://.*\.example\.com"),', r'\1url=\2,'),
    
    # Common audit fields
    (r'(\s+)_=(test_user\.id|org_admin\.id|org_user\.id),\s*# created_by', r'\1created_by=\2,'),
    (r'(\s+)_=(test_user\.id|org_admin\.id|org_user\.id),\s*# updated_by', r'\1updated_by=\2,'),
    (r'(\s+)_=(True),\s*# is_active', r'\1is_active=\2,'),
    (r'(\s+)_=(False),\s*# is_deleted', r'\1is_deleted=\2,'),
    
    # Generic pattern for remaining cases (be careful with this)
    (r'(\s+)_=(.*),\s*$', r'\1FIXME_FIELD=\2,'),
]

def fix_file(filepath):
    """Fix underscore syntax in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    for pattern, replacement in PATTERNS:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            changes_made.append(f"Applied pattern: {pattern}")
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")
        for change in changes_made:
            print(f"  - {change}")
        return True
    return False

def main():
    """Main function to fix all test files."""
    test_dir = Path("/Users/ivan/websites/sites/monitoring/tests")
    fixed_count = 0
    
    for py_file in test_dir.rglob("*.py"):
        if fix_file(py_file):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()