1. The Core (Inner Circle)
🟦 Domain (Business Logic)

Role: Entities, VO, Aggregates.

Hex: #3B82F6 (Blue-500)

Fill: #3B82F6 (Solid) or #1E3A8A (Darker fill)

Meaning: Cold mind, pure logic, stability.

🟪 Application (Orchestration)

Role: UseCases, Workflows, Handlers.

Hex: #A855F7 (Purple-500)

Fill: #A855F7 (Solid) or #581C87 (Darker fill)

Meaning: Connection magic, process management.

2. The Shell (Outer Circle)
To make data flow direction clearly visible on diagrams (left-to-right or top-to-bottom), we split adapters:

🟧 Driving Side (Input / Entry)

Role: Controllers, CLI Commands, Event Consumers.

Hex: #F97316 (Orange-500)

Meaning: Energy, incoming impulse, "Hot" zone.

🟩 Driven Side (Output / Infra)

Role: Repositories, API Clients, Gateways.

Hex: #22C55E (Green-500)

Meaning: Result, persistence, "Safe" zone.

3. The Glue (Connections)
⬜ DTO (Data Transfer Objects)

Role: Request/Response models.

Hex: #94A3B8 (Slate-400)

Style: Gray background, possibly rounded corners, as these are passive data.

🟨 Ports (Interfaces)

Role: Abstract Interfaces / Protocols.

Hex: #EAB308 (Yellow-500)

Style: Often depicted as a "Socket" (semicircle) or rectangle with dashed border, as this is a contract, not an implementation.

🟥 Composition Root

Role: DI Container, Main.

Hex: #F43F5E (Rose-500)

Meaning: Assembly, system level.
