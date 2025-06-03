#!/usr/bin/env python3
"""
SSL Certificate Test Script
This script tests SSL connections and provides debugging information.
"""

import ssl
import certifi
import urllib.request
import os

def test_ssl_connection():
    print("=== SSL Certificate Test ===")
    
    # Check certifi path
    cert_path = certifi.where()
    print(f"Certifi certificate path: {cert_path}")
    print(f"Certificate file exists: {os.path.exists(cert_path)}")
    
    # Check SSL environment variables
    ssl_cert_file = os.environ.get('SSL_CERT_FILE')
    ssl_cert_dir = os.environ.get('SSL_CERT_DIR')
    print(f"SSL_CERT_FILE environment variable: {ssl_cert_file}")
    print(f"SSL_CERT_DIR environment variable: {ssl_cert_dir}")
    
    # Test HTTPS connection
    try:
        print("\nTesting HTTPS connection to httpbin.org...")
        
        # Create SSL context with certifi certificates
        context = ssl.create_default_context(cafile=cert_path)
        
        # Test connection
        with urllib.request.urlopen('https://httpbin.org/get', context=context) as response:
            print(f"✅ SSL connection successful! Status: {response.status}")
            
    except Exception as e:
        print(f"❌ SSL connection failed: {e}")
        
        # Try with system certificates
        try:
            print("Trying with system certificates...")
            context = ssl.create_default_context()
            with urllib.request.urlopen('https://httpbin.org/get', context=context) as response:
                print(f"✅ System SSL connection successful! Status: {response.status}")
        except Exception as e2:
            print(f"❌ System SSL connection also failed: {e2}")
    
    print("\n=== SSL Configuration Recommendations ===")
    print("1. Set SSL_CERT_FILE environment variable:")
    print(f"   export SSL_CERT_FILE={cert_path}")
    print("\n2. Or add to your shell profile (.zshrc, .bashrc):")
    print(f"   echo 'export SSL_CERT_FILE={cert_path}' >> ~/.zshrc")
    print("\n3. For Python code, use:")
    print("   import ssl, certifi")
    print("   ssl_context = ssl.create_default_context(cafile=certifi.where())")

if __name__ == "__main__":
    test_ssl_connection() 