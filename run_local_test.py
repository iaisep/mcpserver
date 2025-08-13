#!/usr/bin/env python3
"""
Local server test to verify MCP functionality
"""
import asyncio
import uvicorn
import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_local_test():
    """Run a local test of the MCP server"""
    try:
        from mcp_instance import mcp
        from config import config
        
        logger.info("Creating SSE app...")
        app = mcp.sse_app()
        
        # Add a simple health check
        from starlette.responses import JSONResponse
        from starlette.routing import Route
        
        async def health_check(request):
            return JSONResponse({
                "status": "healthy", 
                "service": "mcp-odoo-local-test",
                "tools_count": len(mcp._tools) if hasattr(mcp, '_tools') else 0
            })
        
        # Try to add health route
        if hasattr(app, 'router') and hasattr(app.router, 'routes'):
            health_route = Route("/health", health_check)
            app.router.routes.append(health_route)
            logger.info("Added health check route")
        
        logger.info("Starting local server on localhost:8002")
        logger.info("Health check: http://localhost:8002/health")
        logger.info("SSE endpoint: http://localhost:8002/sse")
        logger.info("Messages endpoint: http://localhost:8002/messages")
        logger.info("Press Ctrl+C to stop")
        
        # Run server
        config_obj = uvicorn.Config(
            app,
            host="localhost",
            port=8002,
            log_level="info"
        )
        server = uvicorn.Server(config_obj)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_local_test())
