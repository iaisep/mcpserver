#!/usr/bin/env python3
"""
Monitor deployment progress and port migration
"""
import requests
import time
from datetime import datetime
import asyncio

BASE_URL = "https://dev2.odoo.universidadisep.com"

def check_deployment_status():
    """Check if the new deployment is ready"""
    print(f"🔍 Checking deployment status at {datetime.now().strftime('%H:%M:%S')}")
    
    # Test both old and new configurations
    endpoints_to_test = [
        ("/health", "Health Check"),
        ("/sse", "SSE Endpoint")
    ]
    
    for endpoint, name in endpoints_to_test:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            status_icon = "✅" if response.status_code == 200 else "⚠️" if response.status_code == 502 else "❌"
            print(f"  {status_icon} {name}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    if endpoint == "/health":
                        data = response.json()
                        if 'service' in data:
                            print(f"     Service: {data.get('service')}")
                        if 'tools_count' in data:
                            print(f"     Tools loaded: {data.get('tools_count')}")
                except:
                    pass
                    
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {name}: {str(e)}")
    
    print()

def wait_for_deployment(max_wait_minutes=10):
    """Wait for deployment to complete"""
    print(f"⏳ Waiting for Coolify to redeploy with port 8083...")
    print(f"🕒 Will monitor for up to {max_wait_minutes} minutes")
    print(f"📅 Started at {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    check_interval = 20  # seconds
    
    healthy_checks = 0
    required_healthy_checks = 3  # Need 3 consecutive healthy checks
    
    while time.time() - start_time < max_wait_seconds:
        check_deployment_status()
        
        # Check if service is healthy
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                healthy_checks += 1
                print(f"✅ Healthy check {healthy_checks}/{required_healthy_checks}")
                
                if healthy_checks >= required_healthy_checks:
                    print("🎉 Deployment appears stable!")
                    return True
            else:
                healthy_checks = 0  # Reset counter on failure
                print(f"⚠️  Status {response.status_code} - waiting...")
        except:
            healthy_checks = 0  # Reset counter on error
            print("⚠️  Connection failed - still deploying...")
        
        print(f"⏳ Waiting {check_interval} seconds before next check...")
        time.sleep(check_interval)
        print("-" * 50)
    
    print("⏰ Max wait time reached")
    return False

if __name__ == "__main__":
    print("🚀 Deployment Monitor for Port 8083 Migration")
    print("=" * 50)
    
    success = wait_for_deployment(max_wait_minutes=8)
    
    if success:
        print("\n✅ DEPLOYMENT SUCCESS!")
        print("🔗 Server is ready for n8n integration")
        print(f"📡 URL: {BASE_URL}")
        print("🛠️  Transport: SSE")
    else:
        print("\n⚠️  DEPLOYMENT STATUS UNCLEAR")
        print("🔍 Check Coolify logs for details")
        print("🕒 Manual verification may be needed")
