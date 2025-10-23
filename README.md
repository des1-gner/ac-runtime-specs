# AgentCore Runtime System Specifications Testing

This repository contains practical testing code used to determine the actual system specifications and capabilities of Amazon Bedrock AgentCore Runtime sessions.

## Overview

Amazon Bedrock AgentCore Runtime provides dedicated microVMs for each session, but the exact specifications aren't fully documented. This testing suite was created to gather real-world data about CPU, memory, and storage allocations within AgentCore Runtime sessions.

## What We Discovered

Through practical testing, we confirmed the following AgentCore Runtime specifications:

### System Architecture
- **Platform:** Linux (Amazon Linux 2023) on ARM64 architecture
- **Kernel:** 6.1.134-6.224.amzn2023.aarch64
- **Node:** localhost

### CPU Specifications
- **Allocation:** 2 vCPUs (ARM64 architecture)
- **Billing:** $0.0895 per vCPU-hour, calculated per second
- **I/O Wait Handling:** No CPU charges during I/O wait periods
- **Load Average:** Typically very low (0.13, 0.03, 0.01 during testing)

### Memory Specifications
- **Total Allocation:** ~7.77GB (8,339,812,352 bytes)
- **Available for Applications:** ~7.30GB after system overhead
- **System Overhead:** ~0.47GB (6% of total)
- **Billing:** $0.00945 per GB-hour, calculated per second on peak usage
- **Minimum Billing:** 128MB threshold

### Storage Specifications
- **Total Local Storage:** ~8.76GB (9,407,123,456 bytes)
- **Available Space:** ~7.93GB
- **File System:** Ephemeral - wiped on session termination
- **Mount Restrictions:** No Docker volume mounts or bind mounts supported
- **Working Directory:** Root (/) with full read/write access
- **Temp Directory:** /tmp available and writable

### Session Characteristics
- **Maximum Duration:** 8 hours
- **Inactivity Timeout:** 15 minutes
- **Isolation:** Complete microVM isolation per session
- **Memory Sanitisation:** Complete cleanup on session termination

## Prerequisites

- Python 3.10 or higher
- AWS account with appropriate permissions
- AWS CLI configured with admin credentials

## Project Structure

```
ac-runtime-specs/
├── server/
│   ├── system_info_mcp_server.py    # MCP server with system info tools
│   └── requirements.txt             # Server dependencies
├── client/
│   ├── test_system_info_client.py   # Test client
│   └── requirements.txt             # Client dependencies
└── README.md                        # This file
```

## Setup and Deployment

### Step 1: Create the MCP Server

Create `server/system_info_mcp_server.py`:

