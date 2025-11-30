The ArchPilot System

This project is developed as part of Agents Intensive - Capstone Project competition

I. The Problem & Central Idea

Enterprise systems frequently suffer from Architecture Drift, where high-level documentation (HLL docs/diagrams) falls out of sync with constantly changing code requirements. This leads to development tasks (Jira/tasks) not being rooted in the latest architecture, resulting in tactical patches instead of foundational, root fixes.
The central idea of the ArchPilot system is to eliminate this drift by creating a focused, automated pipeline that translates a structured requirement change directly into a verified architectural delta and a traceable development task plan.

II. Solution: The ArchPilot Agentic Pipeline

ArchPilot is built as a Sequential Workflow using Google's Agent Development Kit (ADK) to enforce rigor and traceability at every step.

III. The Three ADK Agents

The pipeline is driven by three specialized agents, each augmented with specific tools and context.

1. Architectus Prime (The HLL Delta Agent)

This agent serves as the system's Senior Architect, responsible for maintaining the system's structural integrity.
•	Inputs:
o	current_architecture.json: The live HLL blueprint in a constrained schema (services, DBs, links, etc.).
o	requirement_change.yaml: A structured requirement (type, impacted domain, acceptance criteria).
•	Context: Grounded on a repository of architecture best-practice patterns for microservices.
•	Tools:
o	update_architecture_json: Takes current and required changes, returns the full updated JSON and the diff JSON.
o	generate_plantuml_dsl: Converts the updated_architecture.json into C4-PlantUML DSL text for visualization.
•	Responsibilities:
o	Identify the minimal, safe impact on services and database boundaries only.
o	Produce updated_architecture.json and the critical architecture_diff.json (containing added/removed/modified components and rationale)15.

2. TaskMaster Pro (The Task Breakdown Agent)

This agent serves as the system's Project Manager, ensuring every architectural decision translates into an actionable work item.
•	Inputs:
o	architecture_diff.json: The delta output from Architectus Prime.
o	workstreams_config.json: Defines organizational streams (e.g., backend, database, devops).
o	existing_tasks.json (Optional): Used to avoid duplicates.
•	Context: Strictly constrained by the Task JSON Schema (Jira Mock Contract).
•	Tools: Tool for pushing tasks to a "Jira mock" or real API.
•	Responsibilities:
o	Map every element in the diff to a standardized task plan.
o	Ensure 100% Coverage: Every change in the diff must have at least one owning task.
o	Explicitly link the generated tasks to the specific item ID in the architecture_diff.json for full traceability.
o	Output the final task_plan.json.

3. Chronos Forensics (The Audit Agent)

This agent provides crucial Introspection and Audit capabilities, demonstrating enterprise-grade reliability.
•	Inputs:
o	Natural Language Query: User's question (e.g., "Why was the Orders Service switched to Redis last week?").
o	project_id & user_id (for authorization).
•	Context: Deep understanding of the MySQL schema, history tables ($\_v$), and audit columns.
•	Tools:
o	query_audit_log(table, filter): Executes complex SQL queries against history tables.
o	compare_architecture_versions(id1, id2).
•	Responsibilities:
o	Translate the query into complex SQL against audit/history tables.
o	Retrieve the original architecture_diff.json and the rationale for the change.
o	Synthesize the audit trail, detailing the agent, version, timestamp, and user responsible for the change.

IV. Architecture & State Management: Ensuring Enterprise Rigor
ArchPilot's strength lies in robust state management beyond ephemeral agent contexts. It persists the entire system state transactionally in MySQL using a strict Project > Session > Artifact hierarchy. Architecture tables implement versioning with Current (C) and Historical (H) flags enabling multi-version storage crucial for auditability and rollback features. Using JSON data types for current_architecture.json allows efficient relational queries while maintaining a single source of truth for the architecture model.
V. Traceability, Auditing, and Visualization
To mitigate LLM nondeterminism, all critical tables log audit columns: user_id, timestamp, and AI model version/configuration responsible for each artifact. ProjectManager links every generated task explicitly to architectural diff items via IDs, ensuring traceable lineage from requirement through development work. Visualization is offloaded to a deterministic, custom tool that converts current_architecture.json into C4-PlantUML DSL, enabling UI rendering of accurate live diagrams (SVG/PNG). This separation preserves integrity and avoids visual syntax complexity within agents.

VI. Data Persistence and Visualization (The "How")

The project uses a structured data approach to ensure integrity and human readability.

Persistence and Audit
•	Engine: MySQL is used as the transactional and relational persistence engine.
•	Structure: Data adheres to a Project > Session > Artifact hierarchy.
•	Versioning: Architecture tables include a status column to distinguish between the Current Live Version (C) and Historical Versions (H).
•	Audit Columns: Critical tables include audit columns for user_id, timestamp, and the specific AI model version used, guaranteeing full traceability.

Visualization (Diagrams-as-Code)
•	The primary output is the JSON model (current_architecture.json).
•	The C4-PlantUML DSL is used as the free, open-source method to convert the JSON model into visual diagrams (SVG/PNG) for the UI. This keeps the agent focused on data (JSON) and delegates visualization to a separate tool.


VII. The Future Vision: From Pipeline to Platform

Our future vision is to integrate this capability into a full-featured management platform:
•	Management UI Platform: A unified dashboard will allow for team/project management and provide a centralized view of all architectural changes.
•	Jira Connector: Replacing the JSON mock with a dedicated Jira API Connector Tool will enable automatic issue pushing to live systems (Jira, Azure DevOps, GitHub Issues).
•	Living Documentation: The current_architecture.json will be rendered as an interactive, always-current system map, replacing static HLL diagrams forever.
•	Future Rollback Agent: The stored historical data will enable a future agent to analyze two versions and automatically create a task plan for a rollback or feature comparison.
