import requests
import time
from datetime import datetime

def print_section_header(title):
    """Print a section header with formatting"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")

def check_backend_health():
    """
    Check the health of the deployed backend
    """
    print_section_header("HEALTH CHECK")
    
    try:
        # Check health endpoint
        health_url = "https://haybi-backend.onrender.com/health"
        print(f"Checking health endpoint: {health_url}")
        
        response = requests.get(health_url, timeout=15)
        print(f"Health check status code: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend is healthy!")
            print(f"Health timestamp: {health_data.get('timestamp', 'N/A')}")
            return True
        else:
            print("❌ Backend health check failed")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print("❌ Cannot connect to backend - server might be down or unreachable")
        print(f"Error: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print("❌ Request timed out - server might be slow to respond")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking backend health: {e}")
        return False

def check_api_endpoints():
    """
    Check all API endpoints
    """
    print_section_header("API ENDPOINTS CHECK")
    
    base_url = "https://haybi-backend.onrender.com"
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/api/info", "API information"),
        ("/api/jobs", "List jobs (GET)"),
        ("/docs", "API documentation"),
        ("/redoc", "ReDoc documentation")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\nChecking {description}: {url}")
            
            response = requests.get(url, timeout=15)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {description} is accessible!")
                results[endpoint] = "SUCCESS"
                
                # Show brief content for JSON responses
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        if endpoint == "/":
                            print(f"Message: {data.get('message', 'N/A')}")
                        elif endpoint == "/api/info":
                            print(f"API Name: {data.get('name', 'N/A')}")
                    except:
                        pass
            else:
                print(f"❌ {description} returned status code: {response.status_code}")
                results[endpoint] = f"FAILED ({response.status_code})"
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {description} - server might be down")
            results[endpoint] = "CONNECTION ERROR"
        except requests.exceptions.Timeout:
            print(f"❌ {description} request timed out")
            results[endpoint] = "TIMEOUT"
        except Exception as e:
            print(f"❌ Error checking {description}: {e}")
            results[endpoint] = f"ERROR ({str(e)[:50]}...)"
    
    return results

def test_cors_functionality():
    """
    Test CORS functionality for the main API endpoint
    """
    print_section_header("CORS FUNCTIONALITY TEST")
    
    try:
        jobs_url = "https://haybi-backend.onrender.com/api/jobs"
        print(f"Testing CORS for: {jobs_url}")
        
        # Test actual POST request with CORS headers
        response = requests.post(
            jobs_url,
            headers={
                "Origin": "https://example.com",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        
        print(f"POST request status code: {response.status_code}")
        
        # Check for CORS headers in response
        allow_origin = response.headers.get('Access-Control-Allow-Origin', 'Not set')
        print(f"Access-Control-Allow-Origin: {allow_origin}")
        
        if allow_origin != "Not set":
            print("✅ CORS headers are present in response!")
        else:
            print("⚠️  CORS headers not found in response")
            
    except Exception as e:
        print(f"❌ Error testing CORS functionality: {e}")

def test_api_documentation():
    """
    Test if API documentation is accessible
    """
    print_section_header("API DOCUMENTATION CHECK")
    
    docs_urls = [
        ("https://haybi-backend.onrender.com/docs", "Swagger UI"),
        ("https://haybi-backend.onrender.com/redoc", "ReDoc")
    ]
    
    for url, name in docs_urls:
        try:
            print(f"\nChecking {name}: {url}")
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ {name} is accessible!")
                # Check if it looks like the expected documentation
                content = response.text.lower()
                if 'swagger' in content or 'openapi' in content:
                    print(f"📄 {name} content looks correct")
                else:
                    print(f"⚠️  {name} content might not be as expected")
            else:
                print(f"❌ {name} returned status code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")

def generate_report(results):
    """
    Generate a summary report of all tests
    """
    print_section_header("SUMMARY REPORT")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Test completed at: {timestamp}")
    
    success_count = sum(1 for status in results.values() if status == "SUCCESS")
    total_count = len(results)
    
    print(f"\nEndpoints tested: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")
    
    print("\nDetailed results:")
    for endpoint, status in results.items():
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"  {status_icon} {endpoint}: {status}")
    
    if success_count == total_count:
        print("\n🎉 All tests passed! Your backend is working correctly.")
    else:
        print(f"\n⚠️  {total_count - success_count} tests failed. Please check the issues above.")
        
        print("\n💡 Troubleshooting tips:")
        print("1. Check your Render dashboard for deployment status")
        print("2. Verify environment variables are set correctly")
        print("3. Make sure your start command is: uvicorn app.main:app --host 0.0.0.0 --port $PORT")
        print("4. Check Render logs for any error messages")
        print("5. Wait a few minutes for deployment to complete if you just pushed changes")

if __name__ == "__main__":
    print("🔍 Comprehensive Backend Health Check")
    print("This script will test all endpoints and functionality of your backend")
    
    # Check health first
    is_healthy = check_backend_health()
    
    if is_healthy:
        # Test all endpoints
        results = check_api_endpoints()
        
        # Test CORS
        test_cors_functionality()
        
        # Test documentation
        test_api_documentation()
        
        # Generate report
        generate_report(results)
    else:
        print("\n❌ Backend is not healthy. Stopping further tests.")
        print("Please check your Render deployment and try again later.")