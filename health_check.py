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
    try:
        # Check jobs endpoint (GET)
        jobs_url = "https://haybi-backend.onrender.com/api/jobs"
        print(f"\nChecking jobs endpoint: {jobs_url}")
        
        response = requests.get(jobs_url, timeout=10)
        print(f"Jobs endpoint status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Jobs endpoint is accessible!")
        else:
            print(f"❌ Jobs endpoint returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to jobs endpoint - server might be down or unreachable")
    except requests.exceptions.Timeout:
        print("❌ Jobs endpoint request timed out")
    except Exception as e:
        print(f"❌ Error checking jobs endpoint: {e}")

if __name__ == "__main__":
    print("🔍 Checking backend health...")
    
    if check_backend_health():
        check_api_endpoints()
    else:
        print("\n💡 Troubleshooting tips:")
        print("1. Check your Render dashboard for deployment status")
        print("2. Verify environment variables are set correctly")
        print("3. Make sure your start command is: uvicorn app.main:app --host 0.0.0.0 --port $PORT")
        print("4. Check Render logs for any error messages")