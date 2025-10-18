import os, re, shutil

SRC_DIR = "server"
OUT_DIR = "server_clean"

# Start fresh
if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

# Regex patterns for type hints and return annotations
param_hint = re.compile(r":\s*[^,\)\:]+(?=[,\)])")
return_hint = re.compile(r"->\s*[^:]+(?=\s*:)")

def clean_types(content):
    # Remove inline param hints
    content = param_hint.sub("", content)
    # Remove return hints
    content = return_hint.sub("", content)
    return content

for root, _, files in os.walk(SRC_DIR):
    rel_root = os.path.relpath(root, SRC_DIR)
    out_root = os.path.join(OUT_DIR, rel_root)
    os.makedirs(out_root, exist_ok=True)

    for f in files:
        if f.endswith(".py"):
            src_path = os.path.join(root, f)
            out_path = os.path.join(out_root, f)

            with open(src_path, "r", encoding="utf-8") as src:
                code = src.read()
            cleaned = clean_types(code)
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(cleaned)

            print(f"Cleaned: {src_path} -> {out_path}")

print("\n✅ Type hints stripped. Review cleaned code in 'server_clean/' before replacing originals.")
