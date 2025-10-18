import os
import re

def fix_unbalanced_docstrings(base_dir="server"):
    """
    Detects and closes any unbalanced triple-quoted docstrings in .py files.
    Adds a closing triple quote at the end of the file if needed.
    """
    pattern = re.compile(r'"""|\'\'\'')
    fixed_files = []

    for root, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(root, fname)
            with open(path, encoding="utf-8") as f:
                content = f.read()

            quotes = pattern.findall(content)
            if len(quotes) % 2 != 0:
                # Automatically close the last block
                content += '\n"""  # auto-closed missing docstring\n'
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                fixed_files.append(path)

    if not fixed_files:
        print("✅ All files already balanced.")
    else:
        print("🩹 Fixed unbalanced triple quotes in:")
        for f in fixed_files:
            print(" -", f)

if __name__ == "__main__":
    print("=== Auto-Repair Unbalanced Docstrings ===")
    fix_unbalanced_docstrings("server")
