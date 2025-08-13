#!/usr/bin/env python3
"""
Diagnose the intermittent 502 issues with our MCP server
"""

import requests
import time
from datetime import datetime
import subprocess
import sys

def check_docker_stats():
    """Check if docker is available locally (probably not on Windows)"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("🐳 Docker is available locally")
            return True
    except FileNotFoundError:
        print("🚫 Docker not available locally (expected on Windows)")
    return False

def diagnose_502_pattern():
    """Analyze the 502 pattern"""
    print("🔍 DIAGNOSING 502 BAD GATEWAY PATTERN")
    print("=" * 50)
    
    print("The pattern we're seeing:")
    print("✅ 502 responses are actually 'successful' HTTP responses")
    print("✅ This means the proxy (Traefik/Coolify) is working")
    print("❌ The backend container is intermittently unavailable")
    print()
    
    print("Possible causes:")
    print("1. 🔄 Container restarting due to memory issues")
    print("2. ⚡ High server load causing timeouts")
    print("3. 🐞 Application crashes and restarts")
    print("4. 💾 Memory limits being exceeded")
    print("5. 🔧 Coolify health check failing")
    print()
    
    # Check current memory usage from the provided stats
    print("📊 SERVER ANALYSIS (from provided docker stats):")
    print("- Server has 125.7GiB total memory")
    print("- Multiple high-memory services running:")
    print("  • 3 Supabase Kong instances (2.94-2.95GiB each) = ~9GB")
    print("  • Backend worker: 1.18GiB")  
    print("  • Jenkins: 1.11GiB")
    print("  • Odoo12: 1.02GiB")
    print("  • Our MCP service: 0.23GiB (309.1MiB)")
    print()
    print("🎯 Our service memory usage looks normal at 309MB")
    print()

def recommend_solutions():
    """Recommend solutions for the intermittent issues"""
    print("🛠️  RECOMMENDED SOLUTIONS")
    print("=" * 30)
    print()
    
    print("1. 🔧 IMMEDIATE FIXES:")
    print("   • Check Coolify logs for our application")
    print("   • Verify health check configuration")  
    print("   • Consider increasing health check timeout")
    print()
    
    print("2. 🚀 PERFORMANCE OPTIMIZATIONS:")
    print("   • Add resource limits to prevent memory spikes")
    print("   • Implement graceful shutdown handling")
    print("   • Add application-level health monitoring")
    print()
    
    print("3. 📋 MONITORING IMPROVEMENTS:")
    print("   • Add structured logging")
    print("   • Monitor response times")
    print("   • Track restart patterns")
    print()

def check_current_status():
    """Check current status of our service"""
    print("🩺 CURRENT SERVICE STATUS")
    print("=" * 25)
    
    url = "https://dev2.odoo.universidadisep.com/health"
    
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            status_icon = "✅" if response.status_code == 200 else "❌" 
            print(f"{status_icon} Check {i+1}: {response.status_code} ({response_time:.0f}ms)")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'status' in data:
                        print(f"    Status: {data['status']}")
                except:
                    pass
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Check {i+1}: ERROR - {str(e)}")
        
        if i < 4:
            time.sleep(2)
    print()

if __name__ == "__main__":
    print(f"🕒 Diagnosis started at {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    check_current_status()
    diagnose_502_pattern()
    recommend_solutions()
    
    print("💡 NEXT STEPS:")
    print("1. Check Coolify application logs")
    print("2. Verify health check settings")
    print("3. Consider adding resource limits") 
    print("4. Monitor for a few more minutes to confirm pattern")
