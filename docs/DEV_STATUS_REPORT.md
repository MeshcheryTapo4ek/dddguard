# DDDGuard — Development Status Report

> **Date:** 2026-02-12 | **Version:** 1.0.1

This document contains a full audit of the current project state: implemented features, fixed bugs, test coverage gaps, and recommendations for priority improvements.

---

## Table of Contents

1. [Feature Inventory](#1-feature-inventory)
2. [Fixed Bugs (This Audit)](#2-fixed-bugs-this-audit)
3. [Test Coverage](#3-test-coverage)
4. [Architecture Compliance](#4-architecture-compliance)
5. [Documentation Gaps](#5-documentation-gaps)
6. [Recommendations (Priority Plan)](#6-recommendations-priority-plan)

---

## 1. Feature Inventory

### Overview by Context

| Context | Status | Commands | Notes |
|----------|--------|---------|------------|
| **Root (HUD)** | Implemented | `dddguard` (no args) | Interactive menu, all flows connected |
| **Scanner** | Implemented | `scan`, `scandir`, `classify`, `classifydir` | Full pipeline: detection -> classification -> filtering -> expansion |
| **Linter** | Implemented | `lint`, `lintdir` | 5 rules, wizard, Rules Matrix, report |
| **Visualizer** | Implemented | `draw`, `drawdir` | Draw.io diagrams, towers, legend |
| **Scaffolder** | Implemented | `init` | Creates config.yaml |

### Feature Details

| Feature | Status | Files | Details |
|------|--------|-------|--------|
| **Interactive HUD** | Implemented | `root/cli.py` | Full menu with dynamic items, scan history |
| **Scan Project** | Implemented | `scanner/app/use_cases/run_scan_uc.py` | Full pipeline with filters, BFS expansion |
| **Scan Directory** | Implemented | `scanner/adapters/driving/console/cli.py` | Interactive directory picker + wizard |
| **Classify Project** | Implemented | `scanner/app/use_cases/inspect_tree_uc.py` | No filtering, Rich table |
| **Classify Directory** | Implemented | `scanner/adapters/driving/console/cli.py` | Interactive picker + Rich table |
| **Discover Contexts** | Implemented | `scanner/app/use_cases/discover_contexts_uc.py` | For scanner wizard (auto-discovery) |
| **Scan Wizard** | Implemented | `scanner/adapters/driving/console/wizard.py` | Dashboard + strategies + filters + multiselect |
| **Config Viewer** | Implemented | `scanner/adapters/driving/console/wizard.py` | "Check Configuration" item in scanner wizard |
| **Repeat Last Scan** | Implemented | `scanner/adapters/driving/console/session_state.py` | Session state, HUD item |
| **JSON Export** | Implemented | `scanner/adapters/driving/console/cli.py` | `project_tree.json`, content masking option |
| **Detection Pipeline** | Implemented | `scanner/detection/` | AST parsing, import resolution, recursive resolver |
| **Classification Pipeline** | Implemented | `scanner/classification/` | 5 stages: discovery -> coordinates -> prioritization -> matching |
| **Lint Project** | Implemented | `linter/app/check_project_uc.py` | 5 rules (R100, F101, F102, C201, C202) |
| **Lint Directory** | Implemented | `linter/adapters/driving/cli.py` | |
| **Lint Wizard** | Implemented | `linter/adapters/driving/lint_wizard.py` | Run / View Summary / View Matrix / Exit |
| **Rules Viewer (Matrix)** | Implemented | `linter/adapters/driving/rules_viewer.py` | Table + Cross-Context panels |
| **Rules Summary** | Implemented | `shared/assets/asset_help.py` | Text description of rules |
| **Lint Report** | Implemented | `linter/adapters/driving/cli.py` | Violations table with Rule/Context/Details |
| **Draw Project** | Implemented | `visualizer/app/workflows/draw_architecture_workflow.py` | Full pipeline: scan -> layout -> render |
| **Draw Directory** | Implemented | `visualizer/adapters/driving/cli.py` | |
| **Visualizer Wizard** | Implemented | `visualizer/adapters/driving/visualizer_wizard.py` | Filters, output file |
| **Draw.io Renderer** | Implemented | `visualizer/ports/driven/drawio/` | XML generation, towers, zones, edges |
| **Layout Engine** | Implemented | `visualizer/domain/services/` | Grouping, structure, topology optimization, zone layout, assembly |
| **Edge Routing** | Implemented | `visualizer/domain/services/edges/` | Color, routing, topology |
| **Architecture Legend** | Implemented | `shared/assets/asset_legend.py`, `html_templates_data.py` | HTML legend inside drawio |
| **Naming Cloud** | Implemented | `shared/assets/naming_cloud.py` | HTML tag cloud inside drawio |
| **Init Config** | Implemented | `scaffolder/app/create_config_uc.py` | Creates `docs/dddguard/config.yaml` |
| **DI Container (Dishka)** | Implemented | `root/composition.py`, `*/provider.py` | All contexts connected |
| **TUI (Rich + InquirerPy)** | Implemented | `shared/adapters/driving/console/tui.py` | Dashboard, spinner, select, multiselect, path picker, error_boundary |
| **Error Middleware** | Implemented | `shared/adapters/driving/console/tui.py` | `tui.error_boundary()` — centralized error handling for CLI flows |
| **Error Generics** | Implemented | `shared/helpers/generics/errors.py` | BaseDddError + 8 variants: Domain, App, Port (Driving/Driven), Adapter (Driving/Driven) |
| **Config Loader** | Implemented | `shared/adapters/driven/yaml_config_loader.py` | Auto-discovery, YAML parsing |
| **Shared Domain** | Implemented | `shared/domain/` | Enums, CodeGraph, ConfigVo, AccessPolicy, Registry |

---

## 2. Fixed Bugs (This Audit)

The following issues were identified and fixed during this audit:

### FIXED: BUG-001 — Linter ScannerAcl passed unknown parameters

**Severity:** CRITICAL (crash at runtime)

**File:** `src/dddguard/linter/ports/driven/scanner_acl.py`

**Before:** Call to `ScannerFacade.scan_project()` with parameters `include_root=True` and `include_shared=True`, which did not exist in the method signature. This would cause `TypeError` when running `dddguard lint` and `dddguard lintdir`.

**Fixed:** Removed non-existent parameters. Call aligned with `ScannerFacade.scan_project()` signature.

### FIXED: BUG-002 — Visualizer ScannerAcl passed unknown parameters

**Severity:** CRITICAL (crash at runtime)

**File:** `src/dddguard/visualizer/ports/driven/scanner_acl.py`

**Before:** Call to `ScannerFacade.scan_project()` with parameters `include_shared=True`, `include_root=True`, `file_tree_only=False` — none of which exist in the signature. This would cause `TypeError` when running `dddguard draw` and `dddguard drawdir`.

**Fixed:** Removed non-existent parameters. Only valid ones kept: `target_path`, `scan_all`, `import_depth`, `include_assets`.

### FIXED: BUG-003 — Incorrect type hint in CheckProjectUseCase

**Severity:** LOW

**File:** `src/dddguard/linter/app/check_project_uc.py`

**Before:** `def execute(self, root_path: Path) -> ViolationEvent` — type hint pointed to `ViolationEvent`, though the method returned `LinterReport`.

**Fixed:** Type hint changed to `-> LinterReport`.

### FIXED: Removed CreateComponentWizard stub

**File:** `src/dddguard/scaffolder/adapters/driving/create_wizard.py` (deleted)

**Before:** Class `CreateComponentWizard` with "STATUS: Not Implemented Yet", method `run()` returned `None`. The class was unused and gave a false impression of existing functionality.

**Fixed:** File deleted. "Create" section removed from README.md.

### FIXED: Reference to non-existent command `dddguard config`

**File:** `src/dddguard/scanner/adapters/driving/console/wizard.py`

**Before:** "Check Configuration" item in the scanner wizard displayed: `Config check skipped (Use 'dddguard config')`, but no such command existed.

**Fixed:** "Check Configuration" now shows the actual project configuration (root, source_dir, tests_dir, docs_dir, exclude/ignore rules) in a dashboard panel format.

### FIXED: Removed DTO layer from README

**File:** `README.md`

**Before:** README described `dto/` as part of the target architecture, but DDDGuard does not recognize it (not in `LayerEnum`).

**Fixed:** Removed references to `dto/` from the target architecture and layer descriptions in README.

### FIXED: Silent error handling in FileSystemRepository

**File:** `src/dddguard/scanner/detection/ports/driven/storage/file_system_repository.py`

**Before:**
- `get_subdirectories`: `except OSError: pass` — directory read errors were silently swallowed
- `_walk_pathlib`: `except (PermissionError, OSError): return` — inaccessible directories were silently skipped

**Fixed:** Both handlers now print a warning to stderr with the problematic path: `[dddguard] Warning: Cannot list directory '...': ...`

### FIXED: Swallowed discovery error in ScanSettingsWizard

**File:** `src/dddguard/scanner/adapters/driving/console/wizard.py`

**Before:** On discovery error, only `Discovery Failed: <error>` and `pass` were shown. Users could not understand why context and macro filters were empty.

**Fixed:** Added explanatory message: "Context and Macro filters will be unavailable. You can still run the scan with layer filters."

### FIXED: Improved error handling in Root CLI

**File:** `src/dddguard/root/cli.py`

**Before:** Exceptions were caught and printed via Rich, but without duplicating to stderr. For diagnostics, users had to screenshot the terminal. Each CLI flow was wrapped in its own try/except.

**Fixed:** Centralized `tui.error_boundary()` context manager created in `shared/adapters/driving/console/tui.py`. All flow dispatches in the HUD are wrapped through a single `with tui.error_boundary()` instead of duplicate try/except blocks. Middleware handles: `KeyboardInterrupt` (soft abort), `BaseDddError` (structured output with context, layer, and cause), other `Exception` (traceback + stderr). Critical startup errors include a link to GitHub Issues.

### FIXED: Moved tests from src/tests/ to tests/

**Before:** Tests were located in `src/tests/`, which did not match the convention (`tests/` at project root) and the `tests_dir: "tests"` configuration.

**Fixed:** Directory `src/tests/` moved to `tests/`. Added pytest configuration in `pyproject.toml` (`testpaths`, `pythonpath`) and coverage (`[tool.coverage.run]`, `[tool.coverage.report]`). Added dependency `pytest-cov`.

### FIXED: Extended error hierarchy — Driving/Driven variants

**File:** `src/dddguard/shared/helpers/generics/errors.py`

**Before:** Hierarchy had only 4 generic classes: `GenericDomainError`, `GenericAppError`, `GenericPortError`, `GenericAdapterError`. No split by direction (Driving/Driven).

**Fixed:** Added 4 new classes:
- `GenericDrivingPortError` — for Facades, Schemas, Dispatchers
- `GenericDrivenPortError` — for Repositories, Gateways, ACLs
- `GenericDrivingAdapterError` — for Controllers, CLI handlers, Consumers
- `GenericDrivenAdapterError` — for DB engines, HTTP clients, file I/O

Existing errors migrated to specific variants:
- `LinterPortError` -> inherits `GenericDrivingPortError` (Facade)
- `DetectionPortError` -> inherits `GenericDrivenPortError` (Storage)
- `FileWriteError` -> inherits `GenericDrivenAdapterError` (Draw.io renderer)

---

## 3. Test Coverage

### Current Test Structure

```
tests/
└── scanner/
    ├── unit/
    │   ├── test_graph_filtering_service.py
    │   └── test_graph_expansion_service.py
    ├── classification/
    │   ├── flow/
    │   │   └── test_identify_component_uc.py
    │   └── unit/
    │       ├── test_stage0_context_discovery.py
    │       ├── test_stage1_coordinate_definition.py
    │       ├── test_stage2_rule_prioritization.py
    │       └── test_stage3_4_component_matching.py
    └── detection/
        ├── flow/
        │   └── test_scan_project_uc.py
        ├── integration/
        │   └── test_file_system_repository.py
        └── unit/
            ├── test_ast_import_parser_service.py
            ├── test_module_resolution_service.py
            └── test_recursive_import_resolver.py
```

**Total test files: 12** — all in the Scanner context.

### Coverage by Context

| Context | Unit | Flow | Integration | E2E | Status |
|----------|:----:|:----:|:-----------:|:---:|--------|
| Scanner (domain) | 2 | — | — | — | Partial |
| Scanner / Detection (domain) | 3 | 1 | 1 | — | Good |
| Scanner / Classification (domain) | 4 | 1 | — | — | Good |
| **Linter** | 0 | 0 | 0 | 0 | **No tests** |
| **Visualizer** | 0 | 0 | 0 | 0 | **No tests** |
| **Scaffolder** | 0 | 0 | 0 | 0 | **No tests** |
| **Shared** | 0 | 0 | 0 | 0 | **No tests** |
| **Root** | 0 | 0 | 0 | 0 | **No tests** |

### Test Infrastructure

- Tests moved to `tests/` (project root)
- `pyproject.toml` configured: `testpaths = ["tests"]`, `pythonpath = ["src"]`
- Coverage config added: `[tool.coverage.run]`, `[tool.coverage.report]`
- Dependency `pytest-cov` added to dev group

### Missing

- `conftest.py` — no global fixtures
- Tests for `RuleEngineService` (Linter domain) — **most critical gap**, as this is the core linter business logic
- Tests for the entire visualizer layout pipeline
- Tests for `CreateConfigUseCase` (Scaffolder)
- Tests for Facades and ACL

---

## 4. Architecture Compliance

### Strengths

- **S-DDD structure** is consistently followed: domain -> app -> ports -> adapters -> composition
- **Each context** has its own `provider.py` (Dishka DI)
- **Facades** are used as the sole public API of contexts (ports/driving)
- **ACL** is used for inter-context communication (ports/driven)
- **Shared Kernel** holds common VO, enums, CodeGraph — does not break isolation
- **Providers (Dishka)** are correctly wired via `root/composition.py`
- **Layer separation** is clear: domain is unaware of frameworks, app orchestrates

### Room for Improvement

- **Logger is missing** — all contexts use direct output via Rich Console and stderr (could adopt Python `logging`)

---

## 5. Documentation Gaps

| Item | Status |
|-----|--------|
| README.md | Updated (removed `create` section, removed `dto/`) |
| User documentation | Created `docs/USER_GUIDE.md` |
| API documentation (for developers) | Missing |
| Docstrings in code | Present in key classes, but incomplete |
| Design docs (Scanner) | Present: `docs/scanner/detection/design.md`, `docs/scanner/classification/design.md` |
| Design docs (Linter, Visualizer) | Missing |
| CHANGELOG | Missing |
| CONTRIBUTING | Missing |

### README.md — Remaining Improvements

1. No mention of the actual commands `classify`, `classifydir`, `scandir`, `lintdir`, `drawdir`
2. Could add a link to `docs/USER_GUIDE.md`

---

## 6. Recommendations (Priority Plan)

### P1 — High Priority (tests for critical logic)

| # | Task | Details | Estimate |
|---|--------|--------|--------|
| 1 | Write unit tests for `RuleEngineService` | Cover all 5 rules (R100, F101, F102, C201, C202) + edge cases | 2-3 hours |
| 2 | Write flow test for `CheckProjectUseCase` | With fake ScannerGateway | 1 hour |
| 3 | Add `conftest.py` with base fixtures | Fixtures for CodeGraph, CodeNode, ConfigVo | 30 min |
| 4 | Write unit tests for `CreateConfigUseCase` | Scaffolder domain | 1 hour |

### P2 — Medium Priority (improvements)

| # | Task | Details | Estimate |
|---|--------|--------|--------|
| 5 | Tests for Visualizer layout pipeline | Unit tests for domain services | 3-4 hours |
| 6 | Update README: add all commands | `classify`, `classifydir`, `scandir`, `lintdir`, `drawdir` | 30 min |
| 7 | Add link to User Guide in README | | 5 min |
| 8 | Migrate remaining errors to Driving/Driven | Contexts still using `GenericPortError` / `GenericAdapterError` directly | 1 hour |

### P3 — Low Priority (long-term)

| # | Task | Details | Estimate |
|---|--------|--------|--------|
| 9 | Add design docs for Linter and Visualizer | Similar to Scanner | 2-3 hours |
| 10 | CHANGELOG and versioning | To track changes between releases | 1 hour |
| 11 | E2E tests | Full cycle: init -> scan -> lint -> draw | 1 day |
| 12 | Switch to Python `logging` | Replace stderr output with structured logger | 2-3 hours |

---

## Appendix: Context Dependency Map

```
Root (cli.py, composition.py)
├── Scanner [main engine]
│   ├── Detection [AST, imports, CodeGraph]
│   └── Classification [passports, components]
├── Linter [rules, violations]
│   └── -> Scanner (via ScannerAcl)
├── Visualizer [Draw.io diagrams]
│   └── -> Scanner (via ScannerAcl)
├── Scaffolder [config init]
└── Shared [enums, CodeGraph, config, TUI, assets]
```
