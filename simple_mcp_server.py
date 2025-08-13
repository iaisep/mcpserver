#!/usr/bin/env python3
"""
Simple MCP server without FastMCP SSE - direct HTTP implementation
This should work better with proxies like Traefik
"""
import logging
import os
import sys
import json
import asyncio
from datetime import datetime
from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Force environment variables for container deployment
os.environ["HOST"] = "0.0.0.0" 
os.environ["PORT"] = "8082"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    """Simple MCP server implementation"""
    
    def __init__(self):
        self.tools = {}
        self.initialized = False
        # Don't load tools in __init__, do it async later
    
    async def _load_tools_async(self):
        """Load MCP tools from the FastMCP instance (async)"""
        try:
            # Import resources to ensure tools are registered
            from resources import partners
            from resources import accounting  
            from resources import crm
            
            from mcp_instance import mcp
            
            # Use FastMCP's list_tools method (async)
            tools_info = await mcp.list_tools()
            
            logger.info(f"FastMCP tools found: {len(tools_info)}")
            
            for tool in tools_info:
                tool_name = tool.name
                if tool_name:
                    self.tools[tool_name] = {
                        "info": {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        },
                        "mcp_instance": mcp  # Store reference to MCP instance
                    }
                    
            logger.info(f"Loaded {len(self.tools)} MCP tools")
                
        except Exception as e:
            logger.error(f"Error loading tools: {e}")
            import traceback
            traceback.print_exc()
    
    async def handle_initialize(self, params):
        """Handle MCP initialize request"""
        # Load tools on first initialize
        if not self.tools:
            await self._load_tools_async()
            
        self.initialized = True
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"listChanged": False}
            },
            "serverInfo": {
                "name": "mcp-odoo-simple",
                "version": "1.0.0"
            }
        }
    
    async def handle_tools_list(self, params):
        """Handle tools/list request"""
        return {
            "tools": [tool_data["info"] for tool_data in self.tools.values()]
        }
    
    async def handle_tools_call(self, params):
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise Exception(f"Unknown tool: {tool_name}")
        
        try:
            # Use FastMCP's call_tool method
            mcp_instance = self.tools[tool_name]["mcp_instance"]
            result = await mcp_instance.call_tool(tool_name, arguments)
            return result
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            raise Exception(f"Tool execution failed: {str(e)}")

# Global MCP server instance
mcp_server = SimpleMCPServer()

async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "mcp-odoo-simple",
        "timestamp": datetime.now().isoformat(),
        "tools_loaded": len(mcp_server.tools),
        "initialized": mcp_server.initialized
    })

async def handle_mcp_request(request):
    """Handle MCP JSON-RPC requests"""
    try:
        # Parse JSON-RPC request
        body = await request.body()
        data = json.loads(body)
        
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")
        
        logger.info(f"MCP request: {method}")
        
        # Handle different MCP methods
        if method == "initialize":
            result = await mcp_server.handle_initialize(params)
        elif method == "tools/list":
            result = await mcp_server.handle_tools_list(params)
        elif method == "tools/call":
            result = await mcp_server.handle_tools_call(params)
        else:
            raise Exception(f"Unknown method: {method}")
        
        # Return JSON-RPC response
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        logger.error(f"MCP request error: {e}")
        
        # Return JSON-RPC error response
        error_response = {
            "jsonrpc": "2.0", 
            "id": data.get("id") if 'data' in locals() else None,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }
        
        return JSONResponse(error_response, status_code=400)

async def sse_endpoint(request):
    """Simple SSE endpoint that just provides connection info"""
    
    # Generate a simple session ID
    import uuid
    session_id = str(uuid.uuid4()).replace('-', '')
    
    async def generate_sse_data():
        # Send initial connection info
        yield f"event: endpoint\n"
        yield f"data: /messages\n\n"
        
        yield f"event: session\n" 
        yield f"data: {session_id}\n\n"
        
        yield f"event: ready\n"
        yield f"data: MCP server ready\n\n"
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
            yield f"event: heartbeat\n"
            yield f"data: {datetime.now().isoformat()}\n\n"
    
    headers = {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
        'Access-Control-Allow-Origin': '*'
    }
    
    return Response(generate_sse_data(), media_type='text/event-stream', headers=headers)

def create_app():
    """Create the Starlette application"""
    
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    
    routes = [
        Route("/health", health_check, methods=["GET"]),
        Route("/sse", sse_endpoint, methods=["GET"]),
        Route("/messages", handle_mcp_request, methods=["POST"]),
    ]
    
    return Starlette(routes=routes, middleware=middleware)

def main():
    """Main entry point"""
    logger.info("Starting Simple MCP-Odoo server...")
    
    try:
        from config import config
        
        if not config.validate():
            logger.error("Invalid configuration")
            sys.exit(1)
            
        logger.info(f"Server starting on {config.server.host}:{config.server.port}")
        logger.info(f"Tools available: {len(mcp_server.tools)}")
        logger.info("Endpoints:")
        logger.info("  - Health: /health")
        logger.info("  - SSE: /sse") 
        logger.info("  - Messages: /messages")
        
        app = create_app()
        
        import uvicorn
        uvicorn.run(
            app,
            host=config.server.host,
            port=config.server.port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
