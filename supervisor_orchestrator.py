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

        # 1. Store your worker GUID entries (Your verified Entra IDs)
        pdf_worker_id = "88481e79-bfc1-4461-b317-fc5cf93168fd"
        india_worker_id = "8b346c52-bc15-4727-a332-f0d5b1326cd3"

        print("🧵 Initialising a fresh multi-agent execution thread canvas...")
        # Production syntax maps explicitly through the .threads collection
        thread = agent_client.threads.create()
        print(f"   [Thread successfully created: {thread.id}]")

        # 2. Sequential Worker 1 Run: Pull historical menu contexts
        print("➡️ Step 1: Querying PDF Data Specialist...")
        agent_client.messages.create(
            thread_id=thread.id, 
            role="user", 
            content="Extract historical dining slip menu items from your attached knowledge base."
        )
        run_w1 = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=pdf_worker_id)
        print(f"   [Worker 1 Finalized with status: {run_w1.status}]")

        # 3. Sequential Worker 2 Run: Pull modern lodge parameters
        print("➡️ Step 2: Querying India File Researcher...")
        agent_client.messages.create(
            thread_id=thread.id, 
            role="user", 
            content="Fetch active lodge address details for New Delhi from your lodges data asset."
        )
        run_w2 = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=india_worker_id)
        print(f"   [Worker 2 Finalized with status: {run_w2.status}]")

        # 4. Final Supervisor Synthesis Run
        print("👑 Step 3: Invoking Master Supervisor to consolidate and compare datasets...")
        synthesis_prompt = (
            "Review the full conversation history above containing the historical menu data from Worker 1 "
            "and the active New Delhi lodge parameters from Worker 2. Compare the datasets and "
            "synthesize a single, unified markdown review list for the user."
        )
        agent_client.messages.create(thread_id=thread.id, role="user", content=synthesis_prompt)
        
        run_supervisor = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=supervisor_id)
        print(f"🏁 Run execution finalized with Status: {run_supervisor.status}")

        # 5. Extract and print the final supervisor message text
        messages = agent_client.messages.list(thread_id=thread.id)
        print("\n🏆 --- UNIFIED MULTI-AGENT RESPONSE --- 🏆\n")
        
        # Traverse messages list to display content safely
        for msg in reversed(list(messages.data)):
            if msg.role == "assistant" and msg.agent_id == supervisor_id:
                print(msg.content[0].text.value)
                break
                
        print("\n===========================================")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Execution Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_supervisor_workflow()
