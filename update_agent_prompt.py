import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def update_agent_system_prompt():
    # 1. Fetch environment context
    connection_string = os.getenv("AZURE_AIPROJECT_CONNECTION_STRING")
    agent_id = os.getenv("AZURE_AI_AGENT_ID")

    if not connection_string or not agent_id:
        print("❌ Error: Missing required environment variables.")
        sys.exit(1)

    print("🔐 Authenticating with Azure Entra ID via OIDC...")
    credential = DefaultAzureCredential()

    try:
        # 2. Establish connection to your AI Foundry project
        project_client = AIProjectClient.from_connection_string(
            credential=credential,
            conn_str=connection_string
        )
        agent_client = project_client.agents
        print("✅ Connected to Azure AI Foundry Project.")

        # 3. Define your new, version-controlled system prompt
        # You can update this text anytime inside GitHub to change your agent's behavior
        new_prompt = (
            "You are an elite enterprise AI assistant optimized for the Cert 901 architecture. "
            "You are natively connected to search-pilot-901 and knowledgebase839. "
            "Always prioritize facts from the uploaded PDFs. Be concise, highly professional, "
            "and format your responses with clean markdown lists."
        )

        print(f"🔄 Fetching and updating agent ID: {agent_id}...")
        
        # 4. Push the update command to the Azure Control Plane
        updated_agent = agent_client.update_agent(
            assistant_id=agent_id,
            instructions=new_prompt
        )

        print("🎉 Success! Agent system prompt programmatically updated in Foundry.")
        print(f"🤖 Verified Agent ID: {updated_agent.id}")
        print(f"📝 New Instructions Cached: '{updated_agent.instructions[:100]}...'")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Failed to update agent prompt: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    update_agent_system_prompt()
