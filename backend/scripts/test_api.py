import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    # Test health check
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.status_code, response.json() if response.ok else response.text)

    # Test user creation
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/users/", json=user_data)
    print("\nUser Creation:", response.status_code, response.json() if response.ok else response.text)

    # Test login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/login/access-token", data=login_data)
    print("\nLogin:", response.status_code, response.json() if response.ok else response.text)
    
    if response.ok:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test organization creation
        org_data = {
            "name": "Test Organization"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/organizations/", 
            json=org_data,
            headers=headers
        )
        print("\nOrganization Creation:", response.status_code, response.json() if response.ok else response.text)
        
        # Test getting organizations
        response = requests.get(
            f"{BASE_URL}/api/v1/organizations/",
            headers=headers
        )
        print("\nGet Organizations:", response.status_code, response.json() if response.ok else response.text)

if __name__ == "__main__":
    test_api()
