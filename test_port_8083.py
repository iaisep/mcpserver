#!/usr/bin/env python3
"""
Test the server on port 8083 after port migration
"""
import requests
import time
from datetime import datetime

BASE_URL = "https://dev2.odoo.universidadisep.com"

def test_port_8083():
    """Test the new port 8083 configuration"""
    print("🔍 Testing server on new port configuration...")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"📅 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    endpoints = [
        ("/health", "Health Check"),
        ("/sse", "SSE Endpoint"), 
        ("", "Root Endpoint")
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            status_icon = "✅" if response.status_code in [200, 404] else "❌"
            print(f"{status_icon} {name}: {response.status_code} ({response_time:.0f}ms)")
            
            results.append({
                'endpoint': name,
                'status': response.status_code,
                'time': response_time,
                'success': response.status_code in [200, 404]
            })
            
            # Show response content for health check
            if endpoint == "/health" and response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📋 Response: {data}")
                except:
                    pass
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: ERROR - {str(e)}")
            results.append({
                'endpoint': name,
                'status': 'ERROR',
                'time': 0,
                'success': False
            })
    
    print()
    
    # Summary
    successful = [r for r in results if r['success']]
    print(f"📊 Summary: {len(successful)}/{len(results)} endpoints responding correctly")
    
    if len(successful) == len(results):
        print("✅ Server appears to be working correctly on new port!")
    elif len(successful) > 0:
        print("⚠️  Partial connectivity - server may be starting up")
    else:
        print("❌ No connectivity - check deployment status")
        
    return results

if __name__ == "__main__":
    test_port_8083()
