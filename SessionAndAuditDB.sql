-- DDL for the Agentic Architecture Pipeline Database

-- -----------------------------------------------------
-- Table 1: PROJECTS
-- The top-level entity, representing one software system (e.g., "E-commerce App").
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(50) NOT NULL PRIMARY KEY COMMENT 'Unique identifier for the software system (e.g., APP-ECOMMERCE).',
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workstreams_config JSON NOT NULL COMMENT 'JSON structure defining streams: backend, database, devops, etc.',
    
    -- Audit Columns (for creation context)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) COMMENT 'User ID or INITIAL_LOAD'
) ENGINE=InnoDB;


-- -----------------------------------------------------
-- Table 2: ARCHITECTURES (The Master/Current State)
-- Stores the CURRENT, authoritative HLL architecture JSON for a project.
-- This is updated only upon a successful 'COMMIT' of a session.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS architectures (
    architecture_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    
    -- The key artifact JSON for the SrArchitect Agent
    current_architecture_json JSON NOT NULL COMMENT 'The HLL constrained architecture schema (services, DBs, links).',
    
    -- Versioning/Audit
    version_number INT NOT NULL DEFAULT 1 COMMENT 'Sequential version of the architecture (1, 2, 3...).',
    status ENUM('C', 'H') NOT NULL DEFAULT 'C' COMMENT 'C: Current Live Version, H: Historical Version.',
    
    -- Audit Columns
    committed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp of the final commit.',
    committed_by VARCHAR(50) COMMENT 'User ID or AGENT_COMMIT_TOOL',
    
    UNIQUE KEY uk_current_arch (project_id, status), -- Ensures only one 'C' per project
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
) ENGINE=InnoDB;


-- -----------------------------------------------------
-- Table 3: SESSIONS (The Transactional/Workflow Run)
-- Represents one full run of the pipeline (Requirement -> Tasks).
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(64) NOT NULL PRIMARY KEY COMMENT 'Unique GUID for the entire workflow run.',
    project_id VARCHAR(50) NOT NULL,
    initial_arch_id INT NOT NULL COMMENT 'Link to the architecture version this session started with.',
    
    -- Inputs
    requirement_yaml TEXT NOT NULL COMMENT 'The raw structured text/YAML requirement change.',
    
    -- Workflow State
    status ENUM('INIT', 'ARCH_DONE', 'TASKS_DONE', 'COMMITTED', 'REJECTED') NOT NULL DEFAULT 'INIT',
    
    -- Agent 1 Artifacts
    architecture_diff_json JSON COMMENT 'The Delta output from Architectus Prime.',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) COMMENT 'The user who triggered the session.',
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (initial_arch_id) REFERENCES architectures(architecture_id)
) ENGINE=InnoDB;


-- -----------------------------------------------------
-- Table 4: TASKS (JIRA Mock)
-- Stores the final output from TaskMaster Pro, linked to a specific session.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(50) NOT NULL PRIMARY KEY COMMENT 'Generated ID (e.g., APP-101).',
    session_id VARCHAR(64) NOT NULL,
    
    -- Task Fields (Jira Mock)
    title VARCHAR(255) NOT NULL,
    description TEXT,
    stream VARCHAR(50) NOT NULL COMMENT 'backend, database, devops, etc.',
    priority ENUM('HIGH', 'MEDIUM', 'LOW') NOT NULL DEFAULT 'MEDIUM',
    dependencies JSON COMMENT 'JSON array of task_ids this task depends on.',
    
    -- Traceability Column (CRITICAL for Forensics Agent)
    arch_diff_item_id VARCHAR(50) NOT NULL COMMENT 'The ID from the architecture_diff.json element that triggered this task.',
    
    -- Audit Columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_agent VARCHAR(50) COMMENT 'Agent name (e.g., TaskMaster Pro).',
    model_version VARCHAR(50) COMMENT 'LLM model version used for task generation.',
    
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
) ENGINE=InnoDB;


-- -----------------------------------------------------
-- Indexes for performance
-- -----------------------------------------------------
CREATE INDEX idx_arch_project_version ON architectures(project_id, version_number);
CREATE INDEX idx_session_project_status ON sessions(project_id, status);
CREATE INDEX idx_task_arch_diff ON tasks(arch_diff_item_id);