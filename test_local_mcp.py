#!/usr/bin/env python3
"""
Test local MCP server functionality
"""
import asyncio
import aiohttp
import json

async def test_local_mcp():
    """Test the local MCP server"""
    base_url = "http://localhost:8002"
    
    print("=" * 60)
    print("🧪 LOCAL MCP SERVER TEST")
    print("=" * 60)
    
    # Test health endpoint
    print("🏥 Testing health endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health OK: {data}")
                else:
                    print(f"❌ Health failed: {response.status}")
    except Exception as e:
        print(f"❌ Health error: {e}")
    
    # Test MCP tools list
    print("\n📋 Testing MCP tools list...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/messages",
                                  json=mcp_request,
                                  headers={'Content-Type': 'application/json'}) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data and 'tools' in data['result']:
                        tools = data['result']['tools']
                        print(f"✅ Found {len(tools)} tools:")
                        for tool in tools:
                            print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:60]}...")
                    else:
                        print(f"❌ Unexpected response: {data}")
                else:
                    text = await response.text()
                    print(f"❌ Tools list failed: {response.status} - {text}")
    except Exception as e:
        print(f"❌ Tools list error: {e}")
    
    # Test Odoo version tool
    print("\n🔧 Testing Odoo version tool...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "odoo_version",
                "arguments": {}
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/messages",
                                  json=mcp_request,
                                  headers={'Content-Type': 'application/json'}) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data:
                        print(f"✅ Odoo version result: {data['result']}")
                    else:
                        print(f"❌ Unexpected version response: {data}")
                else:
                    text = await response.text()
                    print(f"❌ Version tool failed: {response.status} - {text}")
    except Exception as e:
        print(f"❌ Version tool error: {e}")
    
    print("=" * 60)
    print("🏁 Local test completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_local_mcp())
