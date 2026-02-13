from typing import Final

# Note: We use \b to tell Typer/Click to respect line breaks in the block
LINTER_CLI_HELP: Final[str] = """
Validates architecture using 13 dependency rules across 4 groups.
Every import is checked against the DDDGuard rule engine.

\b
GROUP 1 — INTERNAL RULES (Same Context):
-----------------------------------------
 1. Domain Purity       Domain -> Domain, Global only
 2. App Isolation        App -> App, Domain, Global only
 3. Driving Port Boundary  Ports/Driving -> App, Domain, Ports/Driving, Global
 4. Driven Port Boundary   Ports/Driven -> App, Domain, Adapters/Driven, Global
 5. Driving Adapter Boundary  Adapters/Driving -> Ports/Driving, Global only
 6. Driven Adapter Boundary   Adapters/Driven -> Global only
 7. Composition (Free Zone)   Composition -> everything within same context

\b
GROUP 2 — FRACTAL RULES (Parent <-> Child):
--------------------------------------------
 8. Fractal Upstream    Child -> Parent: Domain, App, Ports/Driven
 9. Fractal Downstream  Parent -> Child: Ports/Driving only (facades)

\b
GROUP 3 — CROSS-CONTEXT RULES (Alien Contexts):
-------------------------------------------------
10. Cross-Context Outbound  Only Ports/Driven (ACL) can call outside
11. Cross-Context Inbound   Only Ports/Driving (facades) are visible

\b
GROUP 4 — SCOPE ISOLATION:
---------------------------
12. Shared Independence  Shared -> Shared, Global only (never contexts)
13. Root Isolation       Root -> providers + Shared only (never internals)

\b
BYPASS CONDITIONS (always allowed):
------------------------------------
- Target is SHARED (global shared kernel)
- Source is COMPOSITION or GLOBAL
- Source or target has no ComponentPassport
"""

# ==============================================================================
# Structured Data for Interactive Tables
# ==============================================================================

# GROUP 1: Internal Layer Rules
# Format: (Layer Name Rich String, Rules Description String)
INTERNAL_RULES_TABLE_DATA: Final[list[tuple[str, str]]] = [
    (
        "[bold blue]DOMAIN[/]",
        "• [bold green]Domain[/], Global\n"
        "• [dim red]Forbidden:[/] App, Ports, Adapters, Composition",
    ),
    (
        "[bold magenta]APP[/]",
        "• [bold green]App[/] (own interfaces), [bold green]Domain[/], Global\n"
        "• [dim red]Forbidden:[/] Ports, Adapters, Composition",
    ),
    (
        "[bold green]PORTS / DRIVING[/]",
        "• [bold green]App[/], [bold green]Domain[/], [bold green]Ports/Driving[/] (schemas), Global\n"
        "• [dim red]Forbidden:[/] Ports/Driven, Adapters, Composition",
    ),
    (
        "[bold orange1]PORTS / DRIVEN[/]",
        "• [bold green]App[/] (interfaces), [bold green]Domain[/], "
        "[bold green]Adapters/Driven[/] (tools), Global\n"
        "• [dim red]Forbidden:[/] Ports/Driving, Adapters/Driving, Composition",
    ),
    (
        "[bold green]ADAPTERS / DRIVING[/]",
        "• [bold green]Ports/Driving[/] (facades, schemas), Global\n"
        "• [dim red]Forbidden:[/] Domain, App, Ports/Driven, Adapters/Driven, Composition",
    ),
    (
        "[bold orange1]ADAPTERS / DRIVEN[/]",
        "• [bold green]Global[/], Shared (external libs only)\n"
        "• [dim red]Forbidden:[/] Domain, App, Ports, Adapters/Driving, Composition",
    ),
    (
        "[bold cyan]COMPOSITION[/]",
        "• [bold green]Everything[/] within the same context\n• [dim](Bypassed — wiring layer)[/]",
    ),
]

# GROUP 2: Fractal Rules (Parent <-> Child)
FRACTAL_RULES_TABLE_DATA: Final[list[tuple[str, str]]] = [
    (
        "[bold yellow]Child -> Parent[/]\n[dim](Upstream)[/]",
        "• [bold green]Allowed:[/] Domain, App, Ports/Driven, Global\n"
        "• [dim red]Forbidden:[/] Ports/Driving, Adapters, Composition",
    ),
    (
        "[bold yellow]Parent -> Child[/]\n[dim](Downstream)[/]",
        "• [bold green]Allowed:[/] Ports/Driving only (facades)\n"
        "• [dim red]Forbidden:[/] Domain, App, Ports/Driven, Adapters, Composition",
    ),
]

# GROUP 3: Cross-Context Rules
CROSS_CONTEXT_RULES_TABLE_DATA: Final[list[tuple[str, str]]] = [
    (
        "[bold orange1]Outbound[/]\n[dim](Who can call)[/]",
        "• Only [bold green]Ports/Driven[/] (ACL) can initiate calls\n"
        "• [dim red]Forbidden:[/] Domain, App, Ports/Driving, Adapters, Composition",
    ),
    (
        "[bold green]Inbound[/]\n[dim](What's visible)[/]",
        "• Only [bold green]Ports/Driving[/] (facades, schemas) are accessible\n"
        "• [dim red]Forbidden:[/] Domain, App, Ports/Driven, Adapters, Composition",
    ),
]

# GROUP 4: Scope Isolation Rules
SCOPE_RULES_TABLE_DATA: Final[list[tuple[str, str]]] = [
    (
        "[bold cyan]SHARED[/]",
        "• [bold green]Allowed:[/] Shared, Global only\n"
        "• [dim red]Forbidden:[/] Context modules, Root\n"
        "• [dim]Base of the pyramid — no upward dependencies[/]",
    ),
    (
        "[bold white]ROOT[/]",
        "• [bold green]Allowed:[/] Context providers (provider.py), Shared\n"
        "• [dim red]Forbidden:[/] Context internals (domain, app, ports, adapters)\n"
        "• [dim]Outermost shell — wires providers only[/]",
    ),
]

# BYPASS conditions
BYPASS_RULES_DATA: Final[list[tuple[str, str]]] = [
    ("Target is [cyan]SHARED[/]", "Shared kernel is globally accessible"),
    ("Source is [cyan]COMPOSITION[/] or [cyan]GLOBAL[/]", "Wiring layers can import freely"),
    ("Missing [cyan]ComponentPassport[/]", "Unclassified nodes cannot be validated"),
]

# Legacy alias for backwards compatibility
LINTER_RULES_TABLE_DATA: Final[list[tuple[str, str]]] = INTERNAL_RULES_TABLE_DATA
