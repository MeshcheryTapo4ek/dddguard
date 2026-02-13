# DDDGuard — Dependency Rules Specification

This document defines the complete set of architectural dependency rules
enforced by the DDDGuard Linter. Every import in a scanned project is validated
against these rules.

---

## Terminology

| Term | Meaning |
|---|---|
| **Layer** | Architectural layer: Domain, App, Ports, Adapters, Composition |
| **Direction** | Sub-layer direction: Driving (inbound) or Driven (outbound) |
| **Scope** | Module scope: Context, Shared, Root |
| **Bounded Context** | An autonomous module with its own layer stack |
| **Macro Context** | A parent context that orchestrates child contexts |
| **Leaf Context** | A terminal context with no children |
| **ACL** | Anti-Corruption Layer — a driven port that translates between contexts |
| **Passport** | `ComponentPassport` — architectural metadata assigned to every code node |

---

## How Rules Are Applied

For every import `source -> target` found in the code graph, the Linter:

1. Checks **bypass conditions** (skip if any match)
2. Determines the **relationship** between source and target contexts
3. Applies the matching **rule group**

```
source -> target
  │
  ├─ [Bypass?] -> skip
  │
  ├─ Same context?           -> Group 1: Internal Rules
  ├─ Parent-child kinship?   -> Group 2: Fractal Rules
  ├─ No kinship (alien)?     -> Group 3: Cross-Context Rules
  └─ Shared/Root scope?      -> Group 4: Scope Isolation Rules
```

---

## Bypass Conditions

These imports are **always allowed** and skip all rule checks:

| Condition | Rationale |
|---|---|
| Target scope is **SHARED** | Shared kernel is globally accessible |
| Source layer is **COMPOSITION** | Composition wires everything within its context |
| Source or target has no `ComponentPassport` | Unclassified nodes cannot be validated |

---

## Group 1: Internal Rules (Same Context)

These rules control which layers can depend on which layers **within a single
bounded context**. They account for both `layer` and `direction`.

### 1. Domain Purity

| | |
|---|---|
| **Source** | Domain (any direction) |
| **Allowed targets** | Domain, Global |
| **Forbidden targets** | App, Ports, Adapters, Composition |
| **Severity** | error |

Domain is the innermost layer. It contains pure business logic and must have
zero dependencies on infrastructure, frameworks, or orchestration layers.

```
domain/order_entity.py  ->  domain/money_vo.py       ✅
domain/order_entity.py  ->  app/create_order_uc.py    ❌ Domain Purity
domain/order_entity.py  ->  ports/driving/facade.py   ❌ Domain Purity
```

### 2. App Isolation

| | |
|---|---|
| **Source** | App (any direction) |
| **Allowed targets** | App (own interfaces), Domain, Global |
| **Forbidden targets** | Ports, Adapters, Composition |
| **Severity** | error |

The application layer orchestrates domain logic through use cases and workflows.
It defines abstract interfaces (`app/interfaces.py`) for external dependencies
and receives concrete implementations via dependency injection. It never imports
ports or adapters directly.

```
app/create_order_uc.py  ->  domain/order_entity.py     ✅
app/create_order_uc.py  ->  app/interfaces.py           ✅
app/create_order_uc.py  ->  ports/driven/repo.py        ❌ App Isolation
app/create_order_uc.py  ->  adapters/driving/cli.py     ❌ App Isolation
```

### 3. Driving Port Boundary

| | |
|---|---|
| **Source** | Ports + DRIVING direction (Facade, Dispatcher, Schema) |
| **Allowed targets** | App, Domain, Ports/Driving (own schemas), Global |
| **Forbidden targets** | Ports/Driven, Adapters (any), Composition |
| **Severity** | error |

Driving ports are the public entry points to a bounded context. A facade
receives external calls, validates input, invokes use cases, and maps domain
results to response schemas.

```
ports/driving/facade.py   ->  app/create_order_uc.py       ✅
ports/driving/facade.py   ->  ports/driving/schemas.py      ✅
ports/driving/facade.py   ->  ports/driven/repo.py          ❌ Driving Port Boundary
ports/driving/facade.py   ->  adapters/driving/cli.py       ❌ Driving Port Boundary
```

### 4. Driven Port Boundary

| | |
|---|---|
| **Source** | Ports + DRIVEN direction (Repository, ACL, Gateway, Publisher) |
| **Allowed targets** | App (interfaces), Domain, Adapters/Driven (tools), Global |
| **Forbidden targets** | Ports/Driving (own), Adapters/Driving, Composition |
| **Severity** | error |

Driven ports implement the abstract interfaces defined in `app/interfaces.py`.
They perform the translation between domain language and external systems.
ACL ports additionally may import driving ports of **other** contexts (see
Group 3: Cross-Context Inbound).

