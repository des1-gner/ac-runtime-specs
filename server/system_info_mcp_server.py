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