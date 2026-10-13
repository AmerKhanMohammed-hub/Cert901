import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectedAgentToolDefinition

def execute_supervisor_workflow():
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not project_endpoint:
        print("❌ Error: Missing AZURE_AI_PROJECT_ENDPOINT environment variable.")
        sys.exit(1)

    print("🔐 Authenticating identity via secure cloud credential bridge...")
    credential = DefaultAzureCredential()
    
    project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
    agent_client = project_client.agents
    print("✅ Connected to Microsoft Foundry Control Plane.")

    worker_1_id = "88481e79-bfc1-4461-b317-fc5cf93168fd"  # PDF Data Specialist
    worker_2_id = "8b346c52-bc15-4727-a332-f0d5b1326cd3"  # India File Researcher

    print(f"📦 Mapping Worker 1 (PDF Specialist): {worker_1_id}")
    print(f"📦 Mapping Worker 2 (India Researcher): {worker_2_id}")

    worker_1_tool = ConnectedAgentToolDefinition(agent_id=worker_1_id)
    worker_2_tool = ConnectedAgentToolDefinition(agent_id=worker_2_id)
    orchestration_tools = [worker_1_tool, worker_2_tool]

    print("👑 Provisioning the Master Masonic Supervisor Agent with routing paths...")
    
    supervisor_agent = agent_client.create_agent(
        model="gpt-5-mini",
        name="Masonic-Ecosystem-Supervisor",
        instructions=(
            "You are the master Orchestrator Agent. You do not have data tools or web tools of your own. "
            "Instead, you supervise two expert workers to answer user requests.\n\n"
            "Your routing paths are explicitly defined:\n"
            "- For historical dining slip data or menus, trigger your tool for Worker 88481e79-bfc1-4461-b317-fc5cf93168fd.\n"
            "- For regional details about Freemason Lodges in India, trigger your tool for Worker 8b346c52-bc15-4727-a332-f0d5b1326cd3.\n\n"
            "Analyze the incoming query, call the correct sequence of tools to gather outputs, "
            "and synthesize a clean markdown comparison for the user."
        ),
        tools=orchestration_tools
    )
    print(f"👑 Supervisor successfully initialized (ID: {supervisor_agent.id})")

    thread = agent_client.create_thread()
    mixed_prompt = (
        "Compare the historical menu items found on our Masonic dining slip PDF with the "
        "regional data parameters for active Freemason Lodges currently operating in Mumbai or New Delhi. "
        "Coordinate with both workers to provide a single, unified breakdown."
    )
    
    print(f"\n💬 Submitting Multi-Agent Query: '{mixed_prompt}'")
    agent_client.create_message(thread_id=thread.id, role="user", content=mixed_prompt)

    print("⚙️ Processing Supervisor delegation and tool-calling states...")
    run = agent_client.create_and_process_run(thread_id=thread.id, assistant_id=supervisor_agent.id)
    print(f"🏁 Run execution finalized with Status: {run.status}")

    messages = agent_client.list_messages(thread_id=thread.id)
    print("\n🏆 --- UNIFIED MULTI-AGENT RESPONSE --- 🏆\n")
    print(messages.data.content.text.value)
    print("\n===========================================")

if __name__ == "__main__":
    execute_supervisor_workflow()