```python
from mcp.server.fastmcp import FastMCP
import boto3
import os
import psutil
import platform
import json

mcp = FastMCP("system_info_mcp_server", host="0.0.0.0", stateless_http=True)

@mcp.tool()
def get_system_info() -> dict:
    """Get comprehensive system information including CPU, memory, and storage details"""
    try:
        # CPU Information
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory Information
        memory = psutil.virtual_memory()
        
        # Disk Information
        disk_usage = psutil.disk_usage('/')
        
        # Platform Information
        system_info = {
            "platform": {
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "cpu": {
                "logical_cores": cpu_count,
                "physical_cores": cpu_count_physical,
                "current_frequency_mhz": cpu_freq.current if cpu_freq else "N/A",
                "min_frequency_mhz": cpu_freq.min if cpu_freq else "N/A",
                "max_frequency_mhz": cpu_freq.max if cpu_freq else "N/A",
                "current_usage_percent": cpu_percent
            },
            "memory": {
                "total_bytes": memory.total,
                "total_gb": round(memory.total / (1024**3), 2),
                "available_bytes": memory.available,
                "available_gb": round(memory.available / (1024**3), 2),
                "used_bytes": memory.used,
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent
            },
            "storage": {
                "total_bytes": disk_usage.total,
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_bytes": disk_usage.used,
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_bytes": disk_usage.free,
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "usage_percent": round((disk_usage.used / disk_usage.total) * 100, 2)
            }
        }
        
        return system_info
    except Exception as e:
        return {"error": f"Failed to get system info: {str(e)}"}

@mcp.tool()
def get_cpu_details() -> dict:
    """Get detailed CPU information and current usage"""
    try:
        cpu_percent_overall = psutil.cpu_percent(interval=1)
        cpu_percent_per_core = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        try:
            load_avg = os.getloadavg()
        except:
            load_avg = "N/A (Windows system)"
        
        return {
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "current_usage_percent": cpu_percent_overall,
            "per_core_usage_percent": cpu_percent_per_core,
            "frequency": {
                "current_mhz": cpu_freq.current if cpu_freq else "N/A",
                "min_mhz": cpu_freq.min if cpu_freq else "N/A",
                "max_mhz": cpu_freq.max if cpu_freq else "N/A"
            },
            "load_average": load_avg,
            "architecture": platform.machine(),
            "processor": platform.processor()
        }
    except Exception as e:
        return {"error": f"Failed to get CPU details: {str(e)}"}

@mcp.tool()
def get_memory_details() -> dict:
    """Get detailed memory information"""
    try:
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        
        return {
            "virtual_memory": {
                "total_bytes": virtual_mem.total,
                "total_gb": round(virtual_mem.total / (1024**3), 2),
                "available_bytes": virtual_mem.available,
                "available_gb": round(virtual_mem.available / (1024**3), 2),
                "used_bytes": virtual_mem.used,
                "used_gb": round(virtual_mem.used / (1024**3), 2),
                "free_bytes": virtual_mem.free,
                "free_gb": round(virtual_mem.free / (1024**3), 2),
                "usage_percent": virtual_mem.percent,
                "buffers_bytes": getattr(virtual_mem, 'buffers', 0),
                "cached_bytes": getattr(virtual_mem, 'cached', 0)
            },
            "swap_memory": {
                "total_bytes": swap_mem.total,
                "total_gb": round(swap_mem.total / (1024**3), 2),
                "used_bytes": swap_mem.used,
                "used_gb": round(swap_mem.used / (1024**3), 2),
                "free_bytes": swap_mem.free,
                "free_gb": round(swap_mem.free / (1024**3), 2),
                "usage_percent": swap_mem.percent
            }
        }
    except Exception as e:
        return {"error": f"Failed to get memory details: {str(e)}"}

@mcp.tool()
def get_storage_details() -> dict:
    """Get detailed storage information for all mounted filesystems"""
    try:
        storage_info = {}
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                storage_info[partition.mountpoint] = {
                    "device": partition.device,
                    "filesystem": partition.fstype,
                    "total_bytes": partition_usage.total,
                    "total_gb": round(partition_usage.total / (1024**3), 2),
                    "used_bytes": partition_usage.used,
                    "used_gb": round(partition_usage.used / (1024**3), 2),
                    "free_bytes": partition_usage.free,
                    "free_gb": round(partition_usage.free / (1024**3), 2),
                    "usage_percent": round((partition_usage.used / partition_usage.total) * 100, 2)
                }
            except PermissionError:
                storage_info[partition.mountpoint] = {"error": "Permission denied"}
        
        return storage_info
    except Exception as e:
        return {"error": f"Failed to get storage details: {str(e)}"}

@mcp.tool()
def test_file_operations() -> dict:
    """Test local filesystem operations and measure available space"""
    try:
        import tempfile
        import time
        
        results = {}
        
        # Test writing to current directory
        try:
            test_file = "agentcore_test_file.txt"
            test_content = "This is a test file created by AgentCore Runtime\n" * 1000
            
            start_time = time.time()
            with open(test_file, 'w') as f:
                f.write(test_content)
            write_time = time.time() - start_time
            
            file_size = os.path.getsize(test_file)
            
            start_time = time.time()
            with open(test_file, 'r') as f:
                read_content = f.read()
            read_time = time.time() - start_time
            
            os.remove(test_file)
            
            results["current_directory"] = {
                "writable": True,
                "file_size_bytes": file_size,
                "write_time_seconds": round(write_time, 4),
                "read_time_seconds": round(read_time, 4),
                "content_matches": len(read_content) == len(test_content)
            }
        except Exception as e:
            results["current_directory"] = {"writable": False, "error": str(e)}
        
        # Test temp directory
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
                tmp_file.write("Temporary file test")
                temp_path = tmp_file.name
            
            temp_size = os.path.getsize(temp_path)
            os.unlink(temp_path)
            
            results["temp_directory"] = {
                "writable": True,
                "temp_path": os.path.dirname(temp_path),
                "test_file_size": temp_size
            }
        except Exception as e:
            results["temp_directory"] = {"writable": False, "error": str(e)}
        
        # Get current working directory info
        cwd = os.getcwd()
        results["working_directory"] = {
            "path": cwd,
            "exists": os.path.exists(cwd),
            "writable": os.access(cwd, os.W_OK),
            "readable": os.access(cwd, os.R_OK)
        }
        
        return results
    except Exception as e:
        return {"error": f"Failed to test file operations: {str(e)}"}

@mcp.tool()
def get_aws_region() -> str:
    """Get the current AWS region using boto3"""
    session = boto3.Session()
    return session.region_name

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### Step 2: Create Requirements Files

Create `server/requirements.txt`:
```
mcp
boto3
bedrock-agentcore
bedrock-agentcore-starter-toolkit
psutil
```

Create `client/requirements.txt`:
```
mcp
boto3
run-mcp-servers-with-aws-lambda
```

### Step 3: Deploy the MCP Server

Navigate to the server directory and configure:

```bash
cd server
agentcore configure -e system_info_mcp_server.py --protocol MCP
```

During configuration:
- **Execution Role:** Press Enter to auto-create
- **ECR Repository:** Press Enter to auto-create  
- **Dependency file:** Press Enter to use detected requirements.txt
- **Authorisation:** Choose no for OAuth (uses IAM by default)

Deploy to AWS:

```bash
agentcore launch
```

Save the Agent ARN returned after successful deployment.

### Step 4: Create Test Client

Create `client/test_system_info_client.py`:

```python
import boto3
import asyncio
from mcp import ClientSession
from mcp_lambda.client.streamable_http_sigv4 import streamablehttp_client_with_sigv4
import json

