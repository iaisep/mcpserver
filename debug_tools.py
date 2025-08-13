#!/usr/bin/env python3
"""
Test to debug tool loading
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio

async def debug_tool_loading():
    print("🔧 Debugging tool loading...")
    
    try:
        # Import resources to ensure tools are registered  
        from resources import partners
        from resources import accounting
        from resources import crm
        
        from mcp_instance import mcp
        print(f"✅ MCP instance loaded: {type(mcp)}")
        
        # Try list_tools method (async)
        tools = await mcp.list_tools()
        print(f"✅ Found {len(tools)} tools via list_tools()")
        for i, tool in enumerate(tools[:10]):
            print(f"   {i+1}. {tool.name} - {tool.description[:50]}...")
            
        if len(tools) > 10:
            print(f"   ... and {len(tools) - 10} more tools")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_tool_loading())
