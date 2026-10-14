import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def execute_supervisor_workflow():
    # 1. Fetch project environment context
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    supervisor_id = os.getenv("AZURE_AI_AGENT_ID")

    if not project_endpoint or not supervisor_id:
        print("❌ Error: Missing required environment variables (AZURE_AI_PROJECT_ENDPOINT or AZURE_AI_AGENT_ID).")
        sys.exit(1)

    print("🔐 Authenticating identity via secure cloud credential bridge...")
    credential = DefaultAzureCredential()
    
    try:
        # 2. Establish connection to your central project hub
        project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
        print("✅ Connected to Microsoft Foundry Control Plane.")

        # 3. Reference your verified data worker GUID entries
        pdf_worker_id = "88481e79-bfc1-4461-b317-fc5cf93168fd"
        india_worker_id = "8b346c52-bc15-4727-a332-f0d5b1326cd3"

        print("💬 Initialising a fresh multi-agent session using the modern Responses API...")
        
        # 4. In the updated SDK, get_openai_client() returns the unified Responses client
        with project_client.get_openai_client() as openai_client:
            
            # --- Step 1: Query PDF Data Specialist Worker ---
            print(f"➡️ Step 1: Invoking PDF Data Specialist (ID: {pdf_worker_id})...")
            w1_conversation = openai_client.conversations.create(
                items=[{
                    "type": "message",
                    "role": "user",
                    "content": "Extract historical dining slip menu items from your attached knowledge base."
                }]
            )
            w1_response = openai_client.responses.create(
                conversation_id=w1_conversation.id,
                agent_reference={"id": pdf_worker_id}
            )
            # Safely extract the worker's textual feedback payload
            w1_text = w1_response.choices[0].message.content
            print("   [Worker 1 Data Retrieved Successfully]")

            # --- Step 2: Query India File Researcher Worker ---
            print(f"➡️ Step 2: Invoking India File Researcher (ID: {india_worker_id})...")
            w2_conversation = openai_client.conversations.create(
                items=[{
                    "type": "message",
                    "role": "user",
                    "content": "Fetch active lodge address details for New Delhi from your lodges data asset."
                }]
            )
            w2_response = openai_client.responses.create(
                conversation_id=w2_conversation.id,
                agent_reference={"id": india_worker_id}
            )
            w2_text = w2_response.choices[0].message.content
            print("   [Worker 2 Data Retrieved Successfully]")

            # --- Step 3: Invoke Master Supervisor for Final Consolidation ---
            print(f"👑 Step 3: Driving Master Supervisor (ID: {supervisor_id}) for synthesis...")
            
            # Package both gathered datasets into a single orchestrated request prompt context
            synthesis_prompt = (
                f"You are the master orchestrator. Review the data parameters gathered below:\n\n"
                f"DATASET 1 (Historical Menu): {w1_text}\n\n"
                f"DATASET 2 (Delhi Lodge Address): {w2_text}\n\n"
                f"Compare these datasets and compile a clean, unified markdown review list for the user."
            )
            
            supervisor_conversation = openai_client.conversations.create(
                items=[{
                    "type": "message",
                    "role": "user",
                    "content": synthesis_prompt
                }]
            )
            
            final_response = openai_client.responses.create(
                conversation_id=supervisor_conversation.id,
                agent_reference={"id": supervisor_id}
            )

            print("\n🏆 --- UNIFIED MULTI-AGENT RESPONSE --- 🏆\n")
            print(final_response.choices[0].message.content)
            print("\n===========================================")
            
        sys.exit(0)

    except Exception as e:
        print(f"❌ Execution Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_supervisor_workflow()