```
ports/driven/pg_repo.py     ->  app/interfaces.py            ✅  (implements)
ports/driven/pg_repo.py     ->  domain/order_entity.py       ✅  (maps to/from)
ports/driven/pg_repo.py     ->  adapters/driven/db_engine.py ✅  (uses tool)
ports/driven/pg_repo.py     ->  ports/driving/facade.py      ❌  Driven Port Boundary
ports/driven/acl/scanner.py ->  other_ctx/ports/driving/...  ✅  (ACL cross-context)
```

### 5. Driving Adapter Boundary

| | |
|---|---|
| **Source** | Adapters + DRIVING direction (Controller, CLI, Consumer) |
| **Allowed targets** | Ports/Driving (facades, schemas), Global |
| **Forbidden targets** | Domain, App, Ports/Driven, Adapters/Driven, Composition |
| **Severity** | error |

Driving adapters are thin infrastructure wrappers (HTTP controllers, CLI
commands, message consumers). They delegate all logic to driving ports and must
not access domain or application layers directly.

```
adapters/driving/cli.py  ->  ports/driving/facade.py     ✅
adapters/driving/cli.py  ->  ports/driving/schemas.py    ✅
adapters/driving/cli.py  ->  domain/order_entity.py      ❌ Driving Adapter Boundary
adapters/driving/cli.py  ->  app/create_order_uc.py      ❌ Driving Adapter Boundary
```

### 6. Driven Adapter Boundary

| | |
|---|---|
| **Source** | Adapters + DRIVEN direction (DB engine, HTTP client, Producer) |
| **Allowed targets** | Global, Shared (external libraries only) |
| **Forbidden targets** | Domain, App, Ports, Adapters/Driving, Composition |
| **Severity** | error |

Driven adapters provide raw infrastructure capabilities (database sessions,
HTTP clients, message producers). They have zero knowledge of domain concepts.
All domain-to-infrastructure mapping is the responsibility of driven ports.

```
adapters/driven/db_engine.py  ->  shared/config.py         ✅
adapters/driven/db_engine.py  ->  domain/order_entity.py   ❌ Driven Adapter Boundary
adapters/driven/db_engine.py  ->  ports/driven/repo.py     ❌ Driven Adapter Boundary
```

### 7. Composition (Free Zone)

| | |
|---|---|
| **Source** | Composition (Container, Config, Entrypoint, Logger) |
| **Allowed targets** | Everything within the same context |
| **Forbidden targets** | Other context internals |
| **Severity** | — (bypassed for intra-context) |

Composition is the wiring layer. It assembles all dependencies via DI
containers and may import any layer within its own context.

---

## Group 2: Fractal Rules (Parent ↔ Child Contexts)

These rules apply when two contexts have a **parent-child kinship** — the
child context is nested inside the parent (macro) context.

Kinship is determined by the `macro_zone` field in `ComponentPassport`:
- **Upstream** (child -> parent): `source.macro_zone == target.context_name`
- **Downstream** (parent -> child): `target.macro_zone == source.context_name`

### 8. Fractal Upstream Access

| | |
|---|---|
| **Direction** | Child -> Parent |
| **Allowed targets** | Domain, App, Ports/Driven, Global |
| **Forbidden targets** | Ports/Driving, Adapters (any), Composition |
| **Severity** | error |

A child context can use its parent's domain types and application interfaces
as a **local shared kernel**. It can also access parent's driven ports
(repository interfaces, gateways). However, a child must not call the parent's
public facade (driving ports) or touch the parent's infrastructure.

```
detection/app/scan.py  ->  scanner/domain/value_objects.py    ✅ (parent domain)
detection/app/scan.py  ->  scanner/app/interfaces.py          ✅ (parent app)
detection/app/scan.py  ->  scanner/ports/driven/repo.py       ✅ (parent driven port)
detection/app/scan.py  ->  scanner/ports/driving/facade.py    ❌ Fractal Upstream
detection/app/scan.py  ->  scanner/adapters/driving/cli.py    ❌ Fractal Upstream
```

### 9. Fractal Downstream Access

| | |
|---|---|
| **Direction** | Parent -> Child |
| **Allowed targets** | Ports/Driving only (facades) |
| **Forbidden targets** | Domain, App, Ports/Driven, Adapters, Composition |
| **Severity** | error |

A parent context is an orchestrator. It accesses children **exclusively**
through their public driving ports (facades). No ACL is needed — children
return types in the parent's domain language.

```
scanner/app/run_scan.py  ->  detection/ports/driving/facade.py  ✅
scanner/app/run_scan.py  ->  detection/domain/parser.py         ❌ Fractal Downstream
scanner/app/run_scan.py  ->  detection/app/scan_uc.py           ❌ Fractal Downstream
```

---

## Group 3: Cross-Context Rules (Alien Contexts)

