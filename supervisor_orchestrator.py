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
        # 1. Instantiate the root control plane client
        project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
        print("✅ Connected to Microsoft Foundry Control Plane.")

        # 2. Reference your worker GUID entries (Your verified Entra IDs)
        pdf_worker_id = "88481e79-bfc1-4461-b317-fc5cf93168fd"
        india_worker_id = "8b346c52-bc15-4727-a332-f0d5b1326cd3"

        # 3. Enter the unified production OpenAI client capability block
        print("🧵 Initialising a fresh multi-agent execution thread via OpenAI layer...")
        with project_client.get_openai_client() as openai_client:
            
            # Create a persistent conversation thread space
            thread = openai_client.beta.threads.create()
            print(f"   [Thread successfully created: {thread.id}]")

            # --- Step 1: Query PDF Data Specialist Worker ---
            print("➡️ Step 1: Querying PDF Data Specialist...")
            openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="Extract historical dining slip menu items from your attached knowledge base."
            )
            run_w1 = openai_client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=pdf_worker_id
            )
            print(f"   [Worker 1 Finalized with status: {run_w1.status}]")

            # --- Step 2: Query India File Researcher Worker ---
            print("➡️ Step 2: Querying India File Researcher...")
            openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="Fetch active lodge address details for New Delhi from your lodges data asset."
            )
            run_w2 = openai_client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=india_worker_id
            )
            print(f"   [Worker 2 Finalized with status: {run_w2.status}]")

            # --- Step 3: Invoke Master Supervisor for Synthesis ---
            print("👑 Step 3: Invoking Master Supervisor to consolidate and compare datasets...")
            synthesis_prompt = (
                "Review the full conversation history above containing the historical menu data from Worker 1 "
                "and the active New Delhi lodge parameters from Worker 2. Compare the datasets and "
                "synthesize a single, unified markdown review list for the user."
            )
            openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=synthesis_prompt
            )
            run_supervisor = openai_client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=supervisor_id
            )
            print(f"🏁 Run execution finalized with Status: {run_supervisor.status}")

            # --- Step 4: Extract and display the final synthesis output ---
            messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
            print("\n🏆 --- UNIFIED MULTI-AGENT RESPONSE --- 🏆\n")
            
            # The list returns newest messages first; parse the top message text value safely
            for msg in messages:
                if msg.role == "assistant" and msg.assistant_id == supervisor_id:
                    if msg.content and hasattr(msg.content[0], 'text'):
                        print(msg.content[0].text.value)
                    break

        print("\n===========================================")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Execution Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_supervisor_workflow()
