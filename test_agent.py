import os
import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def test_agent_execution():
    # 1. Fetch project connection details from environment variables
    connection_string = os.getenv("AZURE_AIPROJECT_CONNECTION_STRING")
    agent_id = os.getenv("AZURE_AI_AGENT_ID")

    if not connection_string or not agent_id:
        print("❌ Error: Missing required environment variables.")
        sys.exit(1)

    print("🔐 Authenticating with Azure AI Foundry via OIDC/Default Identity...")
    credential = DefaultAzureCredential()
    
    # 2. Initialize the project client using the mandatory endpoint argument
    project_client = AIProjectClient(
        endpoint=connection_string,
        credential=credential
    )

    try:
        print(f"🤖 Connecting to Agent ID: {agent_id}")
        
        # 3. Access agent operations via the .agents namespace block
        thread = project_client.agents.create_thread()
        print(f"🧵 Created evaluation thread: {thread.id}")

        # 4. Post a test message targeted at your Foundry IQ knowledge base
        test_prompt = "Hello! Give me a 1-sentence confirmation that your Foundry IQ knowledge base is connected and working."
        project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=test_prompt
        )

        # 5. Run the agent and wait for the processing to finish
        print("⏳ Running agent and waiting for response...")
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id, 
            assistant_id=agent_id
        )

        if run.status == "completed":
            # 6. Retrieve and validate the final answer
            messages = project_client.agents.list_messages(thread_id=thread.id)
            
            # The last message in the sequence is the agent's response
            last_message = messages.data
            agent_response = "".join([text.text.value for text in last_message.content if hasattr(text, 'text')])
            
            print("\n🤖 [Agent Response]:")
            print(f"👉 {agent_response}\n")
            print("✅ Test Passed: Agent successfully responded over your cloud infrastructure.")
            sys.exit(0)
        else:
            print(f"❌ Test Failed: Agent run ended with status '{run.status}'.")
            sys.exit(1)

    except Exception as e:
        print(f"💥 Critical Error during execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_agent_execution()
