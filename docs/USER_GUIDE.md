# DDDGuard — User Guide

> **Version:** 1.0.1 | **Python:** >= 3.10 | **License:** MIT

**DDDGuard** — an interactive command-line tool for analyzing, linting, and visualizing the architecture of projects built on Domain-Driven Design (DDD) principles.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Quick Start](#2-quick-start)
3. [Configuration](#3-configuration)
4. [Interactive Menu (HUD)](#4-interactive-menu-hud)
5. [Scanner — Project Structure Analysis](#5-scanner--project-structure-analysis)
6. [Linter — Architectural Rules Validation](#6-linter--architectural-rules-validation)
7. [Visualizer — Diagram Generation](#7-visualizer--diagram-generation)
8. [Scaffolder — Configuration Initialization](#8-scaffolder--configuration-initialization)
9. [Target Architecture](#9-target-architecture)
10. [Command Reference](#10-command-reference)

---

## 1. Installation

### Via uv (recommended)

```bash
uv tool install dddguard
```

### Via pip

```bash
pip install dddguard
```

### Requirements

- Python 3.10 or higher
- Dependencies are installed automatically: Typer, Rich, InquirerPy, Dishka, PyYAML, Jinja2

---

## 2. Quick Start

### Interactive Mode

Simply run without arguments — the interactive menu will open:

```bash
dddguard
```

### Configuration Initialization

Create a configuration file in the project root:

```bash
dddguard init
```

This creates the file `docs/dddguard/config.yaml` with default settings.

### Quick Directory Analysis (without configuration)

If you want to quickly analyze a directory without creating a configuration:

```bash
dddguard scandir
dddguard classifydir
dddguard lintdir
dddguard drawdir
```

Each of these commands opens an interactive directory selection.

---

## 3. Configuration

### Creating Configuration

```bash
dddguard init [path]
```

By default (if path is not specified), the configuration is created in the current directory.

**File path:** `{project_root}/docs/dddguard/config.yaml`

### Configuration File Structure

```yaml
project:
  root_dir: "/path/to/project/"    # Project root directory
  source_dir: "src"                # Source code directory
  tests_dir: "tests"               # Test directory
  docs_dir: "docs"                 # Documentation directory

scanner:
  exclude_dirs:                     # Directories excluded from scanning
    - ".git"
    - ".venv"
    - "venv"
    - "__pycache__"
    - "node_modules"
    - "migrations"
    - "build"
    - "dist"
    - ".idea"
    - ".vscode"

  ignore_files:                     # Files excluded from scanning
    - "conftest.py"
    - "manage.py"
    - "setup.py"
    - "__main__.py"
```

### Auto-Detection of Configuration

DDDGuard automatically searches for the configuration file by traversing up the directory tree. Search order:

1. `docs/dddguard/config.yaml`
2. `dddguard/config.yaml`
3. `config.yaml`

---

## 4. Interactive Menu (HUD)

When you run `dddguard` without arguments, the interactive menu — the main control panel — opens.

### Appearance

```
╭─────────────────────────────────────────╮
│       DDDGuard Architecture Suite       │
│         Context: Root                   │
├─────────────────────────────────────────┤
│  Project: myproject                     │
│  Source:  src                           │
│  Config:  config.yaml                   │
╰─────────────────────────────────────────╯

 PRIMARY PROJECT ACTIONS
  1. Scan Project        Auto-scan configured source
  2. Lint Project        Validate architecture rules
  3. Draw Arch           Generate diagrams from config
  4. Classify Tree       Visualize arch structure
 DIRECTORY UTILITIES
  1. Classify Dir        Visualize specific folder
  2. Draw Dir            Draw specific folder
  3. Lint Dir            Lint specific folder
  4. Scan Dir            Scan specific folder

  Exit
```

### Menu Modes

**If configuration is found**, all actions are displayed: project commands (working with the configured `source_dir`) and utilities for individual directories.

**If no configuration exists**, the menu offers:
- **Create Config** — create `config.yaml`
- **Ad-hoc Tools** — Classify Dir, Draw Dir, Lint Dir, Scan Dir (work without configuration)

### Repeat Last Scan

If you have already performed a scan in the current session, an option will appear in the menu:
```
  0. Repeat Scan:       target_dir/
```
This instantly repeats the last scan with the same settings without opening the wizard.

### Navigation

- **Up/Down arrows** — move between items
- **Enter** — select action
- **Ctrl+C** — cancel current action

---

## 5. Scanner — Project Structure Analysis

Scanner is the main analysis engine. It parses AST of Python files, resolves imports, identifies contexts and layers, and outputs a complete dependency graph of the project.

### Commands

| Command | Description |
|---------|-------------|
| `dddguard scan` | Project scanning (uses configuration) |
| `dddguard scandir` | Scan selected directory |
| `dddguard classify` | Project tree classification |
| `dddguard classifydir` | Classify selected directory |

### CLI Parameters

```bash
dddguard scan [OPTIONS]

  --depth INTEGER         Depth of recursive import resolution (default: 0)
  --assets / --no-assets  Include Asset/Resource entities (default: enabled)
  --file-tree-only        Mask file contents in output JSON
```

```bash
dddguard scandir [OPTIONS]

  --depth INTEGER         Depth of recursive import resolution (default: 0)
```

### Scanner Wizard

After running any scan command, the interactive settings wizard opens.

```
╭─────────────────────────────────────────────────────────╮
│              Scanner Configuration                      │
│       Arrows to navigate • Enter to toggle              │
├────────────────────────┬────────────────────────────────┤
│  Mode:       Python    │  Layers:   ALL                 │
│  Imp. Depth: None      │  Macros:   ALL                 │
│  Content:    INCLUDED  │  Contexts: ALL                 │
│  Assets:     ON        │                                │
╰────────────────────────┴────────────────────────────────╯
            Target: Project Source (src/myproject)

 STRATEGY
  Scan All Files                [OFF]
  Mask File Content             [OFF]
  Import Depth                  [0]
  Include Assets/Res            [ON]
 FILTERS
  Filter Contexts (Root/Shared) [ALL]
  Filter Layers                 [ALL]
  Filter Macros                 [ALL]

  Check Configuration
  >>> EXECUTE SCAN <<<
  Exit / Cancel
```

### Wizard Parameters

#### Strategy

| Parameter | Description |
|-----------|-------------|
| **Scan All Files** | `OFF` — Python files only, `ON` — all files |
| **Mask File Content** | `ON` — file contents in JSON are replaced with `<Masked Content>` |
| **Import Depth** | `0` — strict mode (direct imports only), `1-5` — recursive dependency expansion |
| **Include Assets/Res** | Include resource files (templates, configs, etc.) |

#### Filters

| Filter | Description |
|--------|-------------|
| **Filter Contexts** | Multi-select bounded contexts (ROOT and SHARED highlighted in color) |
| **Filter Layers** | Multi-select layers: Domain, App, Ports, Adapters, Composition |
| **Filter Macros** | Multi-select macro zones (context groups). Selecting a macro zone automatically updates the context filter |

### Scanning Algorithm

1. **Detection** — filesystem traversal, AST parsing, import resolution
2. **Classification** — assigning each module an architectural "passport" (context, layer, direction, component type)
3. **Filtering** — excluding modules by physical path and selected filters
4. **Expansion** — BFS expansion of dependencies to the specified depth
5. **Finalization** — finalizing visible nodes for the report

### Output Data

**Scan** (`dddguard scan`, `dddguard scandir`) — creates file `project_tree.json` with nested file tree and their contents (or masked contents).

**Classify** (`dddguard classify`, `dddguard classifydir`) — outputs a Rich table to the terminal:

```
 Macro   Context    Layer        Dir  Structure (src)                Type            Method
──────────────────────────────────────────────────────────────────────────────────────────────
         root       COMPOSITION       root/                          
                    COMPOSITION       ├── cli.py                     ENTRYPOINT      STRUCTURAL
                    COMPOSITION       └── composition.py             CONTAINER       NAME
 SCANNER scanner    DOMAIN       -    scanner/
                    DOMAIN            ├── domain/
                    DOMAIN            │   └── value_objects.py       VALUE_OBJECT    NAME
                    APP               ├── app/
                    APP               │   └── use_cases/
                    APP               │       └── run_scan_uc.py     USE_CASE        STRUCTURAL
                    PORTS        In   ├── ports/
                    PORTS             │   └── driving/
                    PORTS             │       └── scanner_facade.py  FACADE          NAME
```

Columns:
- **Macro** — macro zone (context group)
- **Context** — bounded context
- **Layer** — architectural layer (DOMAIN, APP, PORTS, ADAPTERS, COMPOSITION, GLOBAL)
- **Dir** — direction: `In` (Driving), `Out` (Driven), `-` (undefined)
- **Structure** — file tree with indentation
- **Type** — component type (USE_CASE, FACADE, ENTITY, REPOSITORY, etc.)
- **Method** — detection method: `STRUCTURAL` (by folder structure) or `NAME` (by file name)

---

## 6. Linter — Architectural Rules Validation

Linter checks imports between modules for compliance with DDD rules. It uses Scanner to build the dependency graph and then validates each edge of the graph.

### Commands

| Command | Description |
|---------|-------------|
| `dddguard lint` | Project linting (uses configuration) |
| `dddguard lintdir` | Lint selected directory |

### Linter Wizard

```
╭─────────────────────────────────────────╮
│          Linter Configuration           │
│       Validate Architecture Rules       │
├─────────────────────────────────────────┤
│  Target: ./src/myproject                │
╰─────────────────────────────────────────╯

  🚀 Run Linter Analysis
  
  📖 View Rules Summary
  🔢 View Rules Matrix
  
  ❌ Exit
```

#### Menu Items

| Item | Description |
|------|-------------|
| **Run Linter Analysis** | Run architecture validation |
| **View Rules Summary** | Show text description of rules for each layer |
| **View Rules Matrix** | Show access matrix and cross-context policies |

### Rules Matrix

When selecting "View Rules Matrix", two sections are displayed:

#### 1. Internal Layer Boundaries (Intra-Context)

Access matrix within a single bounded context:

```
╭──────────────────────────────────────────────────────────────────╮
│        🛑 Internal Layer Boundaries (Intra-Context)              │
├──────────────┬─────────────────────────┬─────────────────────────┤
│ Source Layer  │ Can Import (Allowed)    │ Cannot Import (Forbid.) │
├──────────────┼─────────────────────────┼─────────────────────────┤
│ DOMAIN       │ DOMAIN, GLOBAL          │ APP, PORTS, ADAPTERS,   │
│              │                         │ COMPOSITION             │
│ APP          │ APP, DOMAIN, GLOBAL     │ PORTS, ADAPTERS,        │
│              │                         │ COMPOSITION             │
│ PORTS        │ PORTS, APP, DOMAIN,     │ COMPOSITION             │
│              │ ADAPTERS, GLOBAL        │                         │
│ ADAPTERS     │ ADAPTERS, PORTS, APP,   │ COMPOSITION             │
│              │ DOMAIN, GLOBAL          │                         │
│ COMPOSITION  │ All                     │ None                    │
╰──────────────┴─────────────────────────┴─────────────────────────╯
```

#### 2. Cross-Context Policies

Two side blocks:

```
╭─── 🔓 Public Layers ───────╮  ╭─── 📡 Outbound Initiators ──╮
│                             │  │                              │
│  • PORTS                    │  │  • ADAPTERS                  │
│                             │  │  • PORTS                     │
│ (Accessible from other      │  │  • APP                       │
│  Contexts)                  │  │                              │
│                             │  │ (Can call other Contexts)    │
╰─────────────────────────────╯  ╰──────────────────────────────╯
```

### Linter Rules

DDDGuard validates 5 rule categories:

#### R100 — Layer Violation (Intra-Context)

Import from forbidden layer within a single bounded context.

**Example:** a module from the `domain/` layer imports a module from the `app/` layer — this is a violation, as Domain must not depend on Application.

```
Rule: R100
Message: Layer violation: 'DOMAIN' cannot import 'APP'
```

#### F101 — Upstream Violation (Fractal / Vertical)

Child context accesses parent context, but to a forbidden layer. Child context can only see parent's `DOMAIN` and `PORTS`.

```
Rule: F101
Message: Upstream Violation: Child 'detection' can only access Parent 'scanner' Domain/Ports.
```

#### F102 — Downstream Violation (Fractal / Vertical)

Parent context accesses child, but to a non-public layer. Parent can only see child context's `PORTS`.

```
Rule: F102
Message: Downstream Violation: Parent 'scanner' can only access Child 'detection' via Public Ports.
```

#### C201 — Context Isolation

A layer that does not have permission to initiate cross-context calls attempts to access another context. Only `ADAPTERS`, `PORTS`, and `APP` can initiate cross-context calls.

```
Rule: C201
Message: Context isolation: 'DOMAIN' layer cannot initiate cross-context calls.
```

#### C202 — Private Access

Attempt to import a non-public layer of another context. Only `PORTS` can be imported from another context.

```
Rule: C202
Message: Private access: Cannot import internal layer 'DOMAIN' of context 'payment'.
```

### Linter Report

**If no violations found:**

```
╭── ✅ Architecture Clean ───────────────╮
│  Files Scanned: 47                     │
│  Violations:    0                      │
│  Status:        PASSED                 │
╰────────────────────────────────────────╯
```

**If violations found:**

```
╭── ❌ Architectural Violations Found ───╮
│  Files Scanned: 47                     │
│  Violations:    3                      │
│  Status:        FAILED                 │
╰────────────────────────────────────────╯

 Rule   Context      Violation Details
──────────────────────────────────────────────────────────────────
 R100   scanner      Layer violation: 'DOMAIN' cannot import 'APP'
                     Loc: scanner.domain.my_service -> scanner.app.some_uc
 C202   payment      Private access: Cannot import internal layer 'DOMAIN' of context 'payment'.
                     Loc: order.adapters.acl -> payment.domain.entity
```

### Exceptions from Validation

The following imports are **always allowed** and are not validated:
- Imports from `shared/` (Shared Kernel)
- Imports from `root/` (Composition Root)
- Imports from `COMPOSITION` and `GLOBAL` layers (technical layers)

---

## 7. Visualizer — Diagram Generation

Visualizer generates architectural diagrams in Draw.io format (`.drawio`), which can be opened at [diagrams.net](https://app.diagrams.net/).

### Commands

| Command | Description |
|---------|-------------|
| `dddguard draw` | Project diagram generation (uses configuration) |
| `dddguard drawdir` | Generate diagram for selected directory |

### Visualizer Wizard

```
╭─────────────────────────────────────────╮
│          ARCHITECTURAL MAPPER           │
├─────────────────────────────────────────┤
│  Output:       architecture.drawio      │
│  Errors:       Visible                  │
│  Wiring (Root): Hidden (Clean)         │
│  Shared Deps:  Hidden (Clean)           │
╰─────────────────────────────────────────╯

 CONFIGURATION
  🔍 Filters & Noise Reduction...
  💾 Output File (architecture.drawio)
  
  >>> GENERATE DIAGRAM <<<
  Exit / Cancel
```

### Visualization Settings

| Setting | Default | Description |
|---------|---------|-------------|
| **Output File** | `architecture.drawio` | Output file name (`.drawio` extension is added automatically) |
| **Show Errors** | Enabled | Show error and exception nodes |
| **Hide Wiring (Root)** | Enabled | Hide arrows from Root (for cleaner diagram) |
| **Hide Shared Deps** | Enabled | Hide arrows to Shared Kernel (reduces noise) |

#### "Filters & Noise Reduction" Submenu

Opens multi-select:
- **Show Errors/Exceptions** — show/hide error nodes
- **Hide Wiring (Root -> *)** — hide arrows from Root to all contexts
- **Hide Common (* -> Shared)** — hide arrows from all contexts to Shared

### How to Open the Diagram

1. Go to [https://app.diagrams.net/](https://app.diagrams.net/)
2. Select **File -> Open From -> Device**
3. Open the generated `.drawio` file

### Diagram Anatomy

The diagram consists of several elements:

#### Sidebar (Legend)

- **Architecture Legend** — layer descriptions, component types, color coding
- **Naming Cloud** — tag cloud with DDD names (patterns for component recognition)

#### Context Towers

Each bounded context is displayed as a vertical "tower" with horizontal zones:

```
┌─────────────── SCANNER CONTEXT ───────────────┐
│  ┌─ DOMAIN ──────────────────────────────┐    │
│  │  [value_objects] [errors] [services]  │    │
│  └───────────────────────────────────────┘    │
│  ┌─ APP ─────────────────────────────────┐    │
│  │  [run_scan_uc] [inspect_tree_uc]      │    │
│  └───────────────────────────────────────┘    │
│  ┌─ ADAPTERS ────────────────────────────┐    │
│  │ DRIVING          │ DRIVEN             │    │
│  │ [cli] [wizard]   │ [acl]              │    │
│  └──────────────────┴────────────────────┘    │
│  ┌─ PORTS ───────────────────────────────┐    │
│  │ DRIVING          │ DRIVEN             │    │
│  │ [facade]         │ [gateway]          │    │
│  └──────────────────┴────────────────────┘    │
│  ┌─ COMPOSITION ─────────────────────────┐    │
│  │  [provider]                           │    │
│  └───────────────────────────────────────┘    │
└───────────────────────────────────────────────┘
```

#### Zone Color Coding

| Zone | Background Color |
|------|------------------|
| Domain | Light blue (#e1f5fe) |
| App | Lilac (#f3e5f5) |
| Adapters Driving | Light green |
| Adapters Driven | Light yellow |
| Ports Driving | Light blue |
| Ports Driven | Light orange |
| Composition | Gray |

#### Nodes and Arrows

- **Nodes** — files/modules, shown as rounded rectangles with module name and component type
- **Interfaces** — dashed border
- **Arrows** — orthogonal lines with classic arrowheads, color depends on node complexity

---

## 8. Scaffolder — Configuration Initialization

Scaffolder creates the initial configuration file for DDDGuard.

### Command

```bash
dddguard init [path]
```

- **path** (optional) — project root. Default — current directory.

### What Is Created

File `docs/dddguard/config.yaml` with standard configuration (see [Configuration section](#3-configuration)).

If the file already exists, the command will display a warning and will not overwrite it.

### From the Interactive Menu

If configuration is not found, the **"Create Config"** item appears in the HUD, which performs the same operation.

---

## 9. Target Architecture

DDDGuard is designed for projects with the following structure:

```
src/
├── <context_name>/              # Bounded Context
│   ├── domain/                  # Pure business logic
│   │   ├── aggregates/          # Aggregates — encapsulation of business rules
│   │   ├── entities/            # Business objects with identity
│   │   ├── vo/                  # Value Objects — immutable, no identity
│   │   ├── services/            # Domain services
│   │   ├── events/              # Domain events
│   │   └── errors/              # Domain exceptions
│   │
│   ├── app/                     # Application Layer: orchestration
│   │   ├── use_cases/           # Commands that change state
│   │   ├── queries/             # Read-only queries
│   │   ├── workflows/           # Long-running processes (Sagas)
│   │   ├── handlers/            # Event handlers
│   │   └── interfaces/          # Contracts (ports) for driven adapters
│   │
│   ├── adapters/                # Translation between core and external world
│   │   ├── driving/             # Inbound adapters (Controllers, CLI)
│   │   └── driven/              # Outbound adapters (Repositories, Gateways)
│   │
│   ├── ports/                   # Infrastructure code
│   │   ├── driving/             # Entry points (Facades, Schemas)
│   │   └── driven/              # Exit points (DB clients, HTTP clients)
│   │
│   └── provider.py              # Context DI container (Composition)
│
├── shared/                      # Shared Kernel — code used by multiple contexts
│
└── root/                        # Global entry point
    ├── composition.py           # Assembly of all contexts
    └── cli.py                   # CLI entry point
```

### Component Types Recognized by DDDGuard

#### Domain Layer
Aggregate Root, Entity, Value Object, Domain Service, Domain Event, Factory, Specification, Policy

#### Application Layer
Use Case, Query, Workflow, Interface, Handler

#### Ports Layer
Facade, Dispatcher, Repository, Publisher, Gateway, ACL, Transaction Manager, Schema, Mapper

#### Adapters Layer
Controller, Consumer, Scheduler, CLI, Repository, Publisher, Gateway, Transaction Manager, Middleware

#### Composition Layer
Container, Config, Entrypoint, Logger

#### Global (Archetype)
Error, Helper, Decorator, Marker, Folder, Stub, Asset, Unknown

### Classification Methods

DDDGuard determines component type in two ways:

1. **STRUCTURAL** — by location in folder structure (e.g., file in `entities/` = Entity)
2. **NAME** — by file name (e.g., `*_service.py` = Service, `*_facade.py` = Facade)

---

## 10. Command Reference

| Command | Description | Requires Config |
|---------|-------------|:--------------:|
| `dddguard` | Interactive menu (HUD) | No* |
| `dddguard init [path]` | Create configuration file | No |
| `dddguard scan` | Project scanning with wizard | Yes** |
| `dddguard scandir` | Scan selected directory | No |
| `dddguard classify` | Project architecture classification | Yes |
| `dddguard classifydir` | Classify selected directory | No |
| `dddguard lint` | Project linting | Yes** |
| `dddguard lintdir` | Lint selected directory | No |
| `dddguard draw` | Architectural diagram generation | Yes** |
| `dddguard drawdir` | Generate diagram for directory | No |

\* HUD works without configuration but offers a limited set of actions.

\** Without configuration, the command will warn and suggest using default settings.

### Common CLI Parameters

```bash
dddguard --help            # Help for all commands
dddguard <command> --help  # Help for specific command
```

---

## FAQ

### What is the difference between `scan` and `classify`?

- **scan** — creates a full dependency graph with filtering and exports to JSON (`project_tree.json`)
- **classify** — displays the architectural tree with component types as a table in the terminal (no filtering, no export)

### How do the `*dir` commands differ from the standard ones?

- **Standard** (`scan`, `lint`, `draw`, `classify`) — work with `source_dir` from configuration
- **Dir variants** (`scandir`, `lintdir`, `drawdir`, `classifydir`) — offer interactive selection of any directory

### Where is the scan output file stored?

By default — `project_tree.json` in the current directory.

### What is "Import Depth"?

- **0 (Strict)** — only files physically located in the scanned directory
- **1+** — BFS expansion: for each visible file, its dependencies (imports) are shown, even if they are outside the scanned directory, up to the specified depth

### What is "Macro Zone"?

A macro zone is a group of related bounded contexts. For example, the `scanner` context can be a macro zone containing child contexts `detection` and `classification`. DDDGuard automatically detects these hierarchies.
