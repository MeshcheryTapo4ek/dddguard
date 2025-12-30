from typing import List
import html


def get_architecture_legend(context_names: List[str]) -> str:
    """
    Returns the rich HTML content for the diagram legend/README block.
    Structure: Domain -> App -> Adapters (Driving/Driven) -> Ports.
    """
    # Filter specific architectural contexts for the header
    business_contexts = [c for c in context_names if c not in ("root", "shared")]
    has_root = "root" in context_names
    has_shared = "shared" in context_names

    # Styles
    H2_STYLE = "margin-top:0; color: #2C3E50; font-size: 16px; border-bottom: 2px solid #BDC3C7; padding-bottom: 5px;"
    H3_STYLE = "margin-top: 10px; margin-bottom: 5px; color: #34495E; font-size: 14px; font-weight: bold;"
    TXT_STYLE = (
        "font-family: Helvetica; color: #333; font-size: 11px; line-height: 1.4;"
    )
    NOTE_STYLE = "background-color: #f4f6f7; padding: 5px; border-left: 3px solid #3498DB; font-style: italic; margin: 4px 0;"

    UL_STYLE = "margin-top: 2px; margin-bottom: 5px; padding-left: 15px;"
    LI_STYLE = "margin-bottom: 2px;"

    # Sub-header style for Adapters split
    SUB_H_STYLE = (
        "font-size: 12px; font-weight: bold; margin-top: 4px; margin-bottom: 2px;"
    )

    return (
        f'<div style="{TXT_STYLE}">'
        # --- HEADER ---
        f'<h2 style="{H2_STYLE}">🗺️ System Architecture Map</h2>'
        # --- MACRO ARCHITECTURE ---
        f'<div style="margin-bottom: 10px;">'
        f"  <b>1. Composition Root {'✅' if has_root else ''}:</b> Entry point. Wires contexts together.<br>"
        f"  <b>2. Shared Kernel {'✅' if has_shared else ''}:</b> Common Code (VOs, DTOs) reused across contexts.<br>"
        f"  <b>3. Bounded Contexts:</b> Isolated business modules ({html.escape(', '.join(business_contexts))})."
        f"</div>"
        # --- VISUAL GUIDE ---
        f'<h3 style="{H3_STYLE}">🎨 Visual Guide</h3>'
        f'<ul style="{UL_STYLE}">'
        f"  <li><b>Arrows (Imports):</b> <code>A ➜ B</code> means A imports B.</li>"
        f'  <li><b>Coloring:</b> <span style="color:#E67E22; font-weight:bold;">Source-Based.</span> All arrows from the same Node share a specific Hue.</li>'
        f"  <li><b>Wiring:</b> The <code>composition.py</code> module is the local assembler.</li>"
        f"</ul>"
        # --- LAYERS ---
        f'<h3 style="{H3_STYLE}">🏗️ Layer Anatomy</h3>'
        # 1. DOMAIN
        f'<div style="margin-bottom: 8px;">'
        f'  <b style="color: #2980B9;">1. 🔵 Domain Layer (The Core)</b><br>'
        f"  <i>Pure business logic. Isolated from infrastructure.</i>"
        f'  <ul style="{UL_STYLE}">'
        f'    <li style="{LI_STYLE}"><b>Aggregate Root:</b> Cluster root. Transaction consistency guardian.</li>'
        f'    <li style="{LI_STYLE}"><b>Entity:</b> Mutable object with Identity.</li>'
        f'    <li style="{LI_STYLE}"><b>Value Object:</b> Immutable, defined by attributes. No ID.</li>'
        f'    <li style="{LI_STYLE}"><b>Domain Service:</b> Stateless logic spanning entities.</li>'
        f'    <li style="{LI_STYLE}"><b>Factory:</b> Encapsulates complex object creation.</li>'
        f'    <li style="{LI_STYLE}"><b>Domain Event:</b> Fact that happened in the past.</li>'
        f'    <li style="{LI_STYLE}"><b>Domain Error:</b> Business rule violation.</li>'
        f"  </ul>"
        f"</div>"
        # 2. APP
        f'<div style="margin-bottom: 8px;">'
        f'  <b style="color: #8E44AD;">2. 🟣 App Layer (Orchestration)</b><br>'
        f"  <i>Coordinates scenarios. No business rules.</i>"
        f'  <ul style="{UL_STYLE}">'
        f'    <li style="{LI_STYLE}"><b>Use Case:</b> Command. Changes state. Transactional.</li>'
        f'    <li style="{LI_STYLE}"><b>Query:</b> Read-only. No side effects. Optimized.</li>'
        f'    <li style="{LI_STYLE}"><b>Workflow:</b> Long-running saga/process coordination.</li>'
        f'    <li style="{LI_STYLE}"><b>Handler:</b> Reacts to Domain/Integration events.</li>'
        f'    <li style="{LI_STYLE}"><b>Interface:</b> Abstract Port definition (Dependency Inversion).</li>'
        f'    <li style="{LI_STYLE}"><b>AppError:</b> Application-specific failure.</li>'
        f"  </ul>"
        f"</div>"
        # 3. ADAPTERS (GROUPED)
        f'<div style="margin-bottom: 8px; border-top: 1px solid #eee; padding-top: 4px;">'
        f'  <b style="color: #34495E;">3. 🔌 Adapters (Interface Layer)</b><br>'
        f"  <i>Connects the Core to the Outside World.</i>"
        # 3a. Driving
        f'  <div style="margin-left: 5px; margin-top: 4px;">'
        f'    <div style="{SUB_H_STYLE}; color: #27AE60;">A. 🟢 Driving (Inbound)</div>'
        f'    <ul style="{UL_STYLE}">'
        f'      <li style="{LI_STYLE}"><b>Controller:</b> Sync input (HTTP/RPC). Direct response.</li>'
        f'      <li style="{LI_STYLE}"><b>Consumer:</b> Async input (Queues). Background processing.</li>'
        f'      <li style="{LI_STYLE}"><b>RequestDTO:</b> Input data contract/structure.</li>'
        f'      <li style="{LI_STYLE}"><b>AdapterError:</b> Input processing failure.</li>'
        f"    </ul>"
        f"  </div>"
        # 3b. Driven
        f'  <div style="margin-left: 5px;">'
        f'    <div style="{SUB_H_STYLE}; color: #D35400;">B. 🟠 Driven (Outbound)</div>'
        f'    <ul style="{UL_STYLE}">'
        f'      <li style="{LI_STYLE}"><b>Repository:</b> Store/Load Aggregates (Collection illusion).</li>'
        f'      <li style="{LI_STYLE}"><b>Gateway/Client:</b> External APIs (Stripe, AWS).</li>'
        f'      <li style="{LI_STYLE}"><b>Publisher:</b> Fire-and-forget event sender.</li>'
        f'      <li style="{LI_STYLE}"><b>Transaction Mgr:</b> Unit of Work (Commit/Rollback).</li>'
        f'      <li style="{LI_STYLE}"><b>ACL Facade:</b> Anti-Corruption Layer for other contexts.</li>'
        f'      <li style="{LI_STYLE}"><b>ResponseDTO:</b> Output data contract.</li>'
        f'      <li style="{LI_STYLE}"><b>AdapterError:</b> External system failure.</li>'
        f"    </ul>"
        f"  </div>"
        f"</div>"
        # 4. PORTS
        f'<div style="margin-bottom: 8px; border-top: 1px solid #eee; padding-top: 4px;">'
        f'  <b style="color: #7F8C8D;">4. ⚙️ Ports (Infrastructure)</b><br>'
        f"  <i>Technological implementations (Tools).</i>"
        f'  <ul style="{UL_STYLE}">'
        f'    <li style="{LI_STYLE}"><b>Infrastructure Impl:</b> DB Session, HTTP Client, Drivers.</li>'
        f"  </ul>"
        f"</div>"
        f'<div style="{NOTE_STYLE}">'
        f"  ⚠️ <b>Note:</b> Arrows originating from <b>Error</b> objects are hidden to reduce noise."
        f"</div>"
        f"</div>"
    )
