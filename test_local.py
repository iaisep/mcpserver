#!/usr/bin/env python3
"""
Quick server test to verify if the code works locally
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_local_server():
    """Test if we can create the FastMCP app locally"""
    print("🧪 Testing local server creation...")
    
    try:
        # Import our modules
        from mcp_instance import mcp
        from config import config
        
        print(f"✅ Config loaded: host={config.server.host}, port={config.server.port}")
        print(f"✅ FastMCP instance created successfully")
        print(f"✅ MCP type: {type(mcp)}")
        
        # Check if mcp has the expected attributes
        if hasattr(mcp, 'sse_app'):
            print("✅ MCP has sse_app method")
        
        if hasattr(mcp, '_tools'):
            print(f"✅ MCP has {len(mcp._tools)} tools registered")
            for tool_name in list(mcp._tools.keys())[:5]:  # Show first 5 tools
                print(f"   - {tool_name}")
        
        # Try to create SSE app
        try:
            sse_app = mcp.sse_app()
            print(f"✅ SSE app created successfully: {type(sse_app)}")
        except Exception as sse_error:
            print(f"❌ SSE app creation failed: {sse_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating local server: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=" * 50)
    print("🔍 LOCAL SERVER VALIDATION")
    print("=" * 50)
    
    success = await test_local_server()
    
    print("=" * 50)
    if success:
        print("✅ Local server code is working correctly")
        print("❓ Issue is likely in deployment configuration")
    else:
        print("❌ Local server code has issues")
        print("🔧 Need to fix the code before redeployment")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
