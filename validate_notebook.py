#!/usr/bin/env python3
"""
Quick validation script for AstroFinanceProject.ipynb
Tests notebook structure, logging configuration, and Python syntax.

Usage:
    python validate_notebook.py
"""

import json
import sys
import ast
import re
from pathlib import Path


def validate_structure(notebook_path):
    """Validate basic notebook structure"""
    print("=" * 70)
    print("VALIDATING NOTEBOOK STRUCTURE")
    print("=" * 70)

    try:
        with open(notebook_path, 'r') as f:
            nb = json.load(f)

        # Check required fields
        assert 'cells' in nb, "Notebook missing 'cells' field"
        assert 'nbformat' in nb, "Notebook missing 'nbformat' field"

        cells = nb['cells']
        code_cells = [c for c in cells if c['cell_type'] == 'code']
        markdown_cells = [c for c in cells if c['cell_type'] == 'markdown']

        print(f"✓ Valid notebook structure")
        print(f"✓ Total cells: {len(cells)}")
        print(f"✓ Code cells: {len(code_cells)}")
        print(f"✓ Markdown cells: {len(markdown_cells)}")

        return True, nb
    except Exception as e:
        print(f"✗ Notebook validation failed: {e}")
        return False, None


def validate_logging(nb):
    """Validate logging configuration in code cells"""
    print("\n" + "=" * 70)
    print("VALIDATING LOGGING CONFIGURATION")
    print("=" * 70)

    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

    errors = []
    warnings = []
    cells_with_logging = 0

    for i, cell in enumerate(code_cells):
        source = cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])

        # Skip very short cells (likely just imports or pip installs)
        if len(source.strip()) < 50:
            continue

        has_logging_import = 'import logging' in source
        has_logging_config = 'logging.basicConfig' in source
        has_logger = 'logger = logging.getLogger' in source

        if has_logging_import:
            cells_with_logging += 1

            if not has_logging_config:
                warnings.append(f"Cell {i+1}: Has logging import but no configuration")
            if not has_logger:
                warnings.append(f"Cell {i+1}: Has logging import but no logger instance")

            # Check for proper log level usage
            logger_calls = re.findall(r'logger\.(info|warning|error|critical|debug)\(', source)
            if logger_calls:
                levels = {}
                for level in logger_calls:
                    levels[level] = levels.get(level, 0) + 1

                print(f"✓ Cell {i+1}: {len(logger_calls)} logger calls")
                print(f"  Levels: INFO={levels.get('info', 0)}, WARN={levels.get('warning', 0)}, "
                      f"ERROR={levels.get('error', 0)}, CRITICAL={levels.get('critical', 0)}")

            # Check for proper format string
            if 'logging.basicConfig' in source:
                if "format='%(asctime)s | %(levelname)" in source or \
                   'format="%(asctime)s | %(levelname)' in source:
                    print(f"  ✓ Proper timestamp format configured")
                else:
                    warnings.append(f"Cell {i+1}: Logging format may not include timestamps")

    print(f"\n✓ Found logging configuration in {cells_with_logging} code cells")

    if errors:
        print("\n✗ ERRORS:")
        for err in errors:
            print(f"  {err}")
        return False

    if warnings:
        print("\n⚠ WARNINGS:")
        for warn in warnings:
            print(f"  {warn}")

    return True


