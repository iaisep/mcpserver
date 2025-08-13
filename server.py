"""
Main MCP Server implementation for Odoo integration.

This module provides the MCP server implementation that exposes
Odoo data to AI agents via the Model Context Protocol.
"""
import logging
import asyncio
from typing import Literal, Optional
import os

from mcp.server.fastmcp import Context

# Import the MCP instance defined in mcp_instance.py
from mcp_instance import mcp, AppContext

# Import all resources to ensure they are registered
from resources import partners
from resources import accounting
from resources import crm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple tool to verify connection
@mcp.tool()
async def odoo_version(ctx: Context) -> str:
    """Get the Odoo server version."""
    try:
        # Get Odoo client from the lifespan context
        # Add logging to debug the context type
        app_context = ctx.request_context.lifespan_context
        logger.info(f"Context type in odoo_version: {type(app_context)}")
        logger.info(f"Context content in odoo_version: {app_context}")

        # Handle the case when app_context is a dictionary
        if isinstance(app_context, dict):
            # Recreate AppContext if possible
            from .odoo.client import OdooClient
            from .config import config

            logger.info("Context is a dictionary, attempting to extract Odoo client...")

            # If the dictionary has an odoo_client as another dictionary, try to recreate it
            if "odoo_client" in app_context and isinstance(app_context["odoo_client"], dict):
                odoo_data = app_context["odoo_client"]
                client = OdooClient(
                    url=odoo_data.get("url"),
                    database=odoo_data.get("database"),
                    username=odoo_data.get("username"),
                    password=odoo_data.get("password")
                )
                if not client.is_connected:
                    await client.connect()
            else:
                # Create a new client using the configuration
                config_data = config.as_dict()
                odoo_config = config_data.get("odoo", {})
                client = OdooClient(
                    url=odoo_config.get("host") or odoo_config.get("url"),
                    database=odoo_config.get("database"),
                    username=odoo_config.get("username"),
                    password=odoo_config.get("password")
                )
                await client.connect()
        else:
            # Use the client directly from the AppContext
            client = app_context.odoo_client

        # Log activity
        await ctx.info("Executing odoo_version tool")

        # Check client connection status and reconnect if needed
        if not client.is_connected:
            await ctx.warning("Odoo client disconnected, reconnecting...")
            await client.connect()

        # Set a timeout for the operation
        version = await asyncio.wait_for(
            client.get_server_version(),
            timeout=5.0
        )

        return f"Connected to: {client.url}\nDatabase: {client.database}\nVersion: {version}"
    except asyncio.TimeoutError:
        logger.error("Timeout while executing odoo_version tool")
        await ctx.error("Operation timed out")
        return "Error: Connection to Odoo timed out"
    except Exception as e:
        logger.error(f"Error in odoo_version tool: {str(e)}", exc_info=True)
        await ctx.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"


def create_app(transport: str = "sse"):
    """Create and return the FastAPI application for MCP server.
    
    Args:
        transport: Transport type to use (should be 'sse' for web deployment)
        
    Returns:
        FastAPI application instance
    """
    logger.info(f"Creating FastAPI app with transport: {transport}")
    
    if transport == "sse":
        # Get the FastAPI app from the MCP instance
        app = mcp.sse_app()
        logger.info("✅ SSE app created successfully")
        
        # Try to add health check endpoint
        try:
            from starlette.responses import JSONResponse
            from starlette.routing import Route
            
            async def health_check(request):
                return JSONResponse({
                    "status": "healthy", 
                    "service": "mcp-odoo",
                    "transport": transport,
                    "tools_count": len(mcp._tools)
                })
            
            # Add health route if possible
            if hasattr(app, 'router') and hasattr(app.router, 'routes'):
                health_route = Route("/health", health_check)
                app.router.routes.append(health_route)
                logger.info("✅ Health check endpoint added")
            
        except Exception as e:
            logger.warning(f"Could not add health endpoint: {e}")
        
        return app
    else:
        raise ValueError(f"Unsupported transport for app creation: {transport}")


