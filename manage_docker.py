#!/usr/bin/env python3
"""
Docker Compose manager for MCP-Odoo server
"""
import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def build_and_start():
    """Build and start the Docker Compose stack"""
    print("🐳 Building and starting MCP-Odoo with Docker Compose...")
    
    # Build and start
    success, stdout, stderr = run_command("docker-compose --env-file .env.docker-compose up --build -d")
    
    if success:
        print("✅ Container started successfully!")
        print("📋 Container status:")
        run_command("docker-compose ps")
        return True
    else:
        print(f"❌ Failed to start: {stderr}")
        return False

def stop():
    """Stop the Docker Compose stack"""
    print("⏹️  Stopping MCP-Odoo container...")
    success, stdout, stderr = run_command("docker-compose down")
    
    if success:
        print("✅ Container stopped successfully!")
    else:
        print(f"❌ Failed to stop: {stderr}")

def restart():
    """Restart the Docker Compose stack"""
    print("🔄 Restarting MCP-Odoo container...")
    stop()
    time.sleep(2)
    return build_and_start()

def logs():
    """Show container logs"""
    print("📋 Container logs:")
    run_command("docker-compose logs -f --tail=50 mcp-odoo")

def status():
    """Show container status"""
    print("📊 Container status:")
    run_command("docker-compose ps")
    
    # Try to check health
    try:
        response = requests.get("http://localhost:8083/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data.get('status', 'unknown')}")
            print(f"🛠️  Service: {data.get('service', 'unknown')}")
            print(f"🔧 Tools: {data.get('tools_count', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def change_port(new_port):
    """Change the external port"""
    print(f"🔧 Changing external port to {new_port}...")
    
    # Read docker-compose.yml
    compose_file = Path("docker-compose.yml")
    if not compose_file.exists():
        print("❌ docker-compose.yml not found!")
        return False
    
    content = compose_file.read_text()
    
    # Replace port mapping (simple string replacement)
    import re
    content = re.sub(r'- "\d+:8083"', f'- "{new_port}:8083"', content)
    
    # Write back
    compose_file.write_text(content)
    
    print(f"✅ Port changed to {new_port}. Run 'restart' to apply changes.")
    return True

def test_connection():
    """Test connection to the server"""
    print("🧪 Testing connection...")
    
    endpoints = [
        ("Health", "http://localhost:8083/health"),
        ("SSE", "http://localhost:8083/sse"),
        ("Root", "http://localhost:8083/")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            status_icon = "✅" if response.status_code in [200, 404] else "❌"
            print(f"{status_icon} {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("""
🐳 MCP-Odoo Docker Compose Manager

Commands:
  start     - Build and start the container
  stop      - Stop the container  
  restart   - Restart the container
  logs      - Show container logs
  status    - Show container status and health
  port PORT - Change external port (e.g., port 8084)
  test      - Test connection to the server
  
Examples:
  python manage_docker.py start
  python manage_docker.py port 8084
  python manage_docker.py restart
  python manage_docker.py test
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        build_and_start()
    elif command == "stop":
        stop()
    elif command == "restart":
        restart()
    elif command == "logs":
        logs()
    elif command == "status":
        status()
    elif command == "test":
        test_connection()
    elif command == "port" and len(sys.argv) >= 3:
        port = sys.argv[2]
        change_port(port)
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
