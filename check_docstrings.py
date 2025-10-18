import os
import re

def find_unbalanced_triple_quotes(base_dir="server"):
    """Scans for unterminated or mismatched triple-quoted strings in all .py files."""
    pattern = re.compile(r'"""|\'\'\'')
    issues = []

    for root, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(root, fname)
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                quotes = pattern.findall(content)
                if len(quotes) % 2 != 0:
                    issues.append(path)
            except Exception as e:
                issues.append(f"{path} (error reading file: {e})")

    if not issues:
        print("✅ All triple-quoted strings appear balanced.")
    else:
        print("⚠️ Unbalanced triple-quoted strings found in:")
        for issue in issues:
            print(f" - {issue}")

if __name__ == "__main__":
    print("=== Docstring Balance Checker ===")
    find_unbalanced_triple_quotes("server")
