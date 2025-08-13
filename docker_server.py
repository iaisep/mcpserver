#!/usr/bin/env python3
"""
Robust Docker server entry point with retry logic and better error handling
"""
import logging
import os
import sys
import time

# Force environment variables for container deployment
os.environ["HOST"] = "0.0.0.0"
os.environ["PORT"] = "8082"
os.environ["UVICORN_HOST"] = "0.0.0.0"
os.environ["UVICORN_PORT"] = "8082"
os.environ["MCP_HOST"] = "0.0.0.0"
os.environ["MCP_PORT"] = "8082"

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_with_retry_logic(max_retries=3, retry_delay=10):
    """Run server with retry logic for improved stability"""
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🚀 Starting server (attempt {attempt + 1}/{max_retries})")
            
            # Import after setting environment variables
            from config import config
            from server import create_app
            import uvicorn
            
            # Validate configuration
            if not config.validate():
                logger.error("❌ Invalid configuration. Check environment variables.")
                sys.exit(1)
            
            logger.info(f"✅ Config validated - Odoo: {config.odoo.url}, Port: {config.server.port}")
            
            # Create the FastAPI app with robust error handling
            app = create_app(transport="sse")
            logger.info("✅ FastAPI application created")
            
            # Configure uvicorn for container stability
            uvicorn_config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8082,
                log_level="info",
                access_log=True,
                # Improved settings for container stability
                timeout_keep_alive=30,
                limit_max_requests=200,
                timeout_graceful_shutdown=15,
                server_header=False,
                date_header=False,
            )
            
            server = uvicorn.Server(uvicorn_config)
            logger.info("🌐 Starting uvicorn server...")
            logger.info("📡 Endpoints available:")
            logger.info("   - Health: http://0.0.0.0:8082/health")
            logger.info("   - SSE: http://0.0.0.0:8082/sse")
            logger.info("   - Messages: http://0.0.0.0:8082/messages")
            
            # This will block until server stops
            server.run()
            
            # If we get here, server stopped normally
            logger.info("✅ Server stopped normally")
            break
            
        except KeyboardInterrupt:
            logger.info("⏹️  Server stopped by signal")
            break
        except ImportError as e:
            logger.error(f"🚫 Import error: {e}")
            logger.error("Dependencies missing - cannot retry")
            sys.exit(1)
        except Exception as e:
            logger.error(f"💥 Server error (attempt {attempt + 1}): {e}")
            logger.exception("Full error details:")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                logger.error("🚨 Max retries exceeded - exiting")
                sys.exit(1)

def main():
    """Main entry point for Docker deployment"""
    logger.info("🐳 Starting robust MCP-Odoo server for Docker deployment...")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"🔗 Process ID: {os.getpid()}")
    
    logger.info("🔧 Environment variables:")
    env_vars = ['HOST', 'PORT', 'ODOO_URL', 'ODOO_DB', 'ODOO_USERNAME']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        logger.info(f"   {var}={value}")
    
    # Run with retry logic for improved stability
    run_with_retry_logic(max_retries=3, retry_delay=10)

if __name__ == "__main__":
    main()
