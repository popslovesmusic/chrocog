"""
Fix Format String Syntax Errors
Corrects invalid format specifications in logger calls from automated refactoring.

Fixes patterns like:
  logger.info("Value: %s", variable:.2f)  # WRONG
to:
  logger.info("Value: %.2f", variable)   # CORRECT
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def fix_format_string_error(line: str) -> str:
    """
    Fix format string syntax errors in logger calls.

    Handles patterns like:
    - logger.info("text %s", var:.2f)  -> logger.info("text %.2f", var)
    - logger.debug("text %s", var:.1f) -> logger.debug("text %.1f", var)
    - logger.warning("text %s", var:d) -> logger.warning("text %d", var)
    """

    # Pattern: logger.LEVEL("format string", args_with_format_specs)
    # Match logger calls with format specs like var:.2f, var:.1f, etc.
    pattern = r'(logger\.\w+\(["\'].*?)(%s)(.*?["\'],\s*)(\w+)(:[\.0-9df]+)(\))'

    def replace_func(match):
        prefix = match.group(1)  # logger.info("...
        format_s = match.group(2)  # %s
        middle = match.group(3)   # ..." ,
        var_name = match.group(4)  # variable
        format_spec = match.group(5)  # :.2f
        suffix = match.group(6)  # )

        # Convert format spec to % format
        # :.2f -> %.2f, :.1f -> %.1f, :d -> %d
        new_format = '%' + format_spec[1:]  # Remove : and add %

        # Build corrected line
        return f"{prefix}{new_format}{middle}{var_name}{suffix}"

    # Apply multiple times for multiple occurrences in same line
    prev_line = ""
    max_iterations = 10
    iteration = 0

    while line != prev_line and iteration < max_iterations:
        prev_line = line
        line = re.sub(pattern, replace_func, line)
        iteration += 1

    # Also handle cases with multiple variables in same call
    # logger.info("A: %s B: %s", var1:.2f, var2:.1f)
    pattern2 = r'(\w+)(:[\.0-9df]+)([,\)])'

    def replace_format_spec(match):
        var_name = match.group(1)
        format_spec = match.group(2)  # :.2f
        suffix = match.group(3)  # , or )

        # Just remove the format spec from variable
        return f"{var_name}{suffix}"

    # Fix remaining format specs on variables
    if ':.' in line or ':d' in line:
        # First, extract and fix the format string part
        if 'logger.' in line and '(' in line:
            parts = line.split('",', 1)
            if len(parts) == 2:
                format_part = parts[0] + '"'
                args_part = parts[1]

                # Fix format string
                format_part = format_part.replace('%s', '%FORMAT_PLACEHOLDER%')

                # Count format specs in args
                format_specs = re.findall(r':[\.0-9df]+', args_part)

                # Replace placeholders with proper format codes
                for spec in format_specs:
                    format_code = '%' + spec[1:]  # :.2f -> %.2f
                    format_part = format_part.replace('%FORMAT_PLACEHOLDER%', format_code, 1)

                # Remove remaining placeholders (use %s)
                format_part = format_part.replace('%FORMAT_PLACEHOLDER%', '%s')

                # Remove format specs from arguments
                args_part = re.sub(r':[\.0-9df]+', '', args_part)

                line = format_part + ',' + args_part

    return line


def fix_file(file_path: Path) -> Tuple[bool, int]:
    """
    Fix format string errors in a single file.

    Returns:
        (changed, num_fixes) tuple
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"ERROR reading {file_path}: {e}")
        return False, 0

    fixed_lines = []
    num_fixes = 0

    for line_num, line in enumerate(lines, 1):
        original = line

        # Only process lines with logger calls and format specs
        if 'logger.' in line and (':.' in line or ':d' in line):
            fixed = fix_format_string_error(line)
            if fixed != original:
                num_fixes += 1
                print(f"  Line {line_num}: Fixed format spec")
                fixed_lines.append(fixed)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    if num_fixes > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return True, num_fixes
        except Exception as e:
            print(f"ERROR writing {file_path}: {e}")
            return False, 0

    return False, 0


def main():
    """Fix all Python files in server directory"""
    server_dir = Path(__file__).parent.parent / "server"

    if not server_dir.exists():
        print(f"ERROR: Server directory not found: {server_dir}")
        return 1

    print("=" * 60)
    print("Format String Syntax Fix")
    print("=" * 60)
    print(f"Scanning: {server_dir}")
    print()

    python_files = list(server_dir.rglob("*.py"))
    print(f"Found {len(python_files)} Python files")
    print()

    total_fixed = 0
    total_files_changed = 0

    for py_file in python_files:
        changed, num_fixes = fix_file(py_file)
        if changed:
            total_files_changed += 1
            total_fixed += num_fixes
            print(f"✓ {py_file.relative_to(server_dir)}: {num_fixes} fixes")

    print()
    print("=" * 60)
    print(f"Summary: {total_fixed} fixes in {total_files_changed} files")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
