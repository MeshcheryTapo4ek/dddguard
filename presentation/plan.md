Accepted. I will fix the rules of the game and structure in a single specification block. This will be our «blueprint» that we will use to build the slides.

I have defined the color encoding based on your requirements and the dddguard standard.

<macro_layout> Presentation Design System:

Color Palette (Semantic Coloring):

🔵 Domain Layer: #3B82F6 (Blue-500) — Pure logic, cold reason.

🟣 App Layer: #A855F7 (Purple-500) — Orchestration, the magic of connections.

🟢 Driving Side (Inbound): #22C55E (Green-500) — Incoming signals, "green light" for start.

Scope: Driving Ports, Driving DTO, Driving Adapters.

🟠 Driven Side (Outbound): #F97316 (Orange-500) — Outgoing side effects, warning.

Scope: Driven Ports, Driven DTO, Driven Adapters.

⚪ Shared Kernel: #94A3B8 (Slate-400) — Base, neutrality.

🔴 Root: #E11D48 (Rose-600) — Composition, entry point.

Typography:

Headings: Large, bold, sans-serif.

Accents: Use colored spans (e.g., <span class="text-blue-500">Domain</span>).

Code: Monospace, focus on lines.

</macro_layout>

Here is the approved plan in Markdown specification format:

<slide_block language="md">

I. Introduction: Chaos vs Order
Title slide (Intro).

Problem:

Chaos in projects, different structures, Code Review disputes.

Difficult onboarding and maintenance.

Solution:

Architecture as a strict contract.

Consistency through tools.

II. Macro Level: Global Map
Trinity: Root + Shared + Bounded Contexts.

Hierarchy (Mermaid Diagram):

Shared (Base) -> Contexts (Logic) -> Root (Composition).

Explanation of dependency directions.

Detailed component breakdown:

Root (Assembly of everything).

Shared Kernel (Stability, VO, DTO).

Bounded Context (Isolation).

III. Micro Level: Context Anatomy
Data flow (Mermaid Diagram):

Port -> DTO -> Adapter -> App -> Domain (and back).

Layer 1: Domain (Core) [Blue]

Entities.

Value Objects.

Aggregates.

Domain Services.

Domain Errors.

Layer 2: App (Orchestration) [Purple]

Use Cases.

Queries.

Commands.

Layer overview.

Fork: Driving vs Driven

Concept "Who pushes whom".

Driven Branch (Outgoing) [Orange]
Driven Adapters:

Repositories.

Gateways.

Publishers.

ACL (Anti-Corruption Layer).

Driven DTO: Response/event contracts.

Driven Ports: Infrastructure (DB Drivers, Clients).

Driving Branch (Incoming) [Green]
Driving Ports: Infrastructure (Web Server, CLI).

Driving DTO: Request contracts.

Driving Adapters: Controllers, Consumers.

Composition Root (Context Level):

Wiring (composition.py).

Container (DI).

IV. Tooling: dddguard
Transition: "Hard to do by hand? Guard will help".

Scan & Draw: Visualization of the dependency graph.

Lint: Rules matrix and layer protection.

Create: Scaffolder and structure generation.

V. Conclusion
Summary: Architecture as Code.

Contacts/QR. </slide_block>

<refine> Plan finalized. We go from pain to macro-structure, then dive into micro-structure (Domain -> App -> Driven -> Driving -> Wiring), and finish with the tool.
