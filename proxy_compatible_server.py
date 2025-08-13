#!/usr/bin/env python3
"""
Alternative server configuration for better proxy compatibility
Adds specific headers and configurations for SSE through proxies
"""
import logging
import os
import sys
from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Force environment variables for container deployment
os.environ["HOST"] = "0.0.0.0"
os.environ["PORT"] = "8000"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy", 
        "service": "mcp-odoo-proxy-compatible",
        "timestamp": "2025-08-13",
        "proxy_headers": {
            "connection": "keep-alive",
            "cache_control": "no-cache"
        }
    })

async def sse_endpoint_with_proxy_headers(request):
    """SSE endpoint with proxy-friendly headers"""
    
    async def generate_sse():
        # Import here to ensure environment variables are set
        from mcp_instance import mcp
        from config import config
        
        # Create the FastMCP SSE app
        fastmcp_app = mcp.sse_app()
        
        # Forward the request to FastMCP but with enhanced headers
        # This is a workaround to add proxy-friendly headers
        
        # Create a new ASGI scope for the FastMCP app
        scope = request.scope.copy()
        
        # Add proxy-friendly headers to the scope
        headers = dict(scope.get('headers', []))
        headers[b'connection'] = b'keep-alive'
        headers[b'cache-control'] = b'no-cache, no-store, must-revalidate'
        headers[b'x-accel-buffering'] = b'no'  # Nginx specific
        
        scope['headers'] = [(k.encode() if isinstance(k, str) else k, 
                           v.encode() if isinstance(v, str) else v) 
                          for k, v in headers.items()]
        
        # Create a simple receive/send pair for ASGI
        receive_queue = []
        send_queue = []
        
        async def receive():
            return {"type": "http.request", "body": b""}
        
        responses = []
        async def send(message):
            responses.append(message)
        
        # Call the FastMCP app
        await fastmcp_app(scope, receive, send)
        
        # Extract the response
        for response_part in responses:
            if response_part["type"] == "http.response.start":
                # This contains the headers and status
                pass
            elif response_part["type"] == "http.response.body":
                body = response_part.get("body", b"")
                if body:
                    yield body
    
    # Return SSE response with proxy-friendly headers
    headers = {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',  # Disable Nginx buffering
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    return Response(generate_sse(), media_type='text/event-stream', headers=headers)

async def messages_endpoint(request):
    """Messages endpoint with proxy compatibility"""
    
    # Import here to ensure environment variables are set
    from mcp_instance import mcp
    
    # Get the FastMCP app and forward the request
    fastmcp_app = mcp.sse_app()
    
    # Create ASGI environment for the request
    scope = request.scope.copy()
    
    responses = []
    async def send(message):
        responses.append(message)
    
    # Read the request body
    body = await request.body()
    
    async def receive():
        return {
            "type": "http.request",
            "body": body,
            "more_body": False
        }
    
    # Forward to FastMCP
    await fastmcp_app(scope, receive, send)
    
    # Process the response
    status = 200
    headers = {}
    response_body = b""
    
    for response_part in responses:
        if response_part["type"] == "http.response.start":
            status = response_part["status"]
            headers = {k.decode(): v.decode() for k, v in response_part.get("headers", [])}
        elif response_part["type"] == "http.response.body":
            response_body += response_part.get("body", b"")
    
    # Add proxy-friendly headers
    headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    })
    
    return Response(response_body, status_code=status, headers=headers)

def create_proxy_compatible_app():
    """Create Starlette app with proxy-compatible configuration"""
    
    # Add CORS middleware for better proxy compatibility
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
        Route("/sse", sse_endpoint_with_proxy_headers, methods=["GET"]),
        Route("/messages", messages_endpoint, methods=["POST"]),
        Route("/messages/", messages_endpoint, methods=["POST"]),  # Handle trailing slash
    ]
    
    return Starlette(routes=routes, middleware=middleware)

def main():
    """Main entry point with proxy compatibility"""
    logger.info("Starting MCP-Odoo server with proxy compatibility...")
    
    try:
        # Import after setting environment variables
        from config import config
        
        # Validate configuration
        if not config.validate():
            logger.error("Invalid configuration. Check environment variables.")
            sys.exit(1)
            
        logger.info(f"Starting proxy-compatible server on {config.server.host}:{config.server.port}")
        logger.info("Enhanced for Traefik/Nginx proxy compatibility")
        logger.info("Available endpoints:")
        logger.info(f"  - Health: http://0.0.0.0:8000/health")
        logger.info(f"  - SSE: http://0.0.0.0:8000/sse") 
        logger.info(f"  - Messages: http://0.0.0.0:8000/messages")
        
        # Create proxy-compatible app
        app = create_proxy_compatible_app()
        
        # Use uvicorn with proxy-optimized settings
        import uvicorn
        uvicorn.run(
            app,
            host=config.server.host,
            port=config.server.port,
            log_level="info",
            access_log=True,
            # Proxy-friendly uvicorn settings
            timeout_keep_alive=120,  # Keep connections alive longer
            timeout_graceful_shutdown=30,
            limit_concurrency=1000,
            backlog=2048
        )
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
