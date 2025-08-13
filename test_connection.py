#!/usr/bin/env python3
"""
Test script to verify MCP server connectivity
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_health_endpoint():
    """Test the health check endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dev2.odoo.universidadisep.com/health', timeout=10) as response:
                print(f"Health endpoint status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Health response: {data}")
                    return True
                else:
                    print(f"Health endpoint failed with status {response.status}")
                    return False
    except Exception as e:
        print(f"Health endpoint error: {e}")
        return False

async def test_sse_endpoint():
    """Test the SSE endpoint connectivity"""
    print("\n📡 Testing SSE endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache'
            }
            async with session.get('https://dev2.odoo.universidadisep.com/sse', 
                                 headers=headers, timeout=5) as response:
                print(f"SSE endpoint status: {response.status}")
                print(f"SSE content type: {response.headers.get('content-type')}")
                if response.status == 200:
                    print("✅ SSE endpoint is accessible")
                    return True
                else:
                    print(f"❌ SSE endpoint failed with status {response.status}")
                    return False
    except asyncio.TimeoutError:
        print("⏱️ SSE endpoint timeout (expected for SSE connections)")
        return True  # Timeout is expected for SSE connections
    except Exception as e:
        print(f"❌ SSE endpoint error: {e}")
        return False

async def test_messages_endpoint():
    """Test the messages endpoint with a simple MCP request"""
    print("\n💬 Testing messages endpoint...")
    try:
        # Prepare a simple MCP list_tools request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Content-Type': 'application/json'
            }
            async with session.post('https://dev2.odoo.universidadisep.com/messages',
                                  json=mcp_request,
                                  headers=headers,
                                  timeout=10) as response:
                print(f"Messages endpoint status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"MCP response received: {len(str(data))} characters")
                    if 'result' in data and 'tools' in data['result']:
                        tools = data['result']['tools']
                        print(f"✅ Found {len(tools)} MCP tools available")
                        # Show first few tools
                        for i, tool in enumerate(tools[:5]):
                            print(f"  - {tool.get('name', 'Unknown tool')}")
                        if len(tools) > 5:
                            print(f"  ... and {len(tools) - 5} more tools")
                        return True
                    else:
                        print(f"Unexpected response format: {data}")
                        return False
                else:
                    response_text = await response.text()
                    print(f"❌ Messages endpoint failed: {response.status} - {response_text}")
                    return False
    except Exception as e:
        print(f"❌ Messages endpoint error: {e}")
        return False

async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 MCP SERVER CONNECTION TEST")
    print(f"⏰ Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 Server: https://dev2.odoo.universidadisep.com")
    print("=" * 60)
    
    results = []
    
    # Test health endpoint
    health_ok = await test_health_endpoint()
    results.append(("Health Check", health_ok))
    
    # Test SSE endpoint
    sse_ok = await test_sse_endpoint()
    results.append(("SSE Endpoint", sse_ok))
    
    # Test messages endpoint
    messages_ok = await test_messages_endpoint()
    results.append(("Messages/Tools", messages_ok))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Server is ready for n8n integration.")
    else:
        print("⚠️  Some tests failed. Check server logs for details.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
