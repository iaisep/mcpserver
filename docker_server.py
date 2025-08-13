#!/usr/bin/env python3
"""
Simplified server entry point for Docker deployment
This forces the correct host binding for containerized environments
"""
import logging
import os
import sys

# Force environment variables for container deployment
os.environ["HOST"] = "0.0.0.0"
os.environ["PORT"] = "8000"
os.environ["UVICORN_HOST"] = "0.0.0.0"
os.environ["UVICORN_PORT"] = "8000"
os.environ["MCP_HOST"] = "0.0.0.0"
os.environ["MCP_PORT"] = "8000"

# Configure logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for Docker deployment"""
    logger.info("Starting MCP-Odoo server for Docker deployment...")
    logger.info("Forced environment variables:")
    logger.info(f"  HOST: {os.environ.get('HOST')}")
    logger.info(f"  PORT: {os.environ.get('PORT')}")
    logger.info(f"  UVICORN_HOST: {os.environ.get('UVICORN_HOST')}")
    logger.info(f"  UVICORN_PORT: {os.environ.get('UVICORN_PORT')}")
    
    try:
        # Import after setting environment variables
        from config import config
        from server import run_server
        
        # Validate configuration
        if not config.validate():
            logger.error("Invalid configuration. Check environment variables.")
            sys.exit(1)
            
        logger.info(f"Starting server on {config.server.host}:{config.server.port}")
        logger.info(f"Odoo URL: {config.odoo.url}")
        logger.info("SSE endpoints will be available at:")
        logger.info(f"  - Health: http://0.0.0.0:8000/health")
        logger.info(f"  - SSE: http://0.0.0.0:8000/sse")
        logger.info(f"  - Messages: http://0.0.0.0:8000/messages")
        
        # Run with forced parameters
        run_server(transport="sse", host="0.0.0.0", port=8000)
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
