#!/usr/bin/env python3
"""
Test script to verify that all endpoints are working correctly
"""

import requests
import json

def test_endpoints():
    """Test all API endpoints"""
    base_url = "https://haybi-backend.onrender.com"
    
    print("Testing API Endpoints...")
    
    # Test root endpoint
    print("\n1. Testing root endpoint (/)")
    try:
        r = requests.get(base_url + "/", timeout=30)
        if r.status_code == 200:
            print("   ✅ Root endpoint: OK")
            print(f"   📄 Message: {r.json().get('message')}")
        else:
            print(f"   ❌ Root endpoint failed with status {r.status_code}")
            print(f"   📄 Response: {r.text}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test health endpoint
    print("\n2. Testing health endpoint (/health)")
    try:
        r = requests.get(base_url + "/health", timeout=30)
        if r.status_code == 200:
            print("   ✅ Health endpoint: OK")
            print(f"   📊 Status: {r.json().get('status')}")
        else:
            print(f"   ❌ Health endpoint failed with status {r.status_code}")
            print(f"   📄 Response: {r.text}")
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
    
    # Test API info endpoint
    print("\n3. Testing API info endpoint (/api/info)")
    try:
        r = requests.get(base_url + "/api/info", timeout=30)
        if r.status_code == 200:
            print("   ✅ API info endpoint: OK")
            print(f"   📋 API Name: {r.json().get('name')}")
        else:
            print(f"   ❌ API info endpoint failed with status {r.status_code}")
            print(f"   📄 Response: {r.text}")
    except Exception as e:
        print(f"   ❌ API info endpoint error: {e}")
    
    # Test list jobs endpoint
    print("\n4. Testing list jobs endpoint (/api/jobs)")
    try:
        r = requests.get(base_url + "/api/jobs", timeout=30)
        if r.status_code == 200:
            print("   ✅ List jobs endpoint: OK")
            jobs = r.json()
            print(f"   📊 Found {len(jobs)} jobs")
        else:
            print(f"   ❌ List jobs endpoint failed with status {r.status_code}")
            print(f"   📄 Response: {r.text}")
    except Exception as e:
        print(f"   ❌ List jobs endpoint error: {e}")

if __name__ == "__main__":
    test_endpoints()