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
        print("✅ Connected to Microsoft Foundry Control Plane.")

        # Reference your target worker GUID entries
        pdf_worker_id = "88481e79-bfc1-4461-b317-fc5cf93168fd"
        india_worker_id = "8b346c52-bc15-4727-a332-f0d5b1326cd3"

        print("💬 Initialising a fresh multi-agent session using the stable Responses API...")
        
        with project_client.get_openai_client() as openai_client:
            
            # --- Step 1: Query PDF Data Specialist Worker ---
            print(f"➡️ Step 1: Invoking PDF Data Specialist (ID: {pdf_worker_id})...")
            w1_response = openai_client.responses.create(
                model="gpt-5-mini",
                input="Extract historical dining slip menu items from your attached knowledge base.",
                extra_body={
                    "agent_reference": {
                        "id": pdf_worker_id,
                        "name": "orange-agent-nfn0jysq17",  # Required field to pass API payload verification
                        "type": "agent_reference"
                    }
                }
            )
            # Safely extract text string from production object schema
            w1_text = getattr(w1_response, "output_text", str(w1_response))
            print("   [Worker 1 Data Retrieved Successfully]")

            # --- Step 2: Query India File Researcher Worker ---
            print(f"➡️ Step 2: Invoking India File Researcher (ID: {india_worker_id})...")
            w2_response = openai_client.responses.create(
                model="gpt-5-mini",
                input="Fetch active lodge address details for New Delhi from your lodges data asset.",
                extra_body={
                    "agent_reference": {
                        "id": india_worker_id,
                        "name": "India-Lodge-Research-Worker",  # Required field to pass API payload verification
                        "type": "agent_reference"
                    }
                }
            )
            w2_text = getattr(w2_response, "output_text", str(w2_response))
            print("   [Worker 2 Data Retrieved Successfully]")

            # --- Step 3: Invoke Master Supervisor for Final Consolidation ---
            print(f"👑 Step 3: Driving Master Supervisor (ID: {supervisor_id}) for synthesis...")
            
            synthesis_prompt = (
                f"You are the master orchestrator. Review the data parameters gathered below:\n\n"
                f"DATASET 1 (Historical Menu): {w1_text}\n\n"
                f"DATASET 2 (Delhi Lodge Address): {w2_text}\n\n"
                f"Compare these datasets and compile a clean, unified markdown review list for the user."
            )
            
            final_response = openai_client.responses.create(
                model="gpt-5-mini",
                input=synthesis_prompt,
                extra_body={
                    "agent_reference": {
                        "id": supervisor_id,
                        "name": "Masonic-Ecosystem-Supervisor",  # Required field to pass API payload verification
                        "type": "agent_reference"
                    }
                }
            )

            print("\n🏆 --- UNIFIED MULTI-AGENT RESPONSE --- 🏆\n")
            print(getattr(final_response, "output_text", str(final_response)))
            print("\n===========================================")
            
        sys.exit(0)

    except Exception as e:
        print(f"❌ Execution Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_supervisor_workflow()
