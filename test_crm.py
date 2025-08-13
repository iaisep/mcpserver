"""
Test script for CRM functionality

This script provides basic tests for the CRM module to ensure
all tools are working correctly.
"""

import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import Context
from resources.crm import *
from config import config

async def test_crm_functionality():
    """Test basic CRM functionality"""
    
    print("=== Testing CRM Functionality ===\n")
    
    # Create a mock context for testing
    # In real usage, this would be provided by the MCP framework
    class MockContext:
        def __init__(self):
            self.request_context = None
            self.lifespan_context = None
        
        async def info(self, message):
            print(f"INFO: {message}")
        
        async def error(self, message):
            print(f"ERROR: {message}")
    
    ctx = MockContext()
    
    try:
        # Test 1: List CRM Stages
        print("1. Testing list_crm_stages...")
        stages = await list_crm_stages(ctx)
        print(f"   Result: {type(stages)} with {len(stages) if isinstance(stages, list) else 'error'} stages")
        
        # Test 2: List CRM Teams  
        print("\n2. Testing list_crm_teams...")
        teams = await list_crm_teams(ctx)
        print(f"   Result: {type(teams)} with {len(teams) if isinstance(teams, list) else 'error'} teams")
        
        # Test 3: List Academic Programs
        print("\n3. Testing get_academic_programs...")
        programs = await get_academic_programs(ctx)
        print(f"   Result: {type(programs)} with {len(programs) if isinstance(programs, list) else 'error'} programs")
        
        # Test 4: List Leads (basic)
        print("\n4. Testing list_leads...")
        leads = await list_leads(ctx, limit=5)
        print(f"   Result: {type(leads)} with {len(leads) if isinstance(leads, list) else 'error'} leads")
        
        # Test 5: List Partners (basic)
        print("\n5. Testing list_partners...")
        partners = await list_partners(ctx, limit=5)
        print(f"   Result: {type(partners)} with {len(partners) if isinstance(partners, list) else 'error'} partners")
        
        # Test 6: Dashboard Stats
        print("\n6. Testing get_crm_dashboard_stats...")
        stats = await get_crm_dashboard_stats(ctx)
        print(f"   Result: {type(stats)}")
        
        print("\n=== All Tests Completed ===")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("CRM Module Test Script")
    print("Note: This requires a working Odoo connection configured in .env")
    print("=" * 60)
    
    # Run the tests
    asyncio.run(test_crm_functionality())
