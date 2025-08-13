#!/usr/bin/env python3
"""
Diagnostic script for MCP server connectivity issues
"""
import asyncio
import aiohttp
import socket
import subprocess
import platform

async def test_domain_resolution():
    """Test if the domain resolves correctly"""
    print("🌐 Testing domain resolution...")
    domain = "dev2.odoo.universidadisep.com"
    
    try:
        # Get IP address
        ip = socket.gethostbyname(domain)
        print(f"✅ {domain} resolves to: {ip}")
        
        # Test if we can connect to port 443 (HTTPS)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, 443))
        if result == 0:
            print(f"✅ Port 443 is open on {ip}")
        else:
            print(f"❌ Port 443 is closed on {ip}")
        sock.close()
        
        # Test if we can connect to port 80 (HTTP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, 80))
        if result == 0:
            print(f"✅ Port 80 is open on {ip}")
        else:
            print(f"❌ Port 80 is closed on {ip}")
        sock.close()
        
        return True
    except Exception as e:
        print(f"❌ Domain resolution failed: {e}")
        return False

async def test_http_headers():
    """Test HTTP headers and responses"""
    print("\n🔍 Testing HTTP headers...")
    url = "https://dev2.odoo.universidadisep.com"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test root path
            async with session.get(url, timeout=10) as response:
                print(f"Root URL ({url}) status: {response.status}")
                print(f"Server header: {response.headers.get('server', 'Not set')}")
                print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
                
                # Check for Traefik headers
                if 'traefik' in str(response.headers).lower():
                    print("✅ Traefik detected in headers")
                else:
                    print("❓ No Traefik headers detected")
                    
            # Test with explicit paths
            test_paths = ["/health", "/sse", "/messages", "/robots.txt", "/favicon.ico"]
            for path in test_paths:
                try:
                    async with session.get(f"{url}{path}", timeout=5) as response:
                        print(f"Path {path}: {response.status}")
                        if response.status not in [404, 502, 503]:
                            content_type = response.headers.get('content-type', '')
                            print(f"  Content-Type: {content_type}")
                except Exception as e:
                    print(f"Path {path}: Error - {e}")
                    
    except Exception as e:
        print(f"❌ HTTP headers test failed: {e}")

async def test_ssl_certificate():
    """Test SSL certificate"""
    print("\n🔒 Testing SSL certificate...")
    try:
        import ssl
        import certifi
        
        context = ssl.create_default_context(cafile=certifi.where())
        
        with socket.create_connection(("dev2.odoo.universidadisep.com", 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="dev2.odoo.universidadisep.com") as ssock:
                cert = ssock.getpeercert()
                print(f"✅ SSL certificate is valid")
                print(f"Subject: {cert.get('subject')}")
                print(f"Issuer: {cert.get('issuer')}")
                print(f"Expires: {cert.get('notAfter')}")
                
    except Exception as e:
        print(f"❌ SSL test failed: {e}")

async def test_dns_alternative():
    """Test with alternative DNS servers"""
    print("\n🔧 Testing alternative DNS...")
    try:
        # Try with Google's DNS
        if platform.system() == "Windows":
            result = subprocess.run(
                ["nslookup", "dev2.odoo.universidadisep.com", "8.8.8.8"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✅ Google DNS resolves the domain")
                print(f"Output: {result.stdout[:200]}...")
            else:
                print(f"❌ Google DNS failed: {result.stderr}")
    except Exception as e:
        print(f"❌ DNS test failed: {e}")

async def main():
    """Main diagnostic function"""
    print("=" * 70)
    print("🩺 MCP SERVER CONNECTIVITY DIAGNOSIS")
    print("=" * 70)
    
    await test_domain_resolution()
    await test_http_headers()
    await test_ssl_certificate()
    await test_dns_alternative()
    
    print("\n" + "=" * 70)
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 70)
    print("If all tests above passed but you still get 502 errors:")
    print("1. The container may not be running")
    print("2. The container may not be binding to 0.0.0.0:8000")
    print("3. Coolify/Traefik may not have deployed the latest version")
    print("4. Check Coolify deployment logs for errors")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
