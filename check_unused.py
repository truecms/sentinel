#!/usr/bin/env python3
"""Quick script to find potential unused variables."""

import ast
import sys

def find_unused_variables(filename):
    """Find variables that are assigned but never used."""
    try:
        with open(filename, 'r') as f:
            tree = ast.parse(f.read(), filename)
    except Exception as e:
        return []
    
    # This is a simplified check - just looking for common patterns
    unused = []
    
    class UnusedChecker(ast.NodeVisitor):
        def visit_Assign(self, node):
            # Check if any target is named '_' (commonly unused)
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '_':
                    unused.append((node.lineno, '_', 'Unused underscore assignment'))
            self.generic_visit(node)
    
    UnusedChecker().visit(tree)
    return unused

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        unused = find_unused_variables(filename)
        if unused:
            print(f"\n{filename}:")
            for line, var, msg in unused:
                print(f"  Line {line}: {var} - {msg}")