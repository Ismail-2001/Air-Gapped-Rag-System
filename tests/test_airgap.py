"""
Air-Gap Verification Test
Ensures the system is physically and logically isolated from external network access.
"""

import socket
import urllib.request
import requests
import os
import sys

def test_external_dns():
    print("Checking external DNS resolution (8.8.8.8)...")
    try:
        socket.gethostbyname("google.com")
        return False, "EXTERNAL DNS RESOLVED: google.com"
    except socket.error:
        return True, "DNS Resolution Failed (Expected)"

def test_external_socket():
    print("Checking external socket connection (8.8.8.8:53)...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return False, "EXTERNAL SOCKET CONNECTED"
    except (socket.error, socket.timeout):
        return True, "Socket Connection Failed (Expected)"

def test_external_http():
    print("Checking external HTTP connection (google.com)...")
    try:
        urllib.request.urlopen("https://google.com", timeout=2)
        return False, "EXTERNAL HTTP CONNECTED"
    except Exception:
        return True, "HTTP Connection Failed (Expected)"

def test_internal_ollama():
    print("Checking internal Ollama connectivity...")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    try:
        resp = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if resp.status_code == 200:
            return True, "Internal Ollama Accessible"
        return False, f"Ollama returned status {resp.status_code}"
    except Exception as e:
        return False, f"Ollama Access Failed: {str(e)}"

def run_all_tests():
    print("\n--- AIR-GAP SECURITY VERIFICATION ---")
    results = [
        ("External DNS", test_external_dns()),
        ("External Socket", test_external_socket()),
        ("External HTTP", test_external_http()),
        ("Internal Ollama", test_internal_ollama())
    ]
    
    all_passed = True
    for test_name, (passed, msg) in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}: {msg}")
        if not passed:
            all_passed = False
            
    print("\n--------------------------------------")
    if all_passed:
        print("RESULT: SYSTEM IS SECURELY ISOLATED")
    else:
        print("RESULT: SECURITY VERIFICATION FAILED")
        
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
