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

    # 3. Extract the dedicated AgentsClient router to isolate method namespaces
    # This bypasses the structural 'AgentsOperations' property tracking errors
    agents_client = project_client.get_agents_client()

    try:
        print(f"🤖 Connecting to Agent ID: {agent_id}")
        
        # 4. Create a thread using the standard nested namespace layout
        thread = agents_client.threads.create()
        print(f"🧵 Created evaluation thread: {thread.id}")

        # 5. Post a test message targeted at your Foundry IQ knowledge base
        test_prompt = "Hello! Give me a 1-sentence confirmation that your Foundry IQ knowledge base is connected and working."
        agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=test_prompt
        )

        # 6. Run the agent and wait for the processing to finish
        print("⏳ Running agent and waiting for response...")
        run = agents_client.runs.create_and_process(
            thread_id=thread.id, 
            assistant_id=agent_id
        )

        if run.status == "completed":
            # 7. Retrieve and validate the final answer
            messages = agents_client.messages.list(thread_id=thread.id)
            
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
