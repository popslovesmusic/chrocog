#!/usr/bin/env python3
"""
Automated Print to Logging Converter
Converts print() statements to proper logging calls
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def detect_log_level(print_content: str) -> str:
    """Detect appropriate log level from print content"""
    content_lower = print_content.lower()

    # Error patterns
    if any(word in content_lower for word in ['error', 'failed', 'exception', 'critical']):
        return 'error'

    # Warning patterns
    if any(word in content_lower for word in ['warning', 'warn', 'deprecated', 'caution']):
        return 'warning'

    # Debug patterns
    if any(word in content_lower for word in ['debug', 'trace', 'dump', 'verbose']):
        return 'debug'

    # Default to info
    return 'info'


def convert_print_to_logging(line: str, indent: str = '') -> str:
    """Convert a single print statement to logging"""

    # Match print(...) statements
    print_pattern = r'print\((.*?)\)(?:\s*#.*)?$'
    match = re.search(print_pattern, line)

    if not match:
        return line

    content = match.group(1).strip()

    # Detect log level
    log_level = detect_log_level(content)

    # Handle f-strings: convert to % formatting
    if content.startswith(('f"', "f'")):
        # Simple f-string: f"text {var}" -> "text %s", var
        # This is simplified - complex f-strings need manual review
        fstring_content = content[2:-1]  # Remove f" and "

        # Replace {var} with %s and extract variables
        vars_found = re.findall(r'\{([^}]+)\}', fstring_content)
        if vars_found:
            # Replace all {var} with %s
            formatted = re.sub(r'\{[^}]+\}', '%s', fstring_content)
            vars_str = ', ' + ', '.join(vars_found)
            new_line = f'{indent}logger.{log_level}("{formatted}"{vars_str})'
        else:
            # No variables, just a string
            new_line = f'{indent}logger.{log_level}("{fstring_content}")'

    # Handle regular strings
    elif content.startswith(('"', "'")):
        new_line = f'{indent}logger.{log_level}({content})'

    # Handle expressions
    else:
        # Wrap in str() if complex expression
        new_line = f'{indent}logger.{log_level}(str({content}))'

    return new_line


def add_logging_import(file_content: str, module_name: str) -> str:
    """Add logging import and logger setup if not present"""

    if 'import logging' in file_content:
        return file_content

    lines = file_content.split('\n')

    # Find where to insert (after docstring, before other imports)
    insert_pos = 0
    in_docstring = False

    for i, line in enumerate(lines):
        # Skip module docstring
        if i == 0 and line.strip().startswith('"""'):
            in_docstring = True
            continue
        if in_docstring and '"""' in line:
            in_docstring = False
            insert_pos = i + 1
            continue
        if in_docstring:
            continue

        # Found first import
        if line.strip().startswith(('import ', 'from ')):
            insert_pos = i
            break

    # Insert logging import and logger
    logging_lines = [
        'import logging',
        '',
        f'logger = logging.getLogger(__name__)',
        ''
    ]

    lines[insert_pos:insert_pos] = logging_lines

    return '\n'.join(lines)


def convert_file(file_path: Path, dry_run: bool = True) -> Tuple[int, int]:
    """Convert all prints in a file to logging"""

    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        lines = content.split('\n')
        converted_count = 0

        # Convert print statements
        new_lines = []
        for line in lines:
            if 'print(' in line and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                new_line = convert_print_to_logging(line, indent_str)
                if new_line != line:
                    converted_count += 1
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        if converted_count == 0:
            return 0, 0

        new_content = '\n'.join(new_lines)

        # Add logging import
        module_name = file_path.stem
        new_content = add_logging_import(new_content, module_name)

        if not dry_run:
            # Backup original
            backup_path = file_path.with_suffix('.py.bak')
            file_path.write_text(original_content, encoding='utf-8')
            backup_path.write_text(original_content, encoding='utf-8')

            # Write new content
            file_path.write_text(new_content, encoding='utf-8')

        return converted_count, 1

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, 0


def main():
    """Main conversion script"""
    import argparse

    parser = argparse.ArgumentParser(description='Convert print() to logging')
    parser.add_argument('path', help='Directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--file', help='Process single file')

    args = parser.parse_args()

    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            count, files = convert_file(file_path, dry_run=args.dry_run)
            print(f"Converted {count} print statements in {file_path}")
    else:
        path = Path(args.path)
        total_converted = 0
        total_files = 0

        for py_file in path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue

            count, files = convert_file(py_file, dry_run=args.dry_run)
            if count > 0:
                total_converted += count
                total_files += files
                status = '(DRY RUN)' if args.dry_run else '(CONVERTED)'
                print(f"{status} {py_file.name}: {count} prints -> logging")

        print(f"\nTotal: {total_converted} prints in {total_files} files")
        if args.dry_run:
            print("Run without --dry-run to apply changes")


if __name__ == '__main__':
    main()
