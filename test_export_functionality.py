#!/usr/bin/env python3
"""
Test script for Concern History Export Functionality
This script tests the new export features added to the Piyukonek system.
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"  # Adjust if your server runs on a different port
TEST_USERNAME = "test_student"  # Replace with an actual test student username
TEST_PASSWORD = "test_password"  # Replace with actual test password

def test_login():
    """Test student login"""
    print("Testing student login...")
    
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect after successful login
            print("✓ Login successful")
            return response.cookies
        else:
            print("✗ Login failed")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Login request failed: {e}")
        return None

def test_export_concern_history_pdf(cookies):
    """Test PDF export of concern history"""
    print("\nTesting PDF export of concern history...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/student/export/concern-history?format=pdf",
            cookies=cookies,
            allow_redirects=False
        )
        
        if response.status_code == 200:
            print("✓ PDF export successful")
            print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"Content-Length: {len(response.content)} bytes")
            
            # Save the PDF for inspection
            filename = f"test_concern_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF saved as: {filename}")
            return True
        else:
            print("✗ PDF export failed")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ PDF export request failed: {e}")
        return False



def test_export_concern_details(cookies, concern_id=1):
    """Test export of specific concern details"""
    print(f"\nTesting export of concern details (ID: {concern_id})...")
    
    print(f"\nTesting PDF export...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/student/export/concern-details/{concern_id}",
            cookies=cookies,
            allow_redirects=False
        )
        
        if response.status_code == 200:
            print(f"✓ PDF export successful")
            print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"Content-Length: {len(response.content)} bytes")
            
            # Save the file for inspection
            filename = f"test_concern_details_{concern_id}_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF saved as: {filename}")
        else:
            print(f"✗ PDF export failed")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ PDF export request failed: {e}")

def test_dashboard_access(cookies):
    """Test access to student dashboard"""
    print("\nTesting student dashboard access...")
    
    try:
        response = requests.get(f"{BASE_URL}/student_dashboard", cookies=cookies)
        
        if response.status_code == 200:
            print("✓ Dashboard access successful")
            
            # Check if export button is present in the HTML
            if 'Export PDF' in response.text:
                print("✓ Export button found in dashboard")
                return True
            else:
                print("✗ Export button not found in dashboard")
                return False
        else:
            print("✗ Dashboard access failed")
            print(f"Status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Dashboard request failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Piyukonek Concern History Export Functionality Test")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test login
    cookies = test_login()
    if not cookies:
        print("\n❌ Cannot proceed without successful login")
        return
    
    # Test dashboard access
    dashboard_ok = test_dashboard_access(cookies)
    
    # Test export functionality
    pdf_ok = test_export_concern_history_pdf(cookies)
    
    # Test concern details export
    test_export_concern_details(cookies)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Dashboard Access: {'✓ PASS' if dashboard_ok else '✗ FAIL'}")
    print(f"PDF Export: {'✓ PASS' if pdf_ok else '✗ FAIL'}")
    
    if all([dashboard_ok, pdf_ok]):
        print("\n🎉 All tests passed! Export functionality is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    print("\nGenerated files can be found in the current directory.")
    print("=" * 60)

if __name__ == "__main__":
    main()
