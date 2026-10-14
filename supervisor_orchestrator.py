import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def execute_supervisor_workflow():
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    supervisor_id = os.getenv("AZURE_AI_AGENT_ID")

    if not project_endpoint or not supervisor_id:
        print("❌ Error: Missing required environment variables (AZURE_AI_PROJECT_ENDPOINT or AZURE_AI_AGENT_ID).")
        sys.exit(1)

    print("🔐 Authenticating identity via secure cloud credential bridge...")
    credential = DefaultAzureCredential()
    
    try:
        project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
        agent_client = project_client.agents
        print("✅ Connected to Microsoft Foundry Control Plane.")

        # 1. Define target worker IDs (Your verified Entra GUIDs)
        pdf_worker_id = "88481e79-bfc1-4461-b317-fc5cf93168fd"
        india_worker_id = "8b346c52-bc15-4727-a332-f0d5b1326cd3"

        print("🧵 Initialising a fresh multi-agent execution thread...")
        thread = agent_client.create_thread()

        # 2. Programmatic Worker 1 Execution: Pull historical context
        print("➡️ Step 1: Querying PDF Data Specialist...")
        agent_client.create_message(thread_id=thread.id, role="user", content="Extract historical dining slip menu items.")
        run_w1 = agent_client.create_and_process_run(thread_id=thread.id, assistant_id=pdf_worker_id)
        print(f"   [Worker 1 Finished with status: {run_w1.status}]")

        # 3. Programmatic Worker 2 Execution: Pull modern lodge parameters
        print("➡️ Step 2: Querying India File Researcher...")
        agent_client.create_message(thread_id=thread.id, role="user", content="Fetch active lodge address details for New Delhi.")
        run_w2 = agent_client.create_and_process_run(thread_id=thread.id, assistant_id=india_worker_id)
        print(f"   [Worker 2 Finished with status: {run_w2.status}]")

        # 4. Final Supervisor Synthesis Execution
        print("👑 Step 3: Invoking Supervisor to consolidate and compare datasets...")
        synthesis_prompt = (
            "Review the full conversation history above containing the historical menu data from Worker 1 "
            "and the active New Delhi lodge parameters from Worker 2. Compare the datasets and "
            "synthesize a single, unified markdown review table/list for the user."
        )
        agent_client.create_message(thread_id=thread.id, role="user", content=synthesis_prompt)
        
        run_supervisor = agent_client.create_and_process_run(thread_id=thread.id, assistant_id=supervisor_id)
        print(f"🏁 Run execution finalized with Status: {run_supervisor.status}")

        # 5. Extract and print the final supervisor message text
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
