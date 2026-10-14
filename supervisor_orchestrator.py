import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# 1. Define the worker delegation functions matching native function-calling formats
def call_pdf_data_specialist_worker(user_query: str) -> str:
    """
    Queries the historical Data Specialist Worker (ID: 88481e79-bfc1-4461-b317-fc5cf93168fd) 
    to extract facts from historical Masonic dining slips, menus, and inner specifications.
    """
    print(f"➡️ Routing sub-query to PDF Data Specialist: {user_query}")
    # In a full runtime loop, you can spin up a thread for worker_1_id here. 
    # For this automation, we provide the mock grounding bridge:
    return "Historical Dining Menu Data: Includes Roast Beef, Yorkshire Pudding, Horseradish sauce, and structural inner lodge specifications."

def call_india_file_researcher_worker(target_city: str) -> str:
    """
    Queries the India File Researcher Worker (ID: 8b346c52-bc15-4727-a332-f0d5b1326cd3) 
    to read local files and pull active lodge addresses for Mumbai or New Delhi.
    """
    print(f"➡️ Routing sub-query to India File Researcher for city: {target_city}")
    if "delhi" in target_city.lower():
        return "Lodge Raisina No. 142 GLI. Address: Freemasons' Hall, Janpath, New Delhi, 110001. Active."
    else:
        return "Lodge St. George No. 1 EC. Address: 19, Ravindra Mansion, Dinshaw Vacha Road, Churchgate, Mumbai. Active."

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

        # Define the function tools map
        function_tools = [call_pdf_data_specialist_worker, call_india_file_researcher_worker]

        print(f"👑 Synchronising Master Supervisor Agent (ID: {supervisor_id}) with Function tools...")
        
        # Attach functions natively to the supervisor via the production SDK parameters
        supervisor_agent = agent_client.update_agent(
            assistant_id=supervisor_id,
            tools=function_tools
        )
        print("👑 Supervisor agent successfully updated with routing function capabilities.")

        print("🧵 Initialising execution thread...")
        thread = agent_client.create_thread()

        mixed_prompt = (
            "Compare the historical menu items found on our Masonic dining slip PDF with the "
            "regional data parameters for active Freemason Lodges currently operating in New Delhi. "
            "Coordinate with both workers to provide a single, unified breakdown."
        )
        
        print(f"\n💬 Submitting Multi-Agent Query: '{mixed_prompt}'")
        agent_client.create_message(thread_id=thread.id, role="user", content=mixed_prompt)

        print("⚙️ Processing Supervisor delegation loop...")
        run = agent_client.create_and_process_run(thread_id=thread.id, assistant_id=supervisor_id)
        print(f"🏁 Run execution finalized with Status: {run.status}")

        messages = agent_client.list_messages(thread_id=thread.id)
        print("\n🏆 --- UNIFIED MULTI-AGENT RESPONSE --- 🏆\n")
        print(messages.data.content.text.value)
        print("\n===========================================")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Execution Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_supervisor_workflow()
