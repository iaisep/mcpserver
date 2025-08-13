#!/usr/bin/env python3
"""
Health check script for port 8082
"""
import asyncio
import aiohttp

async def health_check_8082():
    """Simple health check for port 8082"""
    
    # Note: We need to update Coolify to point to port 8082
    # For now, test what port the server will actually use
    print("🔍 Testing different port configurations...")
    
    urls_to_test = [
        ("Current (8000)", "https://dev2.odoo.universidadisep.com"),
        ("New (8082)", "https://dev2.odoo.universidadisep.com:8082"), 
    ]
    
    print("🩺 Port configuration health check...")
    
    for name, base_url in urls_to_test:
        print(f"\n{name}:")
        test_paths = [
            ("Root", ""),
            ("Health", "/health"),
            ("SSE", "/sse")
        ]
        
        for path_name, path in test_paths:
            url = f"{base_url}{path}"
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as response:
                        print(f"  {path_name:<10} {url:<50} {response.status}")
            except Exception as e:
                print(f"  {path_name:<10} {url:<50} ERROR: {str(e)[:50]}")
    
    print("\n" + "="*80)
    print("📋 Next Steps:")
    print("1. Commit and push these port changes")
    print("2. Update Coolify to expose port 8082 instead of 8000")
    print("3. Update domain configuration if needed")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(health_check_8082())