def generate_mcp_url(agent_runtime_arn: str, region: str) -> str:
    encoded_arn = agent_runtime_arn.replace(':', '%3A').replace('/', '%2F')
    return f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"

async def test_system_info():
    # Replace with your actual Agent ARN and region
    agent_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/system_info_mcp_server-abc123"
    region = "us-east-1"
    
    mcp_url = generate_mcp_url(agent_arn, region)
    print(f"Connecting to: {mcp_url}")

    session = boto3.Session()
    credentials = session.get_credentials()
    
    try:
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
                
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_system_info())
```

### Step 5: Run the Tests

Navigate to the client directory and install dependencies:

```bash
cd ../client
pip install -r requirements.txt
```

Update the `agent_arn` and `region` variables in `test_system_info_client.py` with your actual values, then run:

```bash
python3 test_system_info_client.py
```

## Testing Tools

This repository includes MCP (Model Context Protocol) server tools that can be deployed to AgentCore Runtime to gather system information:

- `get_system_info()` - Complete system overview
- `get_cpu_details()` - Detailed CPU information and usage
- `get_memory_details()` - Memory allocation and usage patterns
- `get_storage_details()` - File system and storage information
- `test_file_operations()` - Local file system capability testing

## Key Findings

1. **True Consumption Billing:** You only pay for actual CPU usage during active processing, not during I/O wait periods
2. **Fixed Hardware Allocation:** All sessions receive the same 2 vCPU / ~8GB RAM allocation
3. **Generous Local Storage:** ~8GB of ephemeral storage available for temporary operations
4. **Enterprise Security:** Complete microVM isolation with memory sanitisation
5. **No Persistent Storage:** Local file system is ephemeral; use AgentCore Memory service for persistence

## Cost Implications

Based on our testing, the per-second billing calculations are:
- **CPU:** $0.0000248611 per vCPU-second (only during active processing)
- **Memory:** $0.000002625 per GB-second (continuous throughout session)

This makes AgentCore Runtime very cost-effective for I/O-heavy agent workloads where CPU usage is sporadic but memory needs are consistent.

## References

This testing was conducted to support AWS Premium Support cases and validate the following official documentation:

- [Amazon Bedrock AgentCore Pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
- [AgentCore Runtime How It Works](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html)
- [AgentCore Memory Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [AWS Pricing Calculator for AgentCore](https://calculator.aws/#/createCalculator/bedrockagentcore)
- [AgentCore Runtime Blog Post](https://aws.amazon.com/blogs/machine-learning/securely-launch-and-scale-your-agents-and-tools-on-amazon-bedrock-agentcore-runtime/)

## Disclaimer

This testing was conducted for AWS Premium Support purposes. System specifications may change over time as AWS continues to optimise the AgentCore Runtime service. Always refer to official AWS documentation for the most current information.

---

*This repository was created to provide definitive answers to customer questions about AgentCore Runtime system specifications and billing behaviour.*
