#!/usr/bin/env python3
"""
Test HTTP instead of HTTPS to bypass SSL issues
"""
import requests
import time
from datetime import datetime

# Try HTTP instead of HTTPS
BASE_URL_HTTP = "http://dev2.odoo.universidadisep.com"
BASE_URL_HTTPS = "https://dev2.odoo.universidadisep.com"

def test_both_protocols():
    """Test both HTTP and HTTPS to isolate SSL issues"""
    print("🔍 TESTING BOTH HTTP AND HTTPS PROTOCOLS")
    print("=" * 50)
    print(f"⏰ Test time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    protocols = [
        ("HTTP", BASE_URL_HTTP),
        ("HTTPS", BASE_URL_HTTPS)
    ]
    
    for protocol_name, base_url in protocols:
        print(f"🌐 Testing {protocol_name}: {base_url}")
        
        endpoints = [
            ("Health", f"{base_url}/health"),
            ("SSE", f"{base_url}/sse"),
            ("Root", base_url)
        ]
        
        for endpoint_name, url in endpoints:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10, allow_redirects=True)
                response_time = (time.time() - start_time) * 1000
                
                status_icon = "✅" if response.status_code in [200, 404] else "❌"
                print(f"  {status_icon} {endpoint_name}: {response.status_code} ({response_time:.0f}ms)")
                
                # Show response for successful health checks
                if endpoint_name == "Health" and response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"    📋 Status: {data.get('status', 'unknown')}")
                        print(f"    🛠️  Service: {data.get('service', 'unknown')}")
                        print(f"    🔧 Tools: {data.get('tools_count', 'unknown')}")
                    except:
                        print(f"    📋 Raw response: {response.text[:100]}...")
                        
            except requests.exceptions.SSLError as e:
                print(f"  🔒 {endpoint_name}: SSL ERROR - {str(e)}")
            except requests.exceptions.ConnectionError as e:
                print(f"  🔌 {endpoint_name}: CONNECTION ERROR - {str(e)}")
            except requests.exceptions.Timeout:
                print(f"  ⏰ {endpoint_name}: TIMEOUT")
            except Exception as e:
                print(f"  ❌ {endpoint_name}: ERROR - {str(e)}")
        
        print()
    
    print("💡 ANALYSIS:")
    print("- If HTTP works but HTTPS fails → SSL certificate issue")
    print("- If both fail with 502 → Application/routing issue") 
    print("- If both fail with connection errors → DNS/network issue")
    print("- If HTTP redirects to HTTPS → Check HTTPS response")

if __name__ == "__main__":
    test_both_protocols()
