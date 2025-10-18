import os, re

root = "server"

print("🧹 Starting automated syntax repair for:", root)

for dirpath, _, files in os.walk(root):
    for f in files:
        if not f.endswith(".py"):
            continue
        path = os.path.join(dirpath, f)
        with open(path, encoding="utf-8", errors="ignore") as infile:
            text = infile.read()

        original = text

        # --- Fix invalid class headers ---
        text = re.sub(r"class\s+([A-Za-z_][A-Za-z0-9_]*)\s*,.*", r"class \1:", text)

        # --- Remove broken doc fragments like "Handles)" or "Config)" ---
        text = re.sub(r"(?m)^\s*(Handles|Returns|Features|Config|Records|Stores|- .*)\)\s*$", "", text)

        # --- Remove unmatched ')' on its own line ---
        text = re.sub(r"(?m)^\s*\)\s*$", "", text)

        # --- Fix doubled or misplaced parentheses ---
        text = re.sub(r"\)\s*:\s*\)", "):", text)
        text = re.sub(r"\)\s*\)\s*:", "):", text)

        # --- Fix unclosed print / f-strings ---
        text = re.sub(r"print\((f?\"[^\"]*?)\)$", r"print(\1)\n", text)
        text = re.sub(r"logger\.info\((f?\"[^\"]*?)\)$", r"logger.info(\1)\n", text)

        # --- Normalize tabs/spaces ---
        text = text.replace("\t", "    ")

        if text != original:
            with open(path, "w", encoding="utf-8") as outfile:
                outfile.write(text)
            print(f"✅ Repaired {path}")

print("\n✨ Repair complete. Now run: python -m compileall server")
