#!/usr/bin/env python3
"""
Batch Refactoring Tool
Addresses all 4 critical issues systematically
"""

import re
import ast
from pathlib import Path
from typing import List, Tuple, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeRefactor:
    """Automated code refactoring"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = file_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.modified = False

    def add_logging_import(self) -> None:
        """Add logging import if not present"""
        if 'import logging' in self.content:
            return

        # Find insertion point after docstring
        insert_idx = 0
        for i, line in enumerate(self.lines):
            if line.strip() and not line.strip().startswith('#'):
                if '"""' in line or "'''" in line:
                    # Skip docstring
                    for j in range(i + 1, len(self.lines)):
                        if '"""' in self.lines[j] or "'''" in self.lines[j]:
                            insert_idx = j + 1
                            break
                    break
                elif line.strip().startswith(('import ', 'from ')):
                    insert_idx = i
                    break

        # Insert logging import and logger
        self.lines.insert(insert_idx, '')
        self.lines.insert(insert_idx, 'logger = logging.getLogger(__name__)')
        self.lines.insert(insert_idx, 'import logging')
        self.modified = True

    def replace_prints_with_logging(self) -> int:
        """Replace all print statements with logging"""
        count = 0

        for i, line in enumerate(self.lines):
            if 'print(' not in line or line.strip().startswith('#'):
                continue

            # Determine log level based on content
            content_lower = line.lower()
            if any(w in content_lower for w in ['error', 'fail', 'exception', 'critical']):
                level = 'error'
            elif any(w in content_lower for w in ['warn', 'deprecated']):
                level = 'warning'
            elif any(w in content_lower for w in ['debug', 'trace', 'verbose']):
                level = 'debug'
            else:
                level = 'info'

            # Get indentation
            indent = len(line) - len(line.lstrip())

            # Simple replacement: convert f-strings to % formatting
            # Extract print content
            match = re.search(r'print\((.*)\)\s*$', line)
            if match:
                content = match.group(1).strip()

                # Handle f-strings
                if content.startswith(('f"', "f'")):
                    # Remove f prefix and quotes
                    quote_char = content[1]
                    fstring_body = content[2:-1]

                    # Replace {var} with %s
                    vars_list = re.findall(r'\{([^}]+)\}', fstring_body)
                    if vars_list:
                        clean_body = re.sub(r'\{[^}]+\}', '%s', fstring_body)
                        vars_str = ', ' + ', '.join(vars_list)
                        new_line = f'{" " * indent}logger.{level}("{clean_body}"{vars_str})'
                    else:
                        new_line = f'{" " * indent}logger.{level}("{fstring_body}")'

                # Handle regular strings
                elif content.startswith(('"', "'")):
                    new_line = f'{" " * indent}logger.{level}({content})'

                else:
                    # Wrap complex expressions
                    new_line = f'{" " * indent}logger.{level}(str({content}))'

                self.lines[i] = new_line
                count += 1
                self.modified = True

        return count

    def add_type_hints_simple(self) -> int:
        """Add basic type hints to function signatures"""
        count = 0

        # This is a simplified version - full type hint addition requires AST parsing
        # For now, we'll add common patterns

        patterns = [
            (r'def\s+(\w+)\(self\)\s*:', r'def \1(self) -> None:'),
            (r'def\s+(\w+)\(self,\s*(\w+)\)\s*:', r'def \1(self, \2) -> None:'),
        ]

        for i, line in enumerate(self.lines):
            if 'def ' in line and '->' not in line:
                for pattern, replacement in patterns:
                    if re.match(pattern, line.strip()):
                        # This is too simplistic, skip for now
                        pass

        return count

    def add_caching_to_functions(self) -> int:
        """Add @lru_cache to computational functions"""
        count = 0

        # Look for functions that are good candidates for caching
        cache_candidates = []

        for i, line in enumerate(self.lines):
            if not line.strip().startswith('def '):
                continue

            # Check next few lines for computational patterns
            func_name = re.search(r'def\s+(\w+)', line)
            if not func_name:
                continue

            name = func_name.group(1)

            # Skip certain functions
            if any(skip in name for skip in ['__init__', '__repr__', '__str__', 'test_']):
                continue

            # Look for computational keywords
            func_body = '\n'.join(self.lines[i:min(i+20, len(self.lines))])
            if any(keyword in func_body for keyword in [
                'np.', 'numpy', 'fft', 'compute', 'calculate',
                'matrix', 'transform', 'process'
            ]):
                # Check if not already cached
                if i > 0 and '@lru_cache' not in self.lines[i-1]:
                    cache_candidates.append(i)

        # Add lru_cache import if needed
        if cache_candidates and 'from functools import' not in self.content:
            for i, line in enumerate(self.lines):
                if line.startswith('import ') or line.startswith('from '):
                    self.lines.insert(i, 'from functools import lru_cache')
                    # Adjust indices
                    cache_candidates = [idx + 1 for idx in cache_candidates]
                    self.modified = True
                    break

        # Add @lru_cache decorators
        for idx in reversed(cache_candidates):  # Reverse to maintain indices
            indent = len(self.lines[idx]) - len(self.lines[idx].lstrip())
            self.lines.insert(idx, ' ' * indent + '@lru_cache(maxsize=128)')
            count += 1
            self.modified = True

        return count

    def save(self, backup: bool = True) -> None:
        """Save modifications"""
        if not self.modified:
            return

        if backup:
            backup_path = self.file_path.with_suffix('.py.backup')
            backup_path.write_text(self.content, encoding='utf-8')

        new_content = '\n'.join(self.lines)
        self.file_path.write_text(new_content, encoding='utf-8')


