from typing import Final

# Note: We use \b to tell Typer/Click to respect line breaks in the following block
LINTER_CLI_HELP: Final[str] = """
🚀 Validates Architecture Rules on the main project.

The Linter enforces strict DDD constraints based on the "Laws of Physics"
of clean architecture.

\b
🧱 LAYER ISOLATION RULES:
-------------------------
1. 🔵 DOMAIN (The Core):
   - Must be PURE.
   - Can ONLY import from SHARED KERNEL and itself.

\b
2. 🟣 APP (The Orchestration):
   - Can import DOMAIN and SHARED KERNEL.
   - Speaks only Domain Language or Primitives.
   - ⛔ NO DTOs: Does not depend on Data Transfer Objects.
   - ⛔ NO INFRASTRUCTURE: Cannot import Adapters or Ports.

\b
3. 🔌 ADAPTERS (The Glue):
   - 🟢 DRIVING (Controllers/Consumers):
     - Converts Driving DTOs -> Domain/Primitives.
     - Calls APP UseCases.
     - ⛔ NO PORTS: Cannot touch DB/Config/Server directly.
   - 🟠 DRIVEN (Repositories/ACLs):
     - Implements APP Interfaces.
     - ✅ USES PORTS: Imports Driven Ports (DB Sessions, Clients).
     - ✅ CROSS-CONTEXT: Can import Driving Adapters/DTOs of other contexts.

\b
4. 📄 DTOs (Data Contracts):
   - Dumb objects. No business logic.
   - Can import DOMAIN (for mapping) + SHARED KERNEL.
   - ⛔ NO LOGIC DEPS: Cannot import App, Adapters, or Ports.

\b
5. ⚙️ PORTS (Infrastructure/Frameworks):
   - 🟢 DRIVING (e.g. FastAPI App, CLI):
     - Imports DRIVING ADAPTERS (to register routes).
   - 🟠 DRIVEN (e.g. SQLAlchemy, Redis Client):
     - Low-level tools. Isolated.

\b
🚧 CROSS-CONTEXT BOUNDARIES:
----------------------------
- Source: Only DRIVEN ADAPTERS (ACL) can initiate calls to other contexts.
- Target: Can only import DRIVING ADAPTERS (Facades) or DRIVING DTOs of the target.
"""
