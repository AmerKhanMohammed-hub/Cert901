import os
import sys
from azure.identity import DefaultAzureCredential
# Import the dedicated AgentsClient layout directly from the SDK
from azure.ai.projects import AgentsClient

def test_agent_execution():
    # 1. Fetch project connection details from environment variables
    connection_string = os.getenv("AZURE_AIPROJECT_CONNECTION_STRING")
    agent_id = os.getenv("AZURE_AI_AGENT_ID")

    if not connection_string or not agent_id:
        print("❌ Error: Missing required environment variables.")
        sys.exit(1)

    print("🔐 Authenticating with Azure AI Foundry via OIDC/Default Identity...")
    credential = DefaultAzureCredential()
    
    try:
        print(f"🤖 Connecting directly to AgentsClient endpoint...")
        # 2. Initialize the dedicated client structure using the endpoint string
        agents_client = AgentsClient(
            endpoint=connection_string,
            credential=credential
        )

        print(f"🤖 Target Agent ID initialized: {agent_id}")
        
        # 3. Create a communication thread using the direct layout
        thread = agents_client.threads.create()
        print(f"🧵 Created evaluation thread: {thread.id}")

        # 4. Post a test message targeted at your Foundry IQ knowledge base
        test_prompt = "Hello! Give me a 1-sentence confirmation that your Foundry IQ knowledge base is connected and working."
        agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=test_prompt
        )

        # 5. Run the agent and wait for processing to finish
        print("⏳ Running agent and waiting for response...")
        run = agents_client.runs.create_and_process(
            thread_id=thread.id, 
            agent_id=agent_id
        )

        if run.status == "completed":
            # 6. Retrieve and validate the final answer string
            messages = agents_client.messages.list(thread_id=thread.id)
            
            # The last message in the sequence sequence is the agent's response
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
