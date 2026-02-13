import html

# Import Constants from Asset Layer
from .html_templates_data import (
    LEGEND_CSS_LI,
    LEGEND_CSS_SUB_H,
    LEGEND_CSS_TXT,
    LEGEND_CSS_UL,
    LEGEND_HTML_HEADER,
    LEGEND_HTML_LAYER_ANATOMY_HEADER,
    LEGEND_HTML_NOTE,
    LEGEND_HTML_VISUAL_GUIDE,
)


def get_architecture_legend(context_names: list[str]) -> str:
    """
    Returns the rich HTML content for the diagram legend/README block.
    Structure: Domain -> App -> Adapters (Driving/Driven) -> Ports.
    """
    # Filter specific architectural contexts for the header
    business_contexts = [c for c in context_names if c not in ("root", "shared")]
    has_root = "root" in context_names
    has_shared = "shared" in context_names

    # Helper for list items to reduce verbosity
    def li(b_text, i_text):
        return f'<li style="{LEGEND_CSS_LI}"><b>{b_text}</b> {i_text}</li>'

    return (
        f'<div style="{LEGEND_CSS_TXT}">'
        # --- HEADER ---
        f"{LEGEND_HTML_HEADER}"
        # --- MACRO ARCHITECTURE ---
        f'<div style="margin-bottom: 10px;">'
        f"  <b>1. Composition Root {'✅' if has_root else ''}:</b> Entry point. Wires contexts together.<br>"
        f"  <b>2. Shared Kernel {'✅' if has_shared else ''}:</b> Common Code (VOs, DTOs) reused across contexts.<br>"
        f"  <b>3. Bounded Contexts:</b> Isolated business modules ({html.escape(', '.join(business_contexts))})."
        f"</div>"
        # --- VISUAL GUIDE ---
        f"{LEGEND_HTML_VISUAL_GUIDE}"
        # --- LAYERS ---
        f"{LEGEND_HTML_LAYER_ANATOMY_HEADER}"
        # 1. DOMAIN
        f'<div style="margin-bottom: 8px;">'
        f'  <b style="color: #2980B9;">1. 🔵 Domain Layer (The Core)</b><br>'
        f"  <i>Pure business logic. Isolated from infrastructure.</i>"
        f'  <ul style="{LEGEND_CSS_UL}">'
        f"{li('Aggregate Root:', 'Cluster root. Transaction consistency guardian.')}"
        f"{li('Entity:', 'Mutable object with Identity.')}"
        f"{li('Value Object:', 'Immutable, defined by attributes. No ID.')}"
        f"{li('Domain Service:', 'Stateless logic spanning entities.')}"
        f"{li('Factory:', 'Encapsulates complex object creation.')}"
        f"{li('Domain Event:', 'Fact that happened in the past.')}"
        f"{li('Domain Error:', 'Business rule violation.')}"
        f"  </ul>"
        f"</div>"
        # 2. APP
        f'<div style="margin-bottom: 8px;">'
        f'  <b style="color: #8E44AD;">2. 🟣 App Layer (Orchestration)</b><br>'
        f"  <i>Coordinates scenarios. No business rules.</i>"
        f'  <ul style="{LEGEND_CSS_UL}">'
        f"{li('Use Case:', 'Command. Changes state. Transactional.')}"
        f"{li('Query:', 'Read-only. No side effects. Optimized.')}"
        f"{li('Workflow:', 'Long-running saga/process coordination.')}"
        f"{li('Handler:', 'Reacts to Domain/Integration events.')}"
        f"{li('Interface:', 'Abstract Port definition (Dependency Inversion).')}"
        f"{li('AppError:', 'Application-specific failure.')}"
        f"  </ul>"
        f"</div>"
        # 3. ADAPTERS (GROUPED)
        f'<div style="margin-bottom: 8px; border-top: 1px solid #eee; padding-top: 4px;">'
        f'  <b style="color: #34495E;">3. 🔌 Adapters (Interface Layer)</b><br>'
        f"  <i>Connects the Core to the Outside World.</i>"
        # 3a. Driving
        f'  <div style="margin-left: 5px; margin-top: 4px;">'
        f'    <div style="{LEGEND_CSS_SUB_H}; color: #27AE60;">A. 🟢 Driving (Inbound)</div>'
        f'    <ul style="{LEGEND_CSS_UL}">'
        f"{li('Controller:', 'Sync input (HTTP/RPC). Direct response.')}"
        f"{li('Consumer:', 'Async input (Queues). Background processing.')}"
        f"{li('RequestDTO:', 'Input data contract/structure.')}"
        f"{li('AdapterError:', 'Input processing failure.')}"
        f"    </ul>"
        f"  </div>"
        # 3b. Driven
        f'  <div style="margin-left: 5px;">'
        f'    <div style="{LEGEND_CSS_SUB_H}; color: #D35400;">B. 🟠 Driven (Outbound)</div>'
        f'    <ul style="{LEGEND_CSS_UL}">'
        f"{li('Repository:', 'Store/Load Aggregates (Collection illusion).')}"
        f"{li('Gateway/Client:', 'External APIs (Stripe, AWS).')}"
        f"{li('Publisher:', 'Fire-and-forget event sender.')}"
        f"{li('Transaction Mgr:', 'Unit of Work (Commit/Rollback).')}"
        f"{li('ACL Facade:', 'Anti-Corruption Layer for other contexts.')}"
        f"{li('ResponseDTO:', 'Output data contract.')}"
        f"{li('AdapterError:', 'External system failure.')}"
        f"    </ul>"
        f"  </div>"
        f"</div>"
        # 4. PORTS
        f'<div style="margin-bottom: 8px; border-top: 1px solid #eee; padding-top: 4px;">'
        f'  <b style="color: #7F8C8D;">4. ⚙️ Ports (Infrastructure)</b><br>'
        f"  <i>Technological implementations (Tools).</i>"
        f'  <ul style="{LEGEND_CSS_UL}">'
        f"{li('Infrastructure Impl:', 'DB Session, HTTP Client, Drivers.')}"
        f"  </ul>"
        f"</div>"
        f"{LEGEND_HTML_NOTE}"
        f"</div>"
    )
