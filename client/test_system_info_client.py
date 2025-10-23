import boto3
import asyncio
from mcp import ClientSession
from mcp_lambda.client.streamable_http_sigv4 import streamablehttp_client_with_sigv4
import json
import sys
from datetime import datetime

class OutputCapture:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'w')
        self.stdout = sys.stdout
    
    def write(self, text):
        self.stdout.write(text)
        self.file.write(text)
        self.file.flush()
    
    def flush(self):
        self.stdout.flush()
        self.file.flush()
    
    def close(self):
        self.file.close()

def generate_mcp_url(agent_runtime_arn: str, region: str) -> str:
    encoded_arn = agent_runtime_arn.replace(':', '%3A').replace('/', '%2F')
    return f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"

async def test_system_info():
    # Replace with your actual Agent ARN and region
    agent_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/system_info_mcp_server-abc123"
    region = "us-east-1"
    
    # Capture output to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_capture = OutputCapture(f"output_{timestamp}.txt")
    sys.stdout = output_capture
    
    try:
        print(f"AgentCore Runtime System Specifications Test")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Agent ARN: {agent_arn}")
        print(f"Region: {region}")
        print("=" * 80)
        
        mcp_url = generate_mcp_url(agent_arn, region)
        print(f"Connecting to: {mcp_url}")

        session = boto3.Session()
        credentials = session.get_credentials()
        
        async with streamablehttp_client_with_sigv4(
            url=mcp_url,
            service="bedrock-agentcore",
            region=region,
            credentials=credentials,
            timeout=120,
            terminate_on_close=False
        ) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as mcp_session:
                print("Initialising MCP session...")
                await mcp_session.initialize()
                print("MCP session initialised successfully")
                
                print("\n" + "="*60)
                print("AGENTCORE RUNTIME SYSTEM SPECIFICATIONS")
                print("="*60)
                
                print("\n=== Complete System Information ===")
                result = await mcp_session.call_tool("get_system_info", {})
                system_info = json.loads(result.content[0].text)
                print(json.dumps(system_info, indent=2))
                
                print("\n=== Detailed CPU Information ===")
                result = await mcp_session.call_tool("get_cpu_details", {})
                cpu_info = json.loads(result.content[0].text)
                print(json.dumps(cpu_info, indent=2))
                
                print("\n=== Detailed Memory Information ===")
                result = await mcp_session.call_tool("get_memory_details", {})
                memory_info = json.loads(result.content[0].text)
                print(json.dumps(memory_info, indent=2))
                
                print("\n=== Detailed Storage Information ===")
                result = await mcp_session.call_tool("get_storage_details", {})
                storage_info = json.loads(result.content[0].text)
                print(json.dumps(storage_info, indent=2))
                
                print("\n=== File System Operations Test ===")
                result = await mcp_session.call_tool("test_file_operations", {})
                file_ops = json.loads(result.content[0].text)
                print(json.dumps(file_ops, indent=2))
                
                print("\n=== AWS Region ===")
                result = await mcp_session.call_tool("get_aws_region", {})
                print(f"Current AWS region: {result.content[0].text}")
                
                print(f"\n\nTest completed successfully at {datetime.now().isoformat()}")
                
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        raise
    finally:
        sys.stdout = output_capture.stdout
        output_capture.close()
        print(f"Output saved to: output_{timestamp}.txt")

if __name__ == "__main__":
    asyncio.run(test_system_info())