import requests
import time

def check_backend_health():
    """
    Check the health of the deployed backend
    """
    try:
        # Check health endpoint
        health_url = "https://haybi-backend.onrender.com/health"
        print(f"Checking health endpoint: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        print(f"Health check status code: {response.status_code}")
        print(f"Health check response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print("❌ Backend health check failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - server might be down or unreachable")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out - server might be slow to respond")
        return False
    except Exception as e:
        print(f"❌ Error checking backend health: {e}")
        return False

def check_api_endpoints():
    """
    Check the main API endpoints
    """
    base_url = "https://haybi-backend.onrender.com"
    
    # Check root endpoint
    try:
        root_url = f"{base_url}/"
        print(f"\nChecking root endpoint: {root_url}")
        
        response = requests.get(root_url, timeout=10)
        print(f"Root endpoint status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Root endpoint is accessible!")
            print(f"Root response: {response.json()}")
        else:
            print(f"❌ Root endpoint returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to root endpoint - server might be down or unreachable")
    except requests.exceptions.Timeout:
        print("❌ Root endpoint request timed out")
    except Exception as e:
        print(f"❌ Error checking root endpoint: {e}")
    
    # Check jobs endpoint (GET)
    try:
        jobs_url = f"{base_url}/api/jobs"
        print(f"\nChecking jobs endpoint: {jobs_url}")
        
        response = requests.get(jobs_url, timeout=10)
        print(f"Jobs endpoint status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Jobs endpoint is accessible!")
            jobs_data = response.json()
            print(f"Jobs count: {len(jobs_data)}")
        else:
            print(f"❌ Jobs endpoint returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to jobs endpoint - server might be down or unreachable")
    except requests.exceptions.Timeout:
        print("❌ Jobs endpoint request timed out")
    except Exception as e:
        print(f"❌ Error checking jobs endpoint: {e}")
    
    # Check API info endpoint
    try:
        info_url = f"{base_url}/api/info"
        print(f"\nChecking API info endpoint: {info_url}")
        
        response = requests.get(info_url, timeout=10)
        print(f"API info endpoint status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API info endpoint is accessible!")
            info_data = response.json()
            print(f"API Name: {info_data.get('name', 'N/A')}")
        else:
            print(f"❌ API info endpoint returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API info endpoint - server might be down or unreachable")
    except requests.exceptions.Timeout:
        print("❌ API info endpoint request timed out")
    except Exception as e:
        print(f"❌ Error checking API info endpoint: {e}")

def test_cors_preflight():
    """
    Test CORS preflight request
    """
    try:
        jobs_url = "https://haybi-backend.onrender.com/api/jobs"
        print(f"\nTesting CORS preflight for: {jobs_url}")
        
        response = requests.options(
            jobs_url,
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        print(f"CORS preflight status code: {response.status_code}")
        
        if response.status_code == 200:
            allow_origin = response.headers.get('Access-Control-Allow-Origin', 'Not set')
            print(f"✅ CORS preflight successful!")
            print(f"Access-Control-Allow-Origin: {allow_origin}")
        else:
            print(f"❌ CORS preflight failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing CORS preflight: {e}")

if __name__ == "__main__":
    print("🔍 Checking backend health and endpoints...")
    
    if check_backend_health():
        check_api_endpoints()
        test_cors_preflight()
    else:
        print("\n💡 Troubleshooting tips:")
        print("1. Check your Render dashboard for deployment status")
        print("2. Verify environment variables are set correctly")
        print("3. Make sure your start command is: uvicorn app.main:app --host 0.0.0.0 --port $PORT")
        print("4. Check Render logs for any error messages")