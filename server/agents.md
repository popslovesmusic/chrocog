Perfect — that’s the right next step.
Here’s an **`agents.md`** you can drop beside your `cleanup.diff` prompt or inside your `server/` folder.
It gives Codex (or any code-generation agent) an explicit *constitution and division of labor* for the refactor, so it can act predictably and produce structured diff patches instead of rewriting blindly.

---

## 🧩 **agents.md — Modular Refactor Authority**

### ⚙️ Mission

This repository contains the **Soundlab / Chrocog Analysis Suite Core**, including:

* A multi-layer FastAPI backend,
* D-ASE AVX2 compute engine,
* Snapshot, preset, and metrics modules.

The goal is to **decompose monolithic scripts into cohesive, testable modules** while preserving runtime behavior and REST compatibility.

Each agent operates under strict **diff-patch discipline** — all output must be valid, self-contained Git patches ready for safe application via:

```bash
apply-diff-safe.ps1 <patch>.diff
```

---

### 🧠 Core Philosophy

1. **No blind rewrites.**
   Every change must appear as a minimal diff.
2. **No functional drift.**
   Do not rename endpoints, parameters, or file entrypoints.
3. **No duplicated initialization.**
   The FastAPI `app` object and D-ASE engine loader must exist **only once**.
4. **Relative imports only.**
   Use `from .module import …` for all internal code.
5. **Keep startup logging** (`🧭 Loaded main.py`, CPU feature prints) intact for operator feedback.

---

### 🧩 Agent Roles

#### 🧱 **Agent A — Structure Analyst**

* Scans `main.py` and identifies separable logical blocks:

  * D-ASE Engine loader
  * FastAPI setup
  * Core endpoints
  * Utility endpoints
  * UI serving logic
  * Class `SoundlabServer`
* Produces a **Refactor Plan Table** mapping line ranges → new module names.

#### 🪚 **Agent B — Extractor**

* Executes the plan from Agent A.
* Generates the **diff patch** splitting each region into new files:

  ```
  server/
    ├── init_engine.py
    ├── init_app.py
    ├── routes_core.py
    ├── routes_health.py
    ├── soundlab_server.py
  ```
* Rewrites `main.py` to become a clean entrypoint:

  ```python
  from .init_engine import init_engine
  from .init_app import create_app

  app = create_app()
  init_engine()
  ```

#### 🧩 **Agent C — Dependency Auditor**

* Ensures all new modules import each other correctly.
* Verifies FastAPI routers attach properly to the shared `app` object.
* Confirms the entrypoint still runs with:

  ```
  uvicorn server.main:app --reload
  ```

#### 🧪 **Agent D — Patch Validator**

* Validates syntax (`python -m py_compile`) and checks that `git apply --check` passes.
* Ensures no semantic regressions (no removed route decorators, no doubled imports).

---

### 🧾 Output Policy

Every operation must output a valid, minimal **Git diff** of the form:

```
diff --git a/server/main.py b/server/main.py
index <hash>..<hash> 100644
--- a/server/main.py
+++ b/server/main.py
@@ -NNN,MMM +NNN,MMM @@
<changes>
```

Nothing else — no commentary, markdown, or extra text.

---

### ✅ Completion Checklist

| Area                 | Must Exist | Notes                                    |
| -------------------- | ---------- | ---------------------------------------- |
| `init_engine.py`     | ✅          | Contains D-ASE loader and feature check  |
| `init_app.py`        | ✅          | Creates and returns FastAPI `app`        |
| `routes_core.py`     | ✅          | `/` and `/engine/status` endpoints       |
| `routes_health.py`   | ⚙️         | Optional system diagnostics              |
| `soundlab_server.py` | ✅          | `SoundlabServer` class and wiring        |
| `main.py`            | ✅          | Entry point importing from above modules |
| Patch Valid          | ✅          | Passes `git apply --check` and compiles  |

---

### 🧭 Directive Summary

> “Refactor methodically, preserve every route and log, split by functional cohesion, and output only clean, verifiable diffs.”

---

Would you like me to include an **example table** inside this file showing which `main.py` sections (by approximate line ranges) map to which new modules — so Codex can parse it as a ready blueprint?
