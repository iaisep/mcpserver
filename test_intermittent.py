#!/usr/bin/env python3
"""
Test script to check for intermittent issues with the MCP-Odoo server
"""
import asyncio
import aiohttp
import time
from datetime import datetime

BASE_URL = "https://dev2.odoo.universidadisep.com"

async def check_endpoint(session, url, endpoint_name):
    """Check a single endpoint"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            return {
                'endpoint': endpoint_name,
                'status': response.status,
                'success': True,
                'time': datetime.now().strftime("%H:%M:%S")
            }
    except asyncio.TimeoutError:
        return {
            'endpoint': endpoint_name,
            'status': 'TIMEOUT',
            'success': False,
            'time': datetime.now().strftime("%H:%M:%S")
        }
    except Exception as e:
        return {
            'endpoint': endpoint_name,
            'status': f'ERROR: {str(e)}',
            'success': False,
            'time': datetime.now().strftime("%H:%M:%S")
        }

async def run_test_cycle():
    """Run a single test cycle"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            check_endpoint(session, f"{BASE_URL}/health", "health"),
            check_endpoint(session, f"{BASE_URL}/sse", "sse"),
            check_endpoint(session, BASE_URL, "root")
        ]
        
        results = await asyncio.gather(*tasks)
        return results

async def monitor_service(cycles=20, delay=5):
    """Monitor service for intermittent issues"""
    print(f"🔍 Monitoring {BASE_URL} for intermittent issues...")
    print(f"Running {cycles} test cycles with {delay}s delay between cycles\n")
    
    all_results = []
    
    for i in range(cycles):
        print(f"Cycle {i+1}/{cycles} at {datetime.now().strftime('%H:%M:%S')}")
        
        cycle_results = await run_test_cycle()
        all_results.extend(cycle_results)
        
        # Print current cycle results
        for result in cycle_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"  {status_icon} {result['endpoint']}: {result['status']}")
        
        if i < cycles - 1:  # Don't sleep after last cycle
            await asyncio.sleep(delay)
        print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 50)
    
    endpoints = ['health', 'sse', 'root']
    for endpoint in endpoints:
        endpoint_results = [r for r in all_results if r['endpoint'] == endpoint]
        successful = [r for r in endpoint_results if r['success']]
        failed = [r for r in endpoint_results if not r['success']]
        
        success_rate = (len(successful) / len(endpoint_results)) * 100
        print(f"{endpoint.upper()}: {len(successful)}/{len(endpoint_results)} successful ({success_rate:.1f}%)")
        
        if failed:
            print(f"  Failures: {[f['status'] for f in failed]}")
    
    # Overall health
    total_tests = len(all_results)
    total_successful = len([r for r in all_results if r['success']])
    overall_success_rate = (total_successful / total_tests) * 100
    
    print(f"\nOVERALL: {total_successful}/{total_tests} successful ({overall_success_rate:.1f}%)")
    
    if overall_success_rate < 95:
        print("⚠️  WARNING: Service showing intermittent issues!")
    elif overall_success_rate == 100:
        print("✅ Service appears stable")
    else:
        print("⚠️  Minor intermittent issues detected")

if __name__ == "__main__":
    asyncio.run(monitor_service())
