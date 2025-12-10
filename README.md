[![PyPI version](https://badge.fury.io/py/dddguard.svg)](https://badge.fury.io/py/dddguard)
[![Python Versions](https://img.shields.io/pypi/pyversions/dddguard.svg)](https://pypi.org/project/dddguard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# dddguard

Architecture Guard, Linter, and Scaffolder for Domain-Driven Design projects.

Stop arguing about folder structures and layer boundaries. `dddguard` enforces strict architectural rules, generates compliant boilerplate, and visualizes your project dependency graph.

It is designed to be your interactive architectural companion.

## Quick Start

Install globally using `uv` (requires Python 3.10+):

```bash
uv tool install dddguard
```

Simply run the tool to enter the interactive HUD:

```bash
dddguard
```

The tool will guide you through scanning, linting, or creating new components.

Capabilities

🛡️ Lint
Command: dddguard lint

You can explore detailed architectural rules and naming conventions interactively via diagrams using the 'View Rules (Summary)' and 'View Rules (Matrix)' options within the linter's interface.

📊 Draw
Command: dddguard draw

The visualizer parses your actual code structure and generates an XML file compatible with Draw.io (diagrams.net). It maps relationships between Contexts and Layers based on real imports. When using `dddguard drawdir` to visualize a specific directory, the generated diagram will include comprehensive information in its legend, providing detailed insights into the visualized architecture.

🧩 Create
Command: dddguard create

Scaffold new Bounded Contexts in seconds. Use the interactive wizard to generate production-ready boilerplate with:
- Correct layers (domain, app, adapters, ports).
- Dependency Injection containers.

📡 Scan
Command: dddguard scan

The core analysis engine. It builds a dependency graph of your entire project, detecting contexts and layers. Use the interactive filters to explore specific parts of your monolith or modular monolith.

The Standard
`dddguard` enforces a highly structured, granular architecture. This approach maximizes separation of concerns and clearly defines the role of every component, from the global entrypoint down to the individual Bounded Context.

```
src/
├── <context_name>/
│   ├── domain/           # Pure Business Logic
│   │   ├── aggregates/   # - Encapsulates business rules and consistency
│   │   ├── entities/     # - Business objects with a distinct identity
│   │   ├── vo/           # - Value Objects, immutable and without identity
│   │   ├── services/     # - Domain-specific operations, not tied to an entity
│   │   ├── events/       # - Represents something that happened in the domain
│   │   └── errors/       # - Custom domain-specific exceptions
│   │
│   ├── app/              # Application Layer: Orchestrates domain logic
│   │   ├── use_cases/    # - Implements Commands that change system state
│   │   ├── queries/      # - Implements Queries that read system state
│   │   ├── workflows/    # - Manages long-running processes (Sagas)
│   │   ├── handlers/     # - Reacts to domain or integration events
│   │   └── interfaces/   # - Defines contracts (ports) for driven adapters
│   │
│   ├── adapters/         # Translation layer between the core and the outside world
│   │   ├── driving/      # - Adapters that drive the application (e.g., Controllers)
│   │   └── driven/       # - Adapters driven by the application (e.g., Repositories)
│   │
│   ├── dto/              # Data Transfer Objects: Simple, logic-less data carriers
│   │   ├── driving/      # - Incoming data structures (Requests)
│   │   └── driven/       # - Outgoing data structures (Responses, Events)
│   │
│   ├── ports/            # Technology-specific infrastructure code
│   │   ├── driving/      # - Entry points for incoming signals (web server, CLI app)
│   │   └── driven/       # - Egress points for outgoing signals (DB client, HTTP client)
│   │
│   └── composition.py    # - Wires all dependencies for this specific context
│
├── shared/               # Shared code: kernels, libraries, or models used by multiple contexts
│
└── root/                 # Global application entrypoint and composition root
    ├── composition.py    # - Wires all contexts and shared services together
    ├── main.py           # - Main application entrypoint (e.g., starts web server)
    └── cli.py            # - CLI application entrypoint
```

### Anatomy of the Architecture

1.  **`root/`**: The top-level entrypoint for your entire application. Its `composition.py` assembles the different Bounded Contexts and `shared/` components.

2.  **`shared/`**: A place for code that is shared across multiple contexts, such as a shared kernel, common libraries, or cross-cutting concerns like logging. The structure within `shared/` is intentionally flexible.

3.  **`<context_name>/`**: Represents a Bounded Context, a self-contained module with its own internal layers:
    -   **`domain/`**: The heart of the context's business logic. It is completely isolated and pure.
    -   **`app/`**: Orchestrates the domain logic to perform specific tasks, defining the application's capabilities.
    -   **`adapters/`**: Translate between the outside world and the application layer, implementing interfaces defined in `app/` or triggering `app/` logic.
    -   **`dto/`**: Define the data contracts for requests and responses, ensuring clean boundaries.
    -   **`ports/`**: Contain the raw, technology-specific code that connects to infrastructure.
    -   **`composition.py`**: The context's local "glue" that wires together its internal components.

## Technology Stack

The project is built with modern Python tooling and development practices:

- **Typer** + **Rich**  + **InquirerPy**   best smooth CLI experience.
- **Dishka**  lightweight Dependency Injection for clean and decoupled architecture.

---

**Maintained by**: **Sense1Tapo4ek**