import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def update_agent_system_prompt():
    # 1. Fetch environment context using the Project Endpoint URL
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    agent_id = os.getenv("AZURE_AI_AGENT_ID")

    if not project_endpoint or not agent_id:
        print("❌ Error: Missing required environment variables (AZURE_AI_PROJECT_ENDPOINT or AZURE_AI_AGENT_ID).")
        sys.exit(1)

    print("🔐 Authenticating with Azure Entra ID via OIDC...")
    credential = DefaultAzureCredential()

    try:
        # 2. Modern Client Initialization: Pass endpoint directly into the constructor
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=credential
        )
        agent_client = project_client.agents
        print("✅ Connected to Azure AI Foundry Project.")

        # 3. Rest of your system prompt configuration...
        new_prompt = (
            "You are the master Orchestrator Agent. You do not have data tools or web tools of your own. "
            "Instead, you supervise two expert worker agents to answer user requests."
        )

        print(f"🔄 Updating agent ID: {agent_id}...")
        updated_agent = agent_client.update_agent(
            assistant_id=agent_id,
            instructions=new_prompt
        )

        print("🎉 Success! Agent system prompt programmatically updated in Foundry.")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Failed to update agent prompt: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    update_agent_system_prompt()