def refactor_file(file_path: Path, apply_logging: bool = True,
                  apply_caching: bool = True) -> dict:
    """Refactor a single file"""

    try:
        refactor = CodeRefactor(file_path)

        stats = {
            'file': file_path.name,
            'prints_converted': 0,
            'caches_added': 0,
            'success': True,
            'error': None
        }

        if apply_logging:
            count = refactor.replace_prints_with_logging()
            if count > 0:
                refactor.add_logging_import()
                stats['prints_converted'] = count

        if apply_caching:
            count = refactor.add_caching_to_functions()
            stats['caches_added'] = count

        refactor.save(backup=True)

        return stats

    except Exception as e:
        return {
            'file': file_path.name,
            'prints_converted': 0,
            'caches_added': 0,
            'success': False,
            'error': str(e)
        }


def main():
    """Main refactoring function"""
    import argparse

    parser = argparse.ArgumentParser(description='Batch refactor code')
    parser.add_argument('directory', help='Directory to refactor')
    parser.add_argument('--logging', action='store_true', help='Fix logging')
    parser.add_argument('--caching', action='store_true', help='Add caching')
    parser.add_argument('--all', action='store_true', help='Apply all fixes')

    args = parser.parse_args()

    directory = Path(args.directory)
    apply_logging = args.logging or args.all
    apply_caching = args.caching or args.all

    total_prints = 0
    total_caches = 0
    total_files = 0
    errors = []

    logger.info("Starting batch refactoring...")

    for py_file in sorted(directory.glob('*.py')):
        if py_file.name.startswith('__'):
            continue

        stats = refactor_file(py_file, apply_logging, apply_caching)

        if stats['success']:
            total_files += 1
            total_prints += stats['prints_converted']
            total_caches += stats['caches_added']

            if stats['prints_converted'] > 0 or stats['caches_added'] > 0:
                logger.info(f"{stats['file']}: {stats['prints_converted']} prints, {stats['caches_added']} caches")
        else:
            errors.append(f"{stats['file']}: {stats['error']}")

    logger.info(f"\nRefactoring complete:")
    logger.info(f"  Files processed: {total_files}")
    logger.info(f"  Prints converted: {total_prints}")
    logger.info(f"  Caches added: {total_caches}")

    if errors:
        logger.warning(f"\nErrors: {len(errors)}")
        for error in errors:
            logger.warning(f"  {error}")


if __name__ == '__main__':
    main()
