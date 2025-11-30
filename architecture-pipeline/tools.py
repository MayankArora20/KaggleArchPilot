import json
from google.adk.tools import tool

# --- Mock DB Manager (Replace with actual MySQL/SQLAlchemy/etc.) ---
class MockDB:
    """Simulates interactions with the MySQL tables."""
    def get_current_architecture(self, project_id: str) -> dict:
        # In MVP: Load from a file or mock data.
        # Real: SELECT current_architecture_json FROM architectures WHERE project_id = :project_id AND status = 'C'
        print(f"DB: Fetching current architecture for {project_id}...")
        return {"project_id": project_id, "services": [{"name": "mock-service", "data": "mock-db"}], "version": 1}

    def commit_session(self, session_data: dict) -> str:
        # In MVP: Save to file.
        # Real: Insert into sessions, update architectures table, etc.
        session_id = f"SES-{hash(json.dumps(session_data))}"
        print(f"DB: Committing new session artifacts: {session_id}")
        return session_id

    def query_audit_log(self, query: str) -> str:
        # Real: SELECT * FROM tasks_v JOIN sessions ... WHERE reason LIKE :query
        return "Audit Log: Orders Service change approved on 2025-11-01 by Architectus Prime (v3.1) because of security review."

db_manager = MockDB()
# ---------------------------------------------------------------------

@tool
def load_current_architecture(project_id: str) -> str:
    """
    Retrieves the current, committed HLL architecture JSON from the database.
    This provides the SrArchitect with its long-term memory/context.
    """
    arch = db_manager.get_current_architecture(project_id)
    return json.dumps(arch)

@tool
def save_architectural_artifacts(session_data_json: str) -> str:
    """
    Saves the new architecture diff and updated architecture to the database, 
    returning the session ID for traceability.
    Input MUST be a JSON string containing the 'architecture_diff_json' and 'updated_architecture_json'.
    """
    session_data = json.loads(session_data_json)
    session_id = db_manager.commit_session(session_data)
    return session_id

@tool
def generate_plantuml_dsl(architecture_json: str) -> str:
    """
    Generates the PlantUML DSL text required to render a diagram in the UI. 
    (Mocks actual rendering for ADK agent's use case).
    """
    # In a real tool, this would parse the JSON and output the text DSL.
    return f"@startuml\n title Architecture Delta\n component OrdersService [Orders Service] \n ...\n@enduml"

@tool
def execute_audit_query(user_query: str) -> str:
    """
    The tool for Chronos Forensics. Translates natural language into a database 
    query and retrieves the relevant audit log and history data.
    """
    return db_manager.query_audit_log(user_query)