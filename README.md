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

## Usage

Deploy the MCP server tools in this repository to your own AgentCore Runtime to verify system specifications in your environment. Results may vary slightly based on region and system load, but should be consistent with the findings documented here.

## Disclaimer

System specifications may change over time as AWS continues to optimise the AgentCore Runtime service. Always refer to official AWS documentation for the most current information.

---

*This repository was created to provide definitive answers to customer questions about AgentCore Runtime system specifications and billing behaviour.*
