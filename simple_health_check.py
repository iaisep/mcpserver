#!/usr/bin/env python3
"""
Simple health check script
"""
import asyncio
import aiohttp

async def simple_health_check():
    """Simple health check"""
    urls_to_test = [
        "https://dev2.odoo.universidadisep.com",
        "https://dev2.odoo.universidadisep.com/health",
        "https://dev2.odoo.universidadisep.com/sse"
    ]
    
    print("🩺 Simple health check...")
    
    for url in urls_to_test:
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    print(f"{url:<50} {response.status}")
        except Exception as e:
            print(f"{url:<50} ERROR: {e}")
    
    print("\nIf all show 502, the container is down or restarting")
    print("If /sse shows 200, the server is ready for MCP")

if __name__ == "__main__":
    asyncio.run(simple_health_check())
