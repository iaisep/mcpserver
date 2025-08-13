"""
Robust server wrapper with retry logic and better error handling
"""
import time
import sys
import logging
import os
from contextlib import contextmanager
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class ServerManager:
    """Manages server lifecycle with retry logic"""
    
    def __init__(self, max_retries: int = 5, retry_delay: int = 5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.restart_count = 0
    
    @contextmanager
    def error_handling(self):
        """Context manager for error handling"""
        try:
            yield
        except KeyboardInterrupt:
            logger.info("⏹️  Server stopped by user")
            sys.exit(0)
        except ImportError as e:
            logger.error(f"🚫 Import error: {e}")
            logger.error("This usually means dependencies are missing")
            sys.exit(1)
        except ConnectionError as e:
            logger.error(f"🔌 Connection error: {e}")
            raise  # Let retry logic handle this
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
            logger.exception("Full traceback:")
            raise  # Let retry logic handle this
    
    def start_server_with_retry(self):
        """Start server with retry logic"""
        
        while self.restart_count < self.max_retries:
            try:
                with self.error_handling():
                    logger.info(f"🚀 Starting server (attempt {self.restart_count + 1}/{self.max_retries})")
                    
                    # Import and create app inside the try block to catch import errors
                    from server import create_app
                    
                    logger.info("📦 Dependencies loaded successfully")
                    
                    # Create the FastAPI app
                    app = create_app(transport="sse")
                    logger.info("✅ Application created successfully")
                    
                    # Start with uvicorn
                    import uvicorn
                    
                    config = uvicorn.Config(
                        app,
                        host="0.0.0.0",
                        port=8082,
                        log_level="info",
                        access_log=True,
                        # Add configuration for stability
                        timeout_keep_alive=30,
                        limit_max_requests=100,
                        timeout_graceful_shutdown=10,
                    )
                    
                    server = uvicorn.Server(config)
                    logger.info("🌐 Server configured, starting...")
                    
                    # This will block until server stops
                    server.run()
                    
                    # If we get here, server stopped normally
                    logger.info("✅ Server stopped normally")
                    break
                    
            except Exception as e:
                self.restart_count += 1
                logger.error(f"❌ Server crashed (attempt {self.restart_count}/{self.max_retries}): {e}")
                
                if self.restart_count >= self.max_retries:
                    logger.error("🚨 Max retries exceeded, giving up")
                    sys.exit(1)
                
                logger.info(f"⏳ Waiting {self.retry_delay} seconds before retry...")
                time.sleep(self.retry_delay)
        
        logger.info("🏁 Server manager exiting")

def main():
    """Main entry point"""
    logger.info("🔧 MCP-Odoo Robust Server Manager")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info(f"📁 Working dir: {os.getcwd()}")
    logger.info(f"🔗 PID: {os.getpid()}")
    
    # Log key environment variables
    env_vars = ['PORT', 'HOST', 'ODOO_URL', 'ODOO_DB', 'ODOO_USERNAME']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        # Don't log passwords
        if 'PASSWORD' not in var.upper():
            logger.info(f"   {var}={value}")
    
    # Start server manager
    manager = ServerManager(max_retries=3, retry_delay=10)
    manager.start_server_with_retry()

if __name__ == "__main__":
    main()
