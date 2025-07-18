#!/usr/bin/env python3
"""Fix all underscore syntax errors in test files."""

import os
import re
from pathlib import Path


def fix_function_args(content):
    """Fix underscore used as function argument."""
    # Pattern: _: type annotation or _ = value in function definitions
    pattern = r"(\bdef\s+\w+\s*\([^)]*?)(\s*_\s*:\s*[\w\[\]]+|\s*_\s*=\s*[^,\)]+)"

    def replace_func(match):
        prefix = match.group(1)
        arg_part = match.group(2)
        # Replace _ with a meaningful name based on context
        return prefix + arg_part.replace("_", "unused_param", 1)

    return re.sub(pattern, replace_func, content)


def fix_model_fields(content):
    """Fix _ used as model field names."""
    patterns = [
        # User model fields
        (r'(\s+)_(\s*=\s*"[^"]*@[^"]*")', r"\1email\2"),  # email fields
        (
            r"(\s+)_(\s*=\s*get_password_hash)",
            r"\1hashed_password\2",
        ),  # password fields
        (r"(\s+)_(\s*=\s*True.*is_active)", r"\1is_active\2"),  # is_active duplicate
        (
            r"(\s+)created_by(\s*=\s*test_organization\.id)",
            r"\1organization_id\2",
        ),  # org reference
        # API call headers
        (r"(\s+)_(\s*=\s*superuser_token_headers)", r"\1headers\2"),
        (r"(\s+)_(\s*=\s*user_token_headers)", r"\1headers\2"),
        (r"(\s+)_(\s*=\s*admin_token_headers)", r"\1headers\2"),
        # Response fields
        (r'"_"(\s*:\s*"[^"]*@[^"]*")', r'"email"\1'),  # email in JSON
        (r'"_"(\s*:\s*"test)', r'"password"\1'),  # password in JSON
        # Enum fields
        (r'(\s+)_(\s*=\s*"critical")', r"\1CRITICAL\2"),
        (r'(\s+)_(\s*=\s*"high")', r"\1HIGH\2"),
        (r'(\s+)_(\s*=\s*"medium")', r"\1MEDIUM\2"),
        (r'(\s+)_(\s*=\s*"low")', r"\1LOW\2"),
        (r'(\s+)_(\s*=\s*"healthy")', r"\1HEALTHY\2"),
        (r'(\s+)_(\s*=\s*"warning")', r"\1WARNING\2"),
        # user_organization.insert() calls
        (r"created_by(\s*=\s*test_user\.id,\s*organization_id)", r"user_id\1"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def fix_pytest_mark(content):
    """Fix _ = pytest.mark.asyncio patterns."""
    # Replace _ = pytest.mark.asyncio with pytestmark = pytest.mark.asyncio
    content = re.sub(
        r"^(\s*)_(\s*=\s*pytest\.mark\.asyncio)",
        r"\1pytestmark\2",
        content,
        flags=re.MULTILINE,
    )
    return content


def fix_generic_assignments(content):
    """Fix remaining generic _ assignments."""
    # Fix duplicate is_active fields
    content = re.sub(
        r"is_active=True,\s*\n\s*is_active=True,",
        "is_active=True,\n        is_superuser=True,",
        content,
    )

    # Fix organization field names
    content = re.sub(
        r"created_by=test_organization\.id,",
        "organization_id=test_organization.id,",
        content,
    )

    return content


def should_process_file(filepath):
    """Check if file should be processed."""
    # Skip non-Python files
    if not filepath.endswith(".py"):
        return False

    # Skip migrations
    if "/migrations/" in filepath or "/alembic/" in filepath:
        return False

    # Skip __pycache__
    if "__pycache__" in filepath:
        return False

    return True


def process_file(filepath):
    """Process a single file to fix underscore errors."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes in order
        content = fix_pytest_mark(content)
        content = fix_model_fields(content)
        content = fix_function_args(content)
        content = fix_generic_assignments(content)

        # Only write if content changed
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Main function to process all files."""
    # Directories to process
    dirs_to_process = ["tests", "app"]

    total_files = 0
    fixed_files = 0

    for dir_name in dirs_to_process:
        if not os.path.exists(dir_name):
            continue

        for root, dirs, files in os.walk(dir_name):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != "__pycache__"]

            for file in files:
                filepath = os.path.join(root, file)
                if should_process_file(filepath):
                    total_files += 1
                    if process_file(filepath):
                        fixed_files += 1
                        print(f"Fixed: {filepath}")

    print(f"\nProcessed {total_files} files, fixed {fixed_files} files")


if __name__ == "__main__":
    main()
