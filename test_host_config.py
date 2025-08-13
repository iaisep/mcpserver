"""
Test script to verify host/port configuration

This script tests that the server can start and bind to 0.0.0.0
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_host_configuration():
    """Test that the configuration loads correctly"""
    from config import config
    
    print("=== Testing Host Configuration ===")
    print(f"Host: {config.server.host}")
    print(f"Port: {config.server.port}")
    print(f"Debug: {config.server.debug}")
    
    # Verify host is 0.0.0.0
    if config.server.host == "0.0.0.0":
        print("✅ Host configuration is correct (0.0.0.0)")
    else:
        print(f"❌ Host configuration is incorrect: {config.server.host}")
        
    # Verify port is 8000 (or as configured in .env)
    expected_port = int(os.environ.get("PORT", "8000"))
    if config.server.port == expected_port:
        print(f"✅ Port configuration is correct ({expected_port})")
    else:
        print(f"❌ Port configuration is incorrect: {config.server.port} (expected {expected_port})")
        
    print("\n=== Environment Variables ===")
    print(f"HOST env var: {os.environ.get('HOST', 'Not set')}")
    print(f"PORT env var: {os.environ.get('PORT', 'Not set')}")
    
    return config.server.host == "0.0.0.0" and config.server.port == expected_port

def test_server_import():
    """Test that server module can be imported and configured"""
    try:
        from server import run_server
        print("✅ Server module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

if __name__ == "__main__":
    print("Host Configuration Test")
    print("=" * 50)
    
    config_ok = test_host_configuration()
    import_ok = test_server_import()
    
    print(f"\n=== Test Results ===")
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Server Import: {'✅ PASS' if import_ok else '❌ FAIL'}")
    
    if config_ok and import_ok:
        print("\n🎉 All tests passed! Server should bind to 0.0.0.0")
    else:
        print("\n⚠️  Some tests failed. Check configuration.")
        
    print("\nNote: This test only validates configuration.")
    print("To fully test, deploy and check server logs for 'Starting SSE server on 0.0.0.0:8000'")