These rules apply when two contexts have **no kinship** — they are not
parent-child and not siblings sharing a common parent orchestrator.

### 10. Cross-Context Outbound

| | |
|---|---|
| **Check** | Which layer/direction is the source? |
| **Allowed source** | Ports/Driven only (ACL) |
| **Forbidden source** | Domain, App, Ports/Driving, Adapters, Composition |
| **Severity** | error |

Only a driven port (specifically, an ACL) may initiate a call to another
bounded context. This ensures all cross-context communication passes through
a translation layer.

```
ports/driven/acl/scanner.py  ->  scanner/ports/driving/...  ✅ (ACL)
app/check_project_uc.py      ->  scanner/ports/driving/...  ❌ Cross-Context Outbound
adapters/driving/cli.py      ->  scanner/ports/driving/...  ❌ Cross-Context Outbound
```

### 11. Cross-Context Inbound

| | |
|---|---|
| **Check** | Which layer/direction is the target? |
| **Allowed target** | Ports/Driving only (facades, schemas) |
| **Forbidden target** | Domain, App, Ports/Driven, Adapters, Composition |
| **Severity** | error |

When accessing another context, only its **public API** (driving ports) is
visible. Internal layers are completely hidden behind the facade boundary.

```
linter/ports/driven/acl.py  ->  scanner/ports/driving/facade.py   ✅
linter/ports/driven/acl.py  ->  scanner/domain/value_objects.py   ❌ Cross-Context Inbound
linter/ports/driven/acl.py  ->  scanner/app/run_scan_uc.py        ❌ Cross-Context Inbound
```

---

## Group 4: Scope Isolation Rules

These rules protect structural boundaries of special scopes.

### 12. Shared Independence

| | |
|---|---|
| **Source** | Any module with scope = SHARED |
| **Forbidden targets** | Any module with scope = CONTEXT or ROOT |
| **Severity** | error |

The shared kernel is the **base of the pyramid**. It provides common types,
utilities, and base classes to all contexts, but never depends on any of them.

```
shared/domain/money_vo.py  ->  shared/helpers/utils.py       ✅
shared/domain/money_vo.py  ->  ordering/domain/order.py      ❌ Shared Independence
shared/domain/money_vo.py  ->  root/composition.py           ❌ Shared Independence
```

### 13. Root Isolation

| | |
|---|---|
| **Source** | Any module with scope = ROOT |
| **Allowed targets** | Context providers (`provider.py`), Shared |
| **Forbidden targets** | Context internals (domain, app, ports, adapters) |
| **Severity** | error |

The root is the outermost shell — it assembles the application by wiring
context providers into a global DI container. It must not reach into context
internals.

```
root/composition.py  ->  ordering/provider.py              ✅
root/composition.py  ->  shared/domain/config_vo.py        ✅
root/composition.py  ->  ordering/domain/order.py          ❌ Root Isolation
root/composition.py  ->  ordering/app/create_order_uc.py   ❌ Root Isolation
```

---

## Complete Access Matrix

Summary of all 13 rules in a single table. Read as: "Source row can import
Target column".

| Source ↓ \ Target -> | Domain | App | Ports/Driving | Ports/Driven | Adapters/Driving | Adapters/Driven | Composition | Global | Shared | Foreign Ports/Driving |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Domain** | yes | -- | -- | -- | -- | -- | -- | yes | yes | -- |
| **App** | yes | yes | -- | -- | -- | -- | -- | yes | yes | -- |
| **Ports/Driving** | yes | yes | yes | -- | -- | -- | -- | yes | yes | -- |
| **Ports/Driven** | yes | yes | -- | yes | -- | yes | -- | yes | yes | **ACL** |
| **Adapters/Driving** | -- | -- | yes | -- | yes | -- | -- | yes | yes | -- |
| **Adapters/Driven** | -- | -- | -- | -- | -- | yes | -- | yes | yes | -- |
| **Composition** | yes | yes | yes | yes | yes | yes | yes | yes | yes | -- |

Legend: `yes` = allowed, `--` = forbidden (error), `ACL` = allowed for ACL ports only

---

## Rule Application Order

The linter evaluates rules in this priority order (first match wins):

```
1. Bypass conditions          -> skip (no violation)
2. Scope isolation (#12, #13) -> check Shared/Root boundaries
3. Same context (#1–#7)       -> check internal layer matrix
4. Fractal kinship (#8, #9)   -> check parent-child rules
5. Alien contexts (#10, #11)  -> check cross-context boundaries
```

---

## Version History

| Date | Change |
|---|---|
| 2026-02-12 | Initial specification. Replaced opaque codes (R100, F101, C201, etc.) with named rules. Added direction-aware checks for Ports and Adapters. Added Shared Independence and Root Isolation rules. |