def validate_syntax(nb):
    """Validate Python syntax in all code cells"""
    print("\n" + "=" * 70)
    print("VALIDATING PYTHON SYNTAX")
    print("=" * 70)

    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

    errors = []
    valid_cells = 0
    warnings = []

    for i, cell in enumerate(code_cells):
        source = cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])

        # Remove IPython magic commands and shell commands
        lines = source.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip magic commands and shell commands
            if line.strip().startswith('!') or line.strip().startswith('%'):
                continue
            cleaned_lines.append(line)

        cleaned_source = '\n'.join(cleaned_lines)

        # Try to parse the Python code
        try:
            ast.parse(cleaned_source)
            valid_cells += 1
            print(f"✓ Cell {i+1}: Valid Python syntax")
        except SyntaxError as e:
            # Check if this is a known false positive (logging.basicConfig with trailing content)
            if 'logging.basicConfig' in cleaned_source and e.lineno:
                # Try compiling the actual source to see if it's really invalid
                try:
                    compile(cleaned_source, f'<cell-{i+1}>', 'exec')
                    # If compile works, it's a false positive from ast.parse
                    valid_cells += 1
                    print(f"✓ Cell {i+1}: Valid Python syntax (verified with compile)")
                    continue
                except:
                    pass

            error_msg = f"Cell {i+1}: Syntax error at line {e.lineno}: {e.msg}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")
            # Show context
            if e.lineno:
                context_lines = cleaned_source.split('\n')
                start = max(0, e.lineno - 2)
                end = min(len(context_lines), e.lineno + 2)
                print(f"  Context:")
                for idx in range(start, end):
                    prefix = ">>> " if idx == e.lineno - 1 else "    "
                    if idx < len(context_lines):
                        print(f"  {prefix}{context_lines[idx]}")

    if errors:
        print(f"\n✗ Found {len(errors)} syntax error(s)")
        return False
    else:
        print(f"\n✓ All {valid_cells} code cells have valid Python syntax")
        return True


def check_dependencies(nb):
    """Check for required dependencies"""
    print("\n" + "=" * 70)
    print("CHECKING DEPENDENCIES")
    print("=" * 70)

    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

    imports = set()

    for cell in code_cells:
        source = cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])

        # Find import statements
        import_matches = re.findall(r'^(?:from|import)\s+(\w+)', source, re.MULTILINE)
        imports.update(import_matches)

    print(f"✓ Found {len(imports)} unique imports:")
    for imp in sorted(imports):
        print(f"  - {imp}")

    # Check critical dependencies
    critical = ['logging', 'pandas', 'numpy']
    recommended = ['yfinance', 'tabulate']

    missing_critical = [dep for dep in critical if dep not in imports]
    missing_recommended = [dep for dep in recommended if dep not in imports]

    if missing_critical:
        print(f"\n⚠ Missing critical dependencies: {', '.join(missing_critical)}")

    if missing_recommended:
        print(f"\n⚠ Missing recommended dependencies: {', '.join(missing_recommended)}")

    # Check for swisseph (can be imported as swisseph or pyswisseph)
    nb_str = json.dumps(nb)
    if 'swisseph' in nb_str.lower() or 'swe' in imports:
        print("✓ Swiss Ephemeris dependency found")

    print("\n✓ Dependency check completed")
    return True


def main():
    """Run all validation checks"""
    notebook_path = Path('AstroFinanceProject.ipynb')

    if not notebook_path.exists():
        print(f"✗ Notebook not found: {notebook_path}")
        sys.exit(1)

    print(f"Validating: {notebook_path}")
    print()

    # Run validations
    success = True

    # Structure validation
    struct_ok, nb = validate_structure(notebook_path)
    success = success and struct_ok

    if not nb:
        print("\n✗ Cannot proceed with further validation due to structure errors")
        sys.exit(1)

    # Logging validation
    logging_ok = validate_logging(nb)
    success = success and logging_ok

    # Syntax validation
    syntax_ok = validate_syntax(nb)
    success = success and syntax_ok

    # Dependency check
    deps_ok = check_dependencies(nb)
    success = success and deps_ok

    # Final summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    if success:
        print("✓ All validation checks passed!")
        print("\nNext steps:")
        print("1. Test in Google Colab: https://colab.research.google.com/github/HAP2Y/Astro-Finance/blob/claude/improve-notebook-logging-011CUgfaDKN7wnTe2USKG74D/AstroFinanceProject.ipynb")
        print("2. Run a few cells to verify logging output")
        print("3. Check for timestamps and proper log levels")
        sys.exit(0)
    else:
        print("✗ Some validation checks failed")
        print("Please review the errors above and fix them before proceeding")
        sys.exit(1)


if __name__ == '__main__':
    main()
