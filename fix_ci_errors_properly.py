#!/usr/bin/env python3
"""
Fix all CI/CD errors in the codebase properly.
"""

import ast
import os
import re
import subprocess

def get_imports_and_usage(content):
    """Parse Python code and get imports and their usage."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None, None
    
    imports = {}
    usage = set()
    
    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                imports[name] = (node.lineno, 'import')
            self.generic_visit(node)
        
        def visit_ImportFrom(self, node):
            if node.module and 'TYPE_CHECKING' in node.module:
                return
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                imports[name] = (node.lineno, 'from')
            self.generic_visit(node)
    
    class UsageVisitor(ast.NodeVisitor):
        def visit_Name(self, node):
            usage.add(node.id)
            self.generic_visit(node)
        
        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name):
                usage.add(node.value.id)
            self.generic_visit(node)
    
    ImportVisitor().visit(tree)
    UsageVisitor().visit(tree)
    
    return imports, usage

def fix_unused_imports(file_path):
    """Remove unused imports using AST parsing."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    if not content.strip():
        return
    
    imports, usage = get_imports_and_usage(content)
    if imports is None:
        return
    
    lines = content.split('\n')
    unused_lines = set()
    
    for name, (line_no, import_type) in imports.items():
        if name not in usage and 'TYPE_CHECKING' not in lines[line_no - 1]:
            unused_lines.add(line_no - 1)
    
    if unused_lines:
        new_lines = [line for i, line in enumerate(lines) if i not in unused_lines]
        
        # Clean up excessive empty lines
        cleaned = []
        prev_empty = False
        for line in new_lines:
            if line.strip() == '':
                if not prev_empty:
                    cleaned.append(line)
                prev_empty = True
            else:
                cleaned.append(line)
                prev_empty = False
        
        with open(file_path, 'w') as f:
            f.write('\n'.join(cleaned))

def fix_long_lines(file_path):
    """Fix lines longer than 88 characters."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed = []
    for line in lines:
        if len(line.rstrip()) > 88:
            # Skip comments, docstrings, and URLs
            stripped = line.strip()
            if stripped.startswith('#') or 'http' in line or '"""' in line:
                fixed.append(line)
                continue
            
            # Try to break at commas in function calls
            if '(' in line and ')' in line and ',' in line:
                indent = len(line) - len(line.lstrip())
                before_paren = line.split('(')[0]
                after_paren = line.split('(', 1)[1].rstrip(')\n')
                
                if ',' in after_paren:
                    fixed.append(before_paren + '(\n')
                    args = after_paren.split(',')
                    for i, arg in enumerate(args):
                        arg = arg.strip()
                        if i < len(args) - 1:
                            fixed.append(' ' * (indent + 4) + arg + ',\n')
                        else:
                            fixed.append(' ' * (indent + 4) + arg + '\n')
                    fixed.append(' ' * indent + ')\n')
                else:
                    fixed.append(line)
            else:
                fixed.append(line)
        else:
            fixed.append(line)
    
    with open(file_path, 'w') as f:
        f.writelines(fixed)

def fix_unused_variables(file_path):
    """Fix F841 unused variables."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return
    
    lines = content.split('\n')
    
    class UnusedVariableFixer(ast.NodeVisitor):
        def __init__(self):
            self.assignments = {}
            self.usage = set()
            self.fixes = []
        
        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.assignments[target.id] = target.lineno
            self.generic_visit(node)
        
        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                self.usage.add(node.id)
            self.generic_visit(node)
        
        def find_unused(self):
            for var, line_no in self.assignments.items():
                if var not in self.usage and var != '_':
                    self.fixes.append((line_no - 1, var))
    
    fixer = UnusedVariableFixer()
    fixer.visit(tree)
    fixer.find_unused()
    
    for line_no, var_name in fixer.fixes:
        if line_no < len(lines):
            lines[line_no] = re.sub(
                r'\b' + var_name + r'\b(?=\s*=)',
                '_',
                lines[line_no]
            )
    
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))

def main():
    """Main function to fix CI errors."""
    python_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith(
            '.') and d not in ['venv',
            '__pycache__']]
        )
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    
    # First pass: fix imports and variables
    for file_path in python_files:
        print(f"Processing {file_path}...")
        try:
            fix_unused_imports(file_path)
            fix_unused_variables(file_path)
            fix_long_lines(file_path)
        except Exception as e:
            print(f"Error in {file_path}: {e}")
    
    # Run formatters
    print("\nRunning isort...")
    subprocess.run(['isort', '.'], check=False)
    
    print("\nRunning Black...")
    subprocess.run(['black', '.'], check=False)
    
    print("\nDone!")

if __name__ == '__main__':
    main()