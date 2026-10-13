import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

def update_agent_system_prompt():
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    agent_id = os.getenv("AZURE_AI_AGENT_ID")

    if not project_endpoint or not agent_id:
        print("❌ Error: Missing required environment variables (AZURE_AI_PROJECT_ENDPOINT or AZURE_AI_AGENT_ID).")
        sys.exit(1)

    print("🔐 Authenticating with Azure Entra ID via OIDC...")
    credential = DefaultAzureCredential()

    try:
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=credential
        )
        agent_client = project_client.agents
        print("✅ Connected to Azure AI Foundry Project.")

        new_instructions = (
            "You are the master Orchestrator Agent. You do not have data tools or web tools of your own. "
            "Instead, you supervise two expert worker agents to answer user requests."
        )

        print(f"🔄 Creating a brand new version configuration for Agent ID: {agent_id}...")
        
        updated_agent = agent_client.create_version(
            agent_name="Masonic-Ecosystem-Supervisor",
            definition=PromptAgentDefinition(
                model="gpt-5-mini",
                instructions=new_instructions
            )
        )

        print("🎉 Success! A new immutable agent prompt version was programmatically deployed to Foundry.")
        print(f"🤖 New Version Active ID: {updated_agent.id}")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Failed to update agent prompt: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    update_agent_system_prompt()
