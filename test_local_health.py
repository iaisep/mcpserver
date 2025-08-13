#!/usr/bin/env python3
"""
Simple health check script for local testing
"""
import requests
import time

def test_health():
    try:
        response = requests.get("http://localhost:8082/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server not running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🩺 Testing local health endpoint...")
    test_health()
