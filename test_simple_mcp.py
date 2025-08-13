#!/usr/bin/env python3
"""
Test the simple MCP server implementation
"""
import asyncio
import aiohttp
import json

async def test_simple_mcp():
    """Test the simple MCP server directly"""
    print("🧪 Testing Simple MCP Server")
    print("=" * 50)
    
    base_url = "https://dev2.odoo.universidadisep.com"
    
    # Test 1: Health check
    print("1️⃣ Health check...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health OK")
                    print(f"   📊 Tools loaded: {data.get('tools_loaded', 0)}")
                    print(f"   🔄 Initialized: {data.get('initialized', False)}")
                else:
                    print(f"   ❌ Health failed: {response.status}")
    except Exception as e:
        print(f"   ❌ Health error: {e}")
    
    # Test 2: Initialize MCP
    print("\n2️⃣ Initialize MCP...")
    try:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": False},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "simple-test",
                    "version": "1.0.0"
                }
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/messages",
                                  json=init_request,
                                  headers={'Content-Type': 'application/json'}) as response:
                
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Initialize success")
                    print(f"   📋 Protocol: {data.get('result', {}).get('protocolVersion')}")
                else:
                    text = await response.text()
                    print(f"   ❌ Initialize failed: {text[:200]}")
    except Exception as e:
        print(f"   ❌ Initialize error: {e}")
    
    # Test 3: List tools
    print("\n3️⃣ List tools...")
    try:
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/messages",
                                  json=tools_request,
                                  headers={'Content-Type': 'application/json'}) as response:
                
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data and 'tools' in data['result']:
                        tools = data['result']['tools']
                        print(f"   ✅ Found {len(tools)} tools")
                        
                        # Show CRM tools
                        crm_tools = [t for t in tools if any(keyword in t.get('name', '').lower() 
                                                           for keyword in ['crm', 'lead', 'partner', 'opportunity'])]
                        if crm_tools:
                            print(f"   📊 CRM tools ({len(crm_tools)}):")
                            for tool in crm_tools[:5]:
                                print(f"      ✓ {tool.get('name')}")
                    else:
                        print(f"   ❌ Unexpected response: {data}")
                else:
                    text = await response.text()
                    print(f"   ❌ Tools failed: {text[:200]}")
    except Exception as e:
        print(f"   ❌ Tools error: {e}")
    
    # Test 4: Execute CRM tool
    print("\n4️⃣ Execute CRM tool...")
    try:
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_leads",
                "arguments": {"limit": 2}
            }
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f"{base_url}/messages",
                                  json=tool_request,
                                  headers={'Content-Type': 'application/json'}) as response:
                
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data:
                        print(f"   ✅ CRM tool executed successfully")
                        print(f"   📄 Result: {str(data['result'])[:150]}...")
                    elif 'error' in data:
                        print(f"   ❌ Tool error: {data['error']}")
                    else:
                        print(f"   ❓ Unexpected response: {data}")
                else:
                    text = await response.text()
                    print(f"   ❌ Tool execution failed: {text[:200]}")
    except Exception as e:
        print(f"   ❌ Tool execution error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Simple MCP test completed!")

if __name__ == "__main__":
    asyncio.run(test_simple_mcp())
