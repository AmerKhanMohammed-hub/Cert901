import os
import sys
import json
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Hardcoded reference mapping to your verified worker GUID entries
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
        # 1. Establish connection to your central project hub
        project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
        print("✅ Connected to Microsoft Foundry Control Plane.")

        # 2. Define the schema tools matching modern payload standards
        tools_definition = [
            {
                "type": "function",
                "name": "call_pdf_data_specialist_worker",
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
                "name": "call_india_file_researcher_worker",
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

        print("👑 Synchronizing Master Supervisor Agent with function calling schemas...")
        project_client.agents.create_version(
            agent_name="Masonic-Ecosystem-Supervisor",
            definition=PromptAgentDefinition(
                model="gpt-5-mini",
                instructions=(
                    "You are the master Orchestrator Supervisor Agent. You delegate tasks to your specialized workers "
                    "by executing function calls. When a user asks a question, determine which function tool is "
                    "required, make the tool call, and synthesize the output data into clean markdown format."
                ),
                tools=tools_definition
            )
        )

        # 3. Enter the unified Responses API interaction context
        print("💬 Initialising multi-agent session using the modern Responses API...")
        with project_client.get_openai_client() as openai_client:
            
            mixed_prompt = (
                "Compare the historical menu items found on our Masonic dining slip PDF with the "
                "regional data parameters for active Freemason Lodges currently operating in New Delhi. "
                "Coordinate with your workers to provide a single, unified breakdown."
            )
            print(f"\n💬 Submitting Multi-Agent Query: '{mixed_prompt}'")
            
            # Create a conversations thread via modern data-plane routing
            conversation = openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": mixed_prompt}]
            )
            
            # --- INITIAL SUPERVISOR CALL ---
            print("⚙️ Driving Master Supervisor to analyze request intent...")
            response = openai_client.responses.create(
                conversation_id=conversation.id,
                agent_reference={
                    "id": supervisor_id,
                    "name": "Masonic-Ecosystem-Supervisor",
                    "type": "agent_reference"
                }
            )

            # --- DYNAMIC INTERCEPT TOOL LOOP ---
            # If the supervisor requests tools, status evaluates to 'requires_action'
            if getattr(response, "status", "") == "requires_action" or hasattr(response, "required_action"):
                print("\n👑 [SUPERVISOR ACTION]: Supervisor is dynamically calling a worker agent...")
                tool_outputs = []
                
                # Iterate through tool actions requested by the LLM
                tool_calls = response.required_action.submit_tool_outputs.tool_calls
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    if function_name in WORKER_MAP:
                        target_worker_id = WORKER_MAP[function_name]
                        worker_query = arguments.get("query") or arguments.get("city") or "Process data parameters."
                        
                        print(f"   ➡️ Triggering Worker GUID: {target_worker_id} dynamically...")
                        
                        # Execute a synchronous data request directly against the targeted sub-worker
                        worker_response = openai_client.responses.create(
                            model="gpt-5-mini",
                            input=worker_query,
                            extra_body={
                                "agent_reference": {
                                    "id": target_worker_id,
                                    "name": "Masonic-Worker-Node",
                                    "type": "agent_reference"
                                }
                            }
                        )
                        worker_text = getattr(worker_response, "output_text", str(worker_response))
                        print(f"   👤 [WORKER RESPONSE]: Extracted payload data successfully.")
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": worker_text
                        })
                
                print("👑 Submitting worker payloads back to Supervisor for final synthesis...")
                # Submit tool outputs back into the exact same conversation context
                response = openai_client.responses.create(
                    conversation_id=conversation.id,
                    agent_reference={
                        "id": supervisor_id,
                        "name": "Masonic-Ecosystem-Supervisor",
                        "type": "agent_reference"
                    },
                    tool_outputs=tool_outputs
                )

            print("\n🏆 --- UNIFIED MULTI-AGENT SYNTHESIS RESPONSE --- 🏆\n")
            print(getattr(response, "output_text", response.choices.message.content if hasattr(response, 'choices') else str(response)))
            print("\n===========================================")
            
        sys.exit(0)

    except Exception as e:
        print(f"❌ Execution Failure: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_supervisor_workflow()
