import os
import sys
import json
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Hardcoded reference to your verified cloud worker GUID entries
WORKER_MAP = {
    "call_pdf_data_specialist_worker": "88481e79-bfc1-4461-b317-fc5cf93168fd",
    "call_india_file_researcher_worker": "8b346c52-bc15-4727-a332-f0d5b1326cd3"
}

def execute_supervisor_workflow():
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    supervisor_id = os.getenv("AZURE_AI_AGENT_ID")

    if not project_endpoint or not supervisor_id:
        print("❌ Error: Missing required environment variables (AZURE_AI_PROJECT_ENDPOINT or AZURE_AI_AGENT_ID).")
        sys.exit(1)

    print("🔐 Authenticating identity via secure cloud credential bridge...")
    credential = DefaultAzureCredential()
    
    try:
        # 1. Initialize the main project client
        project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
        print("✅ Connected to Microsoft Foundry Control Plane.")

        # Define function tool metadata so the Supervisor model knows how to call them
        tools_definition = [
            {
                "type": "function",
                "function": {
                    "name": "call_pdf_data_specialist_worker",
                    "description": "Queries the historical Data Specialist Worker to extract facts from historical Masonic dining slips and menus.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The specific menu extraction query."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "call_india_file_researcher_worker",
                    "description": "Queries the India File Researcher Worker to read local files and pull active lodge addresses for New Delhi.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "The target city, e.g., New Delhi."}
                        },
                        "required": ["city"]
                    }
                }
            }
        ]

        print(f"👑 Attaching dynamic routing function capabilities to Supervisor via Immutable Versioning...")
        # Satisfy payload constraints by providing 'name' in both the parameter and inside the definition
        project_client.agents.create_version(
            agent_name="Masonic-Ecosystem-Supervisor",
            definition=PromptAgentDefinition(
                name="Masonic-Ecosystem-Supervisor",  # Required field inside definition to clear validation block
                model="gpt-5-mini",
                instructions=(
                    "You are the master Orchestrator Supervisor Agent. You delegate tasks to your specialized workers "
                    "by executing function calls. When a user asks a question, determine which function tool is "
                    "required, make the tool call, and synthesize the output data into clean markdown format."
                ),
                tools=tools_definition
            )
        )
        print("👑 Supervisor agent template successfully synchronized with runtime function schemas.")

        # 2. Enter the OpenAI execution layer for threads and routing loops
        with project_client.get_openai_client() as openai_client:
            print("🧵 Initialising multi-agent interaction thread...")
            thread = openai_client.beta.threads.create()

            mixed_prompt = (
                "Compare the historical menu items found on our Masonic dining slip PDF with the "
                "regional data parameters for active Freemason Lodges currently operating in New Delhi. "
                "Coordinate with your workers to provide a single, unified breakdown."
            )
            print(f"\n💬 Submitting Multi-Agent Query: '{mixed_prompt}'")
            openai_client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=mixed_prompt
            )

            # Create the initial run execution
            run = openai_client.beta.threads.runs.create(
                thread_id=thread.id, assistant_id=supervisor_id
            )

            # --- THE DYNAMIC ORCHESTRATION LOOP ---
            print("⚙️ Entering Autonomous Supervisor Delegation Loop...")
            while True:
                # Poll the run status
                run_status = openai_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                
                if run_status.status == "completed":
                    print("🏁 Supervisor has finished consolidation!")
                    break
                
                elif run_status.status == "requires_action":
                    print("\n👑 [SUPERVISOR ACTION]: Supervisor is dynamically calling a worker agent...")
                    tool_outputs = []
                    
                    # Intercept the worker calls requested by the Supervisor model
                    for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        if function_name in WORKER_MAP:
                            target_worker_id = WORKER_MAP[function_name]
                            print(f"   ➡️ Triggering Worker GUID: {target_worker_id} via sub-thread execution...")
                            
                            # Execute an isolated sub-run directly against the designated worker agent
                            sub_thread = openai_client.beta.threads.create()
                            
                            # Determine payload input parameter strings
                            worker_query = arguments.get("query") or arguments.get("city") or "Extract structural data targets."
                            
                            openai_client.beta.threads.messages.create(
                                thread_id=sub_thread.id, 
                                role="user", 
                                content=worker_query
                            )
                            sub_run = openai_client.beta.threads.runs.create_and_poll(
                                thread_id=sub_thread.id, assistant_id=target_worker_id
                            )
                            
                            # Fetch what the worker found in its database
                            worker_messages = openai_client.beta.threads.messages.list(thread_id=sub_thread.id)
                            
                            # Safely parse text block content values from response arrays
                            worker_output = "No data payload returned."
                            if worker_messages.data:
                                latest_msg = worker_messages.data[0] # Grab the first entry element
                                if latest_msg.content and hasattr(latest_msg.content[0], 'text'):
                                    worker_output = latest_msg.content[0].text.value
                            
                            print(f"   👤 [WORKER RESPONSE]: Captured payload data successfully.")
                            
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": worker_output
                            })
                    
                    # Submit the worker results back up to the Supervisor
                    openai_client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )
                
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    print(f"❌ Run failed with status: {run_status.status}")
                    sys.exit(1)

            # --- DISPLAY FINAL SYNTHESIS ---
            messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
            print("\n🏆 --- UNIFIED MULTI-AGENT SYNTHESIS RESPONSE --- 🏆\n")
            if messages.data:
                print(messages.data[0].content[0].text.value)
            print("\n===========================================")
            
        sys.exit(0)

    except Exception as e:
        print(f"❌ Execution Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_supervisor_workflow()
