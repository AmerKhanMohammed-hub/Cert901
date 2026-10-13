import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
# Import standard built-in data tools from the core projects module
from azure.ai.projects.models import CodeInterpreterTool
# Multi-agent connection tools live inside the agents.models namespace
from azure.ai.agents.models import ConnectedAgentTool

def execute_supervisor_workflow():
    # 1. Fetch configuration properties from pipeline environment
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    supervisor_id = os.getenv("AZURE_AI_AGENT_ID")

    if not project_endpoint or not supervisor_id:
        print("❌ Error: Missing required environment variables (AZURE_AI_PROJECT_ENDPOINT or AZURE_AI_AGENT_ID).")
        sys.exit(1)

    print("🔐 Authenticating identity via secure cloud credential bridge...")
    credential = DefaultAzureCredential()
    
    try:
        # 2. Instantiate central project client
        project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
        agent_client = project_client.agents
        print("✅ Connected to Microsoft Foundry Control Plane.")

        # 3. Define Worker GUID strings (Your verified Entra IDs)
        worker_1_id = "88481e79-bfc1-4461-b317-fc5cf93168fd"  # PDF Data Specialist
        worker_2_id = "8b346c52-bc15-4727-a332-f0d5b1326cd3"  # India File Researcher

        print(f"📦 Mapping Worker 1 (PDF Specialist): {worker_1_id}")
        print(f"📦 Mapping Worker 2 (India Researcher): {worker_2_id}")

        # 4. Instantiate the tools using the correct ConnectedAgentTool constructor
        worker_1_tool = ConnectedAgentTool(agent_id=worker_1_id)
        worker_2_tool = ConnectedAgentTool(agent_id=worker_2_id)
        orchestration_tools = [worker_1_tool, worker_2_tool]

        print(f"👑 Synchronising Master Supervisor Agent (ID: {supervisor_id})...")
        
        # 5. Attach the sub-agent tools directly to the supervisor profile
        supervisor_agent = agent_client.update_agent(
            assistant_id=supervisor_id,
            tools=orchestration_tools
        )
        print("👑 Supervisor agent successfully updated with active worker tools.")

        # 6. Initialize thread canvas and inject prompt
        print("🧵 Initialising execution thread...")
        thread = agent_client.create_thread()

        mixed_prompt = (
            "Compare the historical menu items found on our Masonic dining slip PDF with the "
            "regional data parameters for active Freemason Lodges currently operating in Mumbai or New Delhi. "
            "Coordinate with both workers to provide a single, unified breakdown."
        )
        
        print(f"\n💬 Submitting Multi-Agent Query: '{mixed_prompt}'")
        agent_client.create_message(thread_id=thread.id, role="user", content=mixed_prompt)

        # 7. Execute the orchestrated run block
        print("⚙️ Processing Supervisor delegation loop...")
        run = agent_client.create_and_process_run(thread_id=thread.id, assistant_id=supervisor_id)
        print(f"🏁 Run execution finalized with Status: {run.status}")

        # 8. Render the unified output
        messages = agent_client.list_messages(thread_id=thread.id)
        print("\n🏆 --- UNIFIED MULTI-AGENT RESPONSE --- 🏆\n")
        print(messages.data[0].content[0].text.value)
        print("\n===========================================")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Execution Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_supervisor_workflow()
