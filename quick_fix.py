#!/usr/bin/env python3
"""Quick fix for the most common underscore syntax errors."""

import re
import sys
from pathlib import Path


def fix_file(filepath):
    """Fix underscore syntax in a single file."""
    with open(filepath, "r") as f:
        lines = f.readlines()

    fixed_lines = []
    changed = False

    for i, line in enumerate(lines):
        original_line = line

        # Try to fix based on context from surrounding lines
        if re.match(r"^\s*_=", line):
            # Look at previous lines for context
            context = "".join(lines[max(0, i - 5) : i])

            # Common patterns
            if "Organization(" in context:
                if (
                    '"' in line
                    and "Organization" not in line
                    and "org" not in line.lower()
                ):
                    line = re.sub(r"_=", "name=", line)
                elif "test_user.id" in line or "user.id" in line:
                    if "created_by" not in context:
                        line = re.sub(r"_=", "created_by=", line)
                    else:
                        line = re.sub(r"_=", "updated_by=", line)
                elif "True" in line:
                    if "is_active" not in context:
                        line = re.sub(r"_=", "is_active=", line)
                    else:
                        line = re.sub(r"_=", "is_deleted=", line)
                elif "False" in line:
                    line = re.sub(r"_=", "is_deleted=", line)

            elif "User(" in context:
                if '"hashed_password"' in line:
                    line = re.sub(r"_=", "hashed_password=", line)
                elif "org.id" in line:
                    line = re.sub(r"_=", "organization_id=", line)
                elif '"user"' in line or '"admin"' in line:
                    line = re.sub(r"_=", "role=", line)
                elif "False" in line:
                    if "is_active" not in context:
                        line = re.sub(r"_=", "is_active=", line)
                    else:
                        line = re.sub(r"_=", "is_superuser=", line)
                elif "True" in line:
                    line = re.sub(r"_=", "is_active=", line)

            elif "Module(" in context:
                if "https://drupal.org" in line:
                    line = re.sub(r"_=", "drupal_org_link=", line)
                elif '"custom"' in line or '"contrib"' in line:
                    line = re.sub(r"_=", "module_type=", line)
                elif "machine_name" not in context and '"' in line and "_" in line:
                    line = re.sub(r"_=", "machine_name=", line)
                elif "display_name" not in context and '"' in line and "Test" in line:
                    line = re.sub(r"_=", "display_name=", line)
                elif "description" not in context and '"' in line:
                    line = re.sub(r"_=", "description=", line)

            elif "ModuleVersion(" in context:
                if ".id" in line and "module" in line:
                    line = re.sub(r"_=", "module_id=", line)
                elif '"' in line and re.search(r"\d+\.\d+", line):
                    line = re.sub(r"_=", "version_string=", line)
                elif "datetime" in line:
                    line = re.sub(r"_=", "release_date=", line)
                elif "https://drupal.org" in line:
                    line = re.sub(r"_=", "release_notes_link=", line)
                elif "[" in line and "]" in line:
                    line = re.sub(r"_=", "drupal_core_compatibility=", line)
                elif "False" in line or "True" in line:
                    line = re.sub(r"_=", "is_security_update=", line)

            elif "Site(" in context:
                if "https://" in line:
                    line = re.sub(r"_=", "url=", line)

            elif "SiteModule(" in context:
                if "site.id" in line:
                    line = re.sub(r"_=", "site_id=", line)
                elif "version.id" in line:
                    if "current_version" not in context:
                        line = re.sub(r"_=", "current_version_id=", line)
                    else:
                        line = re.sub(r"_=", "latest_version_id=", line)
                elif "True" in line:
                    if "enabled" not in context:
                        line = re.sub(r"_=", "enabled=", line)
                    elif "update_available" not in context:
                        line = re.sub(r"_=", "update_available=", line)
                    else:
                        line = re.sub(r"_=", "security_update_available=", line)

            # Generic user.id handling
            if ".id" in line and ("created" not in line and "updated" not in line):
                if "created_by" not in context:
                    line = re.sub(r"_=", "created_by=", line)
                else:
                    line = re.sub(r"_=", "updated_by=", line)

        if line != original_line:
            changed = True

        fixed_lines.append(line)

    if changed:
        with open(filepath, "w") as f:
            f.writelines(fixed_lines)
        print(f"Fixed {filepath}")
        return True
    return False


def main():
    """Main function."""
    test_dir = Path("/Users/ivan/websites/sites/monitoring/tests")
    fixed_count = 0

    # Get all files with the issue
    files_to_fix = []
    for py_file in test_dir.rglob("*.py"):
        with open(py_file, "r") as f:
            if any(re.match(r"^\s*_=", line) for line in f):
                files_to_fix.append(py_file)

    print(f"Found {len(files_to_fix)} files to fix")

    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