def run_server(transport: Literal["stdio", "sse"] = "stdio",
               host: Optional[str] = None,
               port: Optional[int] = None):
    """Run the MCP server with improved error handling and connection management.
    
    Args:
        transport: Transport type to use (stdio or sse)
        host: Host to bind to for SSE transport (overrides config)
        port: Port to bind to for SSE transport (overrides config)
    """
    # Import config here to avoid circular imports
    from config import config

    # Override config with parameters if provided
    if host is not None:
        config.server.host = host
    if port is not None:
        config.server.port = port

    # Validate configuration
    if not config.validate():
        logger.error("Invalid configuration. Check environment variables.")
        raise ValueError("Invalid configuration. Check environment variables.")
    
    # Configure SSE server environment variables if using SSE transport
    if transport == "sse":
        # Set environment variables for the FastMCP SSE server
        os.environ["MCP_HOST"] = config.server.host
        os.environ["MCP_PORT"] = str(config.server.port)

        # Also try common Uvicorn environment variables
        os.environ["UVICORN_HOST"] = config.server.host
        os.environ["UVICORN_PORT"] = str(config.server.port)

        # Log startup information
        logger.info(f"Starting MCP Odoo server on {config.server.host}:{config.server.port}")
        logger.info(f"Connected to Odoo instance: {config.odoo.url}")
        logger.info(f"Environment variables set: MCP_HOST={os.environ.get('MCP_HOST')}, MCP_PORT={os.environ.get('MCP_PORT')}")
    else:
        logger.info(f"Starting MCP Odoo server with {transport} transport")
        logger.info(f"Connected to Odoo instance: {config.odoo.url}")

    try:
        # Log initialization info
        logger.info("Starting MCP server with Odoo integration")
        logger.info(f"Using {transport} transport")

        # Run the server with the configured transport
        if transport == "sse":
            # For SSE transport, force uvicorn direct configuration to ensure proper host binding
            logger.info(f"Starting SSE server on {config.server.host}:{config.server.port}")
            
            try:
                # Force direct uvicorn configuration for reliable host binding in containers
                logger.info("Using direct uvicorn configuration for reliable host binding")
                import uvicorn

                # Get ASGI app from FastMCP instance
                mcp_app = mcp.sse_app()
                logger.info("Successfully created MCP SSE app")

                # Try to add health check route to existing MCP app
                try:
                    from starlette.responses import JSONResponse
                    from starlette.routing import Route

                    # Create a simple health check function
                    async def health_check(request):
                        return JSONResponse({"status": "healthy", "service": "mcp-odoo"})

                    # Add health route to the existing MCP app if possible
                    if hasattr(mcp_app, 'router') and hasattr(mcp_app.router, 'routes'):
                        health_route = Route("/health", health_check)
                        mcp_app.router.routes.append(health_route)
                        logger.info("Added health check route to MCP app")
                    else:
                        logger.info("Cannot add health route, using MCP app as-is")
                        
                except Exception as e:
                    logger.warning(f"Could not add health endpoint ({e}), using MCP app as-is")
                    
                # Use the MCP app directly (with or without health endpoint)
                app = mcp_app
                logger.info("Using MCP SSE app directly")

                logger.info(f"Starting uvicorn server on {config.server.host}:{config.server.port}")
                logger.info("MCP SSE endpoints available at standard paths (/sse, /messages)")
                uvicorn.run(app, host=config.server.host, port=config.server.port, log_level="info")
                
            except Exception as e:
                logger.error(f"Uvicorn/SSE failed ({e}). Trying FastMCP fallback approaches")
                    
            except Exception as main_error:
                logger.error(f"All modern transports failed ({main_error}). Trying FastMCP fallback approaches")
                try:
                    # Fallback: pass host and port directly (newer versions of FastMCP)
                    mcp.run(transport=transport, host=config.server.host, port=config.server.port)
                except TypeError as e:
                    # Final fallback: if direct parameters don't work, try with environment variables
                    logger.info(f"Direct host/port parameters not supported ({e}), trying environment variables approach")
                    mcp.run(transport=transport)
        else:
            # For stdio, no host/port needed
            mcp.run(transport=transport)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested. Cleaning up...")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise