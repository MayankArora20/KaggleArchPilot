from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import AgentTool
from tools import (
    load_current_architecture, 
    save_architectural_artifacts, 
    generate_plantuml_dsl, 
    execute_audit_query
)

# --- 1. Agent Definitions ---

# 1.1. Architectus Prime (The SrArchitect)
# Model should be capable of complex JSON reasoning and tool use.
architectus_prime = LlmAgent(
    name="ArchitectusPrime",
    model="gemini-2.5-pro", # Use Pro for complex reasoning and large context
    instruction="""
    You are Architectus Prime, a Senior Cloud Architect. Your sole job is to analyze a new requirement 
    against the CURRENT_ARCHITECTURE and output a minimal, safe architectural change (the DIFF).
    
    1. Load the architecture using the 'load_current_architecture' tool.
    2. Analyze the requirement and identify affected components.
    3. Output the 'architecture_diff_json' and 'updated_architecture_json' in a single, verified JSON structure.
    4. Use the 'save_architectural_artifacts' tool to commit the artifacts.
    """,
    tools=[load_current_architecture, save_architectural_artifacts, generate_plantuml_dsl]
)

# 1.2. TaskMaster Pro (The ProjectManager)
task_master_pro = LlmAgent(
    name="TaskMasterPro",
    model="gemini-2.5-flash", # Use Flash for faster, simpler data transformation tasks
    instruction="""
    You are TaskMaster Pro, a Project Manager. Your job is to convert the architectural delta 
    provided in the input into a structured 'task_plan.json' (Jira Mock).
    
    Constraint: Ensure 100% coverage. Every item in the architecture diff must map to a task.
    Output the final task plan in the requested JSON schema (id, title, stream, arch_diff_item_id).
    """,
    # In a real setup, this agent would have a 'save_task_plan' tool
    # that inserts data into the 'tasks' table.
    tools=[]
)


# --- 2. Workflow Orchestration ---

# The main linear pipeline for the change request (ArchitectusPrime -> TaskMasterPro)
# This handles the state passing (output of A -> input of B) automatically.
main_pipeline = SequentialAgent(
    name="ArchitectureChangePipeline",
    description="Orchestrates the HLL Architecture Change to Task creation workflow.",
    sub_agents=[
        architectus_prime, 
        task_master_pro
    ],
    # The output of TaskMasterPro is the final result for the user.
)

# --- 3. Root Agent (The Dispatcher) ---

# The root agent determines whether the user wants to run the pipeline or query the audit log.
root_agent = LlmAgent(
    name="RootDispatcher",
    model="gemini-2.5-flash",
    instruction="""
    You are the Root Dispatcher. 
    - If the user provides a new requirement (e.g., "Add feature X"), delegate to the 'ArchitectureChangePipeline'.
    """,
    sub_agents=[
        main_pipeline
    ]
)