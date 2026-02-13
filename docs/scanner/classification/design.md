# Design: Classification Module

## 1. Purpose & Responsibility

The **Classification Module** is the semantic heart of `dddguard`. While the *Detection* module operates in the **Physical World** (files, imports, AST nodes), the *Classification* module operates in the **Architectural World**.

Its primary responsibility is to issue an **Architectural Passport** for every node in the CodeGraph. It answers the question: *"What is the architectural significance of this file in the context of Domain-Driven Design?"*

**Key Responsibilities:**
* **Context Boundary Detection:** Identifying Bounded Contexts and Macro Zones.
* **Coordinate Definition:** determining the Layer, Direction (Driving/Driven), and Scope.
* **Component Identification:** Mapping file/folder patterns to DDD Archetypes (e.g., Entity, Repository, Facade).
* **Noise Filtering:** Ignoring technical markers (`__init__`, `conftest`) to focus on business assets.

---

## 2. Architectural Pipeline

The classification process is implemented as a linear **Pipeline** consisting of distinct, stateless Domain Services (Stages).



### High-Level Flow (`IdentifyComponentUseCase`)

1.  **Input:** Physical File Path (e.g., `src/billing/domain/model/order.py`)
2.  **Stage 0:** "Where am I?" (Context Discovery)
3.  **Stage 1:** "What are my coordinates?" (Layer & Direction Definition)
4.  **Stage 2:** "Which rules apply?" (Rule Prioritization)
5.  **Stage 3 & 4:** "What am I?" (Pattern Matching)
6.  **Post-Processing:** Inference & Validation.
7.  **Output:** `ComponentPassport`.

---

## 3. Detailed Stages

### Stage 0: Context Discovery
**Service:** `Stage0ContextDiscoveryService`

Implements the **"Stop-at-Layer" Algorithm**. It traverses the path parts from left to right. The first directory that matches a known DDD Layer (e.g., `domain`, `adapters`, `app`) acts as a boundary.
* **Before the Layer:** The Bounded Context (and Macro Zone).
* **At the Layer:** The Detected Layer Token.
* **After the Layer:** The Effective Internal Path.

> *Example:* `src/logistics/fleet/domain/vehicle.py`
> * Context: `fleet` (Macro: `logistics`)
> * Layer Token: `domain`

### Stage 1: Coordinate Definition
**Service:** `Stage1CoordinateDefinitionService`

Refines the raw boundary into a strict **3D Coordinate System**:
1.  **Scope:** `ROOT`, `SHARED`, or `CONTEXT` (Default).
2.  **Layer:** Refines special cases (e.g., root-level files often imply `COMPOSITION`).
3.  **Direction:** Scans for directional keywords (`driving`, `driven`, `in`, `out`) critical for Ports & Adapters.

**Feature: Token Distillation**
It strips away "Structural Noise" (layer names, direction names) from the path, leaving only **Searchable Tokens** for the next stage.
> *Input:* `adapters/driving/web/order_controller.py`
> *Searchable Tokens:* `["web", "order_controller"]` (Layer and Direction removed).

### Stage 2: Rule Prioritization
**Service:** `Stage2RulePrioritizationService`

Determines **which** regex rules should be applied. Instead of checking every possible rule (inefficient and inaccurate), it fetches a targeted **Rule Pool**.

**Sorting Strategy (The "Special Sauce"):**
1.  **Layer Weight (ASC):** Rules from the current layer (`DOMAIN`) beat rules from `GLOBAL`.
2.  **Regex Length (DESC):** Specific, long regexes (`^.*repository$`) beat generic ones (`.*`).

### Stage 3 & 4: Component Matching
**Service:** `Stage3_4ComponentMatchingService`

Executes the matching against the prioritized pool using a **Fast-Fail Strategy**:

* **Stage 3 (Structural Match):** Checks if any *folder* in the path matches a rule.
    * *Why first?* Folder structure (e.g., `/repositories/`) is a stronger architectural signal than a filename.
* **Stage 4 (Naming Match):** Checks if the *filename stem* matches a rule.
    * *Fallback:* Specific naming conventions (e.g., `user_repository.py`).

---

## 4. Domain Model

### Core Value Objects

* **`ComponentPassport`**: The final output. An immutable record of the component's architectural identity.
* **`ContextBoundaryVo`**: Intermediate result of Stage 0. Holds the "physical split" of the path.
* **`IdentificationCoordinatesVo`**: Intermediate result of Stage 1. Holds the "architectural coordinates" + clean tokens.
* **`RuleCandidate`**: A compiled regex rule with an attached weight and origin layer.

### Enums (The Ubiquitous Language)

The module relies heavily on shared Enums to enforce strict typing:
* `LayerEnum` (Domain, App, Adapters...)
* `DirectionEnum` (Driving, Driven...)
* `ComponentType` (Union of DomainType, AppType, PortType, etc.)

---

## 5. Key Algorithms & Heuristics

### A. The "Stop-at-Layer" Heuristic
Allows `dddguard` to support nested contexts of arbitrary depth without explicit configuration. It doesn't care if your context is at `src/ctx` or `src/org/team/group/ctx`. It stops parsing structure the moment it sees `domain/` or `adapters/`.

### B. Layer Inference (Post-Processing)
Handles "Floating Components". If a file's location is ambiguous (`Layer.UNDEFINED`), but its name strictly matches a Global rule (e.g., `string_utils.py` matches `GLOBAL` rules), the classifier infers the layer from the rule match.

### C. The Marker Intercept
Performance optimization. Files like `__init__.py` or `__main__.py` are intercepted immediately after Stage 1, bypassing the expensive regex matching in Stages 2-4.

---

## 6. Extensibility

The system is data-driven. Behavior is defined in Registries (`shared/domain/registry.py`), not hardcoded in services.

* To add a new Layer synonym: Update `DDD_LAYER_REGISTRY`.
* To add a new Component pattern: Update `DDD_NAMING_REGISTRY` or `DDD_STRUCTURAL_REGISTRY`.
* To change Layer priorities: Update `LAYER_WEIGHTS` in Stage 2.