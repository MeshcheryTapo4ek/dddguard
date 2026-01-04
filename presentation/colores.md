1. The Core (Внутренний круг)
🟦 Domain (Business Logic)

Role: Entities, VO, Aggregates.

Hex: #3B82F6 (Blue-500)

Fill: #3B82F6 (Solid) или #1E3A8A (Darker fill)

Meaning: Холодный разум, чистая логика, стабильность.

🟪 Application (Orchestration)

Role: UseCases, Workflows, Handlers.

Hex: #A855F7 (Purple-500)

Fill: #A855F7 (Solid) или #581C87 (Darker fill)

Meaning: Магия соединения, управление процессами.

2. The Shell (Внешний круг)
Чтобы на схемах было четко видно направление данных (слева-направо или сверху-вниз), разделим адаптеры:

🟧 Driving Side (Input / Entry)

Role: Controllers, CLI Commands, Event Consumers.

Hex: #F97316 (Orange-500)

Meaning: Энергия, входящий импульс, "Горячая" зона.

🟩 Driven Side (Output / Infra)

Role: Repositories, API Clients, Gateways.

Hex: #22C55E (Green-500)

Meaning: Результат, сохранение, "Безопасная" зона.

3. The Glue (Связи)
⬜ DTO (Data Transfer Objects)

Role: Request/Response models.

Hex: #94A3B8 (Slate-400)

Style: Серый фон, возможно скругленные углы, так как это пассивные данные.

🟨 Ports (Interfaces)

Role: Abstract Interfaces / Protocols.

Hex: #EAB308 (Yellow-500)

Style: Часто изображаются как "Socket" (полукруг) или прямоугольник с пунктирной обводкой (Dashed Border), так как это контракт, а не реализация.

🟥 Composition Root

Role: DI Container, Main.

Hex: #F43F5E (Rose-500)

Meaning: Сборка, системный уровень.