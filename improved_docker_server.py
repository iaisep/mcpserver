#!/usr/bin/env python3
"""
Improved Docker server with better error handling and monitoring
"""

import os
import sys
import logging
import signal
import uvicorn
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from server import create_app

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/mcp-server.log', mode='a') if os.path.exists('/tmp') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

def setup_signal_handlers():
    """Setup graceful shutdown handlers"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

def run_server(transport: str = "sse", host: str = "0.0.0.0", port: int = 8082):
    """Run the MCP server with improved error handling"""
    
    logger.info("🚀 Starting improved MCP-Odoo server...")
    logger.info(f"📋 Configuration: transport={transport}, host={host}, port={port}")
    
    # Set environment variables for consistent configuration
    os.environ["PORT"] = str(port)
    os.environ["HOST"] = host
    os.environ["TRANSPORT"] = transport
    
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()
    
    try:
        # Create the FastAPI app
        logger.info("🔧 Creating FastAPI application...")
        app = create_app(transport=transport)
        
        # Log server startup
        logger.info("✅ Application created successfully")
        logger.info(f"🌐 Server will be available at: http://{host}:{port}")
        logger.info(f"🔗 Health check: http://{host}:{port}/health")
        logger.info(f"📡 SSE endpoint: http://{host}:{port}/sse")
        
        # Start the server with improved configuration
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            server_header=False,
            date_header=False,
            # Improved configuration for stability
            timeout_keep_alive=5,
            limit_max_requests=1000,
            # Graceful shutdown timeout
            timeout_graceful_shutdown=10,
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️  Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server startup failed: {str(e)}")
        logger.exception("Full error details:")
        sys.exit(1)

if __name__ == "__main__":
    # Force configuration for Docker environment
    logger.info("🐳 Docker server starting...")
    
    # Log environment information
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"🌍 Environment variables:")
    for key in ['PORT', 'HOST', 'TRANSPORT', 'ODOO_URL', 'ODOO_DB', 'ODOO_USERNAME']:
        value = os.environ.get(key, 'Not set')
        logger.info(f"   {key}={value}")
    
    try:
        run_server(transport="sse", host="0.0.0.0", port=8082)
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
        sys.exit(1)
