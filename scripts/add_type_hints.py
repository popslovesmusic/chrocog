#!/usr/bin/env python3
"""
Add Type Hints to Python Code
Uses AST parsing to add intelligent type hints
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Common type mappings
TYPE_MAPPINGS = {
    # Parameter name patterns -> types
    'buffer': 'np.ndarray',
    'data': 'np.ndarray',
    'array': 'np.ndarray',
    'matrix': 'np.ndarray',
    'signal': 'np.ndarray',
    'samples': 'np.ndarray',

    'config': 'Dict',
    'settings': 'Dict',
    'params': 'Dict',
    'options': 'Dict',
    'metadata': 'Dict',

    'name': 'str',
    'path': 'str',
    'filename': 'str',
    'message': 'str',
    'text': 'str',
    'content': 'str',

    'count': 'int',
    'size': 'int',
    'length': 'int',
    'index': 'int',
    'id': 'int',
    'port': 'int',

    'rate': 'float',
    'value': 'float',
    'threshold': 'float',
    'alpha': 'float',
    'beta': 'float',
    'gamma': 'float',

    'enabled': 'bool',
    'enable': 'bool',
    'flag': 'bool',
    'active': 'bool',
}

# Return type patterns
RETURN_PATTERNS = {
    'get_': 'Optional[Any]',
    'is_': 'bool',
    'has_': 'bool',
    'can_': 'bool',
    'should_': 'bool',
    'check_': 'bool',
    'validate_': 'bool',
    'compute_': 'float',
    'calculate_': 'float',
    'create_': 'Any',
    'build_': 'Any',
}


class TypeHintAdder:
    """Add type hints to Python code"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = file_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.modified = False

    def add_typing_import(self) -> None:
        """Add typing imports if not present"""
        needed_imports = set()

        # Check what we might need
        if 'Dict' in self.content and 'from typing import' not in self.content:
            needed_imports.add('Dict')
        if 'List' in self.content:
            needed_imports.add('List')
        if 'Optional' in self.content:
            needed_imports.add('Optional')

        if not needed_imports:
            needed_imports = {'Dict', 'List', 'Optional', 'Any', 'Tuple'}

        if needed_imports and 'from typing import' not in self.content:
            # Find insertion point
            for i, line in enumerate(self.lines):
                if line.startswith('import ') and not line.startswith('import logging'):
                    import_line = f"from typing import {', '.join(sorted(needed_imports))}"
                    self.lines.insert(i, import_line)
                    self.modified = True
                    break

    def infer_param_type(self, param_name: str) -> str:
        """Infer type from parameter name"""
        param_name_lower = param_name.lower()

        # Check exact matches
        if param_name_lower in TYPE_MAPPINGS:
            return TYPE_MAPPINGS[param_name_lower]

        # Check contains patterns
        if 'list' in param_name_lower or param_name_lower.endswith('s'):
            return 'List'
        if 'dict' in param_name_lower or 'config' in param_name_lower:
            return 'Dict'
        if 'path' in param_name_lower:
            return 'str'
        if 'count' in param_name_lower or 'num' in param_name_lower:
            return 'int'

        return 'Any'

    def infer_return_type(self, func_name: str, func_body: str) -> str:
        """Infer return type from function"""
        # Check for explicit return None
        if 'return None' in func_body:
            return 'None'

        # Check if no return statement
        if 'return' not in func_body:
            return 'None'

        # Check patterns
        for pattern, ret_type in RETURN_PATTERNS.items():
            if func_name.startswith(pattern):
                return ret_type

        # Check return statements
        if 'return True' in func_body or 'return False' in func_body:
            return 'bool'
        if 'return {}' in func_body or 'return dict(' in func_body:
            return 'Dict'
        if 'return []' in func_body or 'return list(' in func_body:
            return 'List'

        return 'Any'

    def add_hints_to_function(self, line_idx: int) -> bool:
        """Add type hints to a function definition"""
        line = self.lines[line_idx]

        # Already has type hints
        if '->' in line:
            return False

        # Skip special methods (except __init__)
        if '__' in line and '__init__' not in line:
            return False

        # Parse function signature
        match = re.match(r'(\s*)def\s+(\w+)\((.*?)\):?', line)
        if not match:
            return False

        indent, func_name, params_str = match.groups()

        # Get function body to analyze
        func_body_lines = []
        for i in range(line_idx + 1, min(line_idx + 30, len(self.lines))):
            if self.lines[i].strip() and not self.lines[i].strip().startswith(('"""', "'''", '#')):
                func_body_lines.append(self.lines[i])
            if self.lines[i].strip().startswith('def '):
                break
        func_body = '\n'.join(func_body_lines)

        # Parse parameters
        params = [p.strip() for p in params_str.split(',') if p.strip()]
        if not params:
            # No parameters, just add return type
            return_type = self.infer_return_type(func_name, func_body)
            new_line = f"{indent}def {func_name}() -> {return_type}:"
            self.lines[line_idx] = new_line
            return True

        # Add types to parameters
        typed_params = []
        for param in params:
            if '=' in param:
                # Has default value
                param_name, default = param.split('=', 1)
                param_name = param_name.strip()
                default = default.strip()

                if param_name == 'self':
                    typed_params.append('self')
                elif param_name == 'cls':
                    typed_params.append('cls')
                else:
                    param_type = self.infer_param_type(param_name)
                    typed_params.append(f"{param_name}: {param_type} = {default}")
            else:
                # No default
                if param == 'self':
                    typed_params.append('self')
                elif param == 'cls':
                    typed_params.append('cls')
                else:
                    param_type = self.infer_param_type(param)
                    typed_params.append(f"{param}: {param_type}")

        # Infer return type
        return_type = self.infer_return_type(func_name, func_body)

        # Reconstruct function signature
        params_joined = ', '.join(typed_params)
        new_line = f"{indent}def {func_name}({params_joined}) -> {return_type}:"

        self.lines[line_idx] = new_line
        self.modified = True
        return True

    def process_file(self) -> int:
        """Process entire file"""
        count = 0

        for i, line in enumerate(self.lines):
            if line.strip().startswith('def '):
                if self.add_hints_to_function(i):
                    count += 1

        if count > 0:
            self.add_typing_import()

        return count

    def save(self, backup: bool = True) -> None:
        """Save modifications"""
        if not self.modified:
            return

        if backup:
            backup_path = self.file_path.with_suffix('.py.typehints.backup')
            backup_path.write_text(self.content, encoding='utf-8')

        new_content = '\n'.join(self.lines)
        self.file_path.write_text(new_content, encoding='utf-8')


def add_type_hints_to_file(file_path: Path) -> int:
    """Add type hints to a file"""
    try:
        adder = TypeHintAdder(file_path)
        count = adder.process_file()
        if count > 0:
            adder.save(backup=True)
        return count
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return 0


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Add type hints')
    parser.add_argument('directory', help='Directory to process')
    args = parser.parse_args()

    directory = Path(args.directory)
    total_funcs = 0
    total_files = 0

    logger.info("Adding type hints...")

    for py_file in sorted(directory.glob('*.py')):
        if py_file.name.startswith('__'):
            continue

        count = add_type_hints_to_file(py_file)
        if count > 0:
            total_files += 1
            total_funcs += count
            logger.info(f"{py_file.name}: {count} functions")

    logger.info(f"\nComplete: {total_funcs} functions in {total_files} files")


if __name__ == '__main__':
    main()
