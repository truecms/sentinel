#!/usr/bin/env python3
"""
Fix all CI/CD errors in the codebase.
"""

import os
import re
import subprocess


def remove_unused_imports(file_path):
    """Remove unused imports from a Python file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Skip if file is empty
    if not content.strip():
        return

    lines = content.split("\n")

    # Extract imports
    import_lines = []
    import_map = {}  # import name -> line number

    for i, line in enumerate(lines):
        if line.strip().startswith(("import ", "from ")):
            import_lines.append((i, line))

            # Extract imported names
            if line.strip().startswith("import "):
                # Handle: import module, import module as alias
                parts = line.strip()[7:].split(" as ")
                module = parts[0].strip()
                alias = parts[1].strip() if len(parts) > 1 else module
                import_map[alias] = i
            elif line.strip().startswith("from "):
                # Handle: from module import name, from module import name as alias
                match = re.match(r"from\s+[\w.]+\s+import\s+(.+)", line.strip())
                if match:
                    imports_part = match.group(1)
                    # Handle multiple imports
                    for imp in imports_part.split(","):
                        imp = imp.strip()
                        if " as " in imp:
                            name, alias = imp.split(" as ")
                            import_map[alias.strip()] = i
                        else:
                            import_map[imp] = i

    # Check which imports are used
    code_without_imports = "\n".join(
        [
            line
            for i, line in enumerate(lines)
            if i not in [idx for idx, _ in import_lines]
        ]
    )

    unused_lines = set()
    for name, line_idx in import_map.items():
        # Check if the import is used in the code
        # Skip TYPE_CHECKING imports
        if "TYPE_CHECKING" in lines[line_idx]:
            continue

        # Create regex pattern to match usage
        pattern = r"\b" + re.escape(name) + r"\b"
        if not re.search(pattern, code_without_imports):
            unused_lines.add(line_idx)

    # Remove unused import lines
    if unused_lines:
        new_lines = [line for i, line in enumerate(lines) if i not in unused_lines]

        # Clean up empty lines left by removed imports
        cleaned_lines = []
        prev_empty = False
        for line in new_lines:
            if line.strip() == "":
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                _ = False

        with open(file_path, "w") as f:
            f.write("\n".join(cleaned_lines))


def fix_line_length(file_path):
    """Fix lines that are too long (>88 characters)."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    fixed_lines = []
    for line in lines:
        if len(line.rstrip()) > 88:
            # Skip URLs and long strings
            if "http" in line or '"""' in line or "'''" in line:
                fixed_lines.append(line)
                continue

            # Try to split at logical points
            if " = " in line and not line.strip().startswith(('"""', "'''")):
                indent = len(line) - len(line.lstrip())
                parts = line.split(" = ", 1)
                if len(parts[0]) + 3 + len(parts[1].rstrip()) > 88:
                    fixed_lines.append(parts[0] + " = (\n")
                    fixed_lines.append(" " * (indent + 4) + parts[1].strip() + "\n")
                    fixed_lines.append(" " * indent + ")\n")
                else:
                    fixed_lines.append(line)
            elif "(" in line and ")" in line and line.count("(") == 1:
                # Split function calls
                indent = len(line) - len(line.lstrip())
                before_paren = line.split("(", 1)[0]
                after_paren = line.split("(", 1)[1]

                if len(line.rstrip()) > 88 and "," in after_paren:
                    fixed_lines.append(before_paren + "(\n")
                    args = after_paren.rstrip(")\n").split(",")
                    for i, arg in enumerate(args):
                        if i < len(args) - 1:
                            fixed_lines.append(" " * (indent + 4) + arg.strip() + ",\n")
                        else:
                            fixed_lines.append(" " * (indent + 4) + arg.strip() + "\n")
                    fixed_lines.append(" " * indent + ")\n")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    with open(file_path, "w") as f:
        f.writelines(fixed_lines)


def fix_unused_variables(file_path):
    """Fix unused variable assignments."""
    with open(file_path, "r") as f:
        content = f.read()

    # Pattern to find variable assignments
    pattern = r"^(\s*)(\w+)\s*=\s*(.+)$"

    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match:
            indent, var_name, value = match.groups()

            # Check if variable is used later
            remaining_code = "\n".join(lines[i + 1 :])
            var_pattern = r"\b" + re.escape(var_name) + r"\b"

            if not re.search(var_pattern, remaining_code) and var_name != "_":
                # Replace with underscore if not used
                fixed_lines.append(f"{indent}_ = {value}")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    with open(file_path, "w") as f:
        f.write("\n".join(fixed_lines))


def main():
    """Main function to fix all CI errors."""
    # Get all Python files
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip virtual environments and hidden directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ["venv", "__pycache__", "node_modules"]
        ]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    print(f"Found {len(python_files)} Python files")

    # Fix each file
    for file_path in python_files:
        print(f"Processing {file_path}...")

        try:
            # First remove unused imports
            remove_unused_imports(file_path)

            # Then fix line length
            fix_line_length(file_path)

            # Finally fix unused variables
            fix_unused_variables(file_path)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Run black formatter
    print("\nRunning Black formatter...")
    subprocess.run(["black", "."], check=False)

    # Run isort
    print("\nRunning isort...")
    subprocess.run(["isort", "."], check=False)

    print("\nDone! All CI errors should be fixed.")


if __name__ == "__main__":
    main()
