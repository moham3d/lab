#!/usr/bin/env python3
"""
Comprehensive API Test Script for Patient Visit Management System

This script tests all endpoints in the FastAPI application with proper sequencing:
1. Authentication first
2. Create resources before testing GET operations
3. Test all CRUD operations
4. Handle errors gracefully
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
API_V1_STR = "/api/v1"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.test_user_id: Optional[str] = None
        self.test_patient_id: Optional[str] = None
        self.test_patient_ssn: Optional[str] = None
        self.test_visit_id: Optional[str] = None
        self.test_nursing_assessment_id: Optional[str] = None
        self.test_radiology_assessment_id: Optional[str] = None
        self.test_document_id: Optional[str] = None

    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def make_request(self, method: str, endpoint: str, data: Dict = None,
                    files: Dict = None, params: Dict = None) -> requests.Response:
        """Make HTTP request with authentication"""
        url = f"{BASE_URL}{API_V1_STR}{endpoint}"
        headers = {}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if data and not files:
            headers["Content-Type"] = "application/json"
            data = json.dumps(data)

        self.log(f"Making {method} request to {url}")
        if data and not files:
            self.log(f"Request data: {data}")

        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            files=files,
            params=params
        )

        self.log(f"Response status: {response.status_code}")
        if response.content:
            try:
                self.log(f"Response data: {response.json()}")
            except:
                self.log(f"Response text: {response.text}")

        return response

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.log("=== Testing Authentication Endpoints ===")

        # Use existing admin credentials
        login_data = {
            "username": "admin",
            "password": "admin"
        }

        # Try to login with admin credentials
        response = self.session.post(
            f"{BASE_URL}{API_V1_STR}/auth/login",
            data=login_data
        )

        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            self.log("Login successful with admin credentials, got access token")
        else:
            self.log(f"Login failed: {response.status_code} - {response.text}", "ERROR")
            return False

        # Test refresh token (not implemented)
        refresh_data = {"refresh_token": "dummy_token"}
        response = self.make_request("POST", "/auth/refresh", refresh_data)
        self.log(f"Refresh token test: {response.status_code} (expected 501)")

        # Test logout
        response = self.make_request("POST", "/auth/logout")
        self.log(f"Logout test: {response.status_code}")

        # Test list users
        response = self.make_request("GET", "/auth/users")
        if response.status_code == 200:
            users = response.json()
            self.log(f"Found {len(users)} users")
        else:
            self.log(f"List users failed: {response.status_code}", "ERROR")

        return True

    def test_patient_endpoints(self):
        """Test patient CRUD operations"""
        self.log("=== Testing Patient Endpoints ===")

        # Generate unique patient data
        import time
        unique_id = str(int(time.time() * 1000000))  # More unique
        ssn_suffix = unique_id[-4:]  # Take last 4 digits

        # Create patient
        patient_data = {
            "ssn": f"1234567890{ssn_suffix}",
            "mobile_number": f"010{unique_id[-8:]}",
            "phone_number": f"011{unique_id[-8:]}",
            "medical_number": f"MED{unique_id[-3:]}",
            "full_name": f"John Doe Test {unique_id}",
            "date_of_birth": "1990-01-01",
            "gender": "male"
        }

        response = self.make_request("POST", "/patients/", patient_data)
        if response.status_code == 200:
            patient = response.json()
            self.test_patient_id = patient["id"]
            self.test_patient_ssn = patient["ssn"]
            self.log(f"Created patient with ID: {self.test_patient_id}")
        else:
            self.log(f"Create patient failed: {response.status_code}", "ERROR")
            return False

        # Get patient by ID
        response = self.make_request("GET", f"/patients/{self.test_patient_id}")
        self.log(f"Get patient by ID: {response.status_code}")

        # Get patient by SSN
        response = self.make_request("GET", f"/patients/search/ssn/{patient_data['ssn']}")
        self.log(f"Get patient by SSN: {response.status_code}")

        # Get patient by mobile
        response = self.make_request("GET", f"/patients/search/mobile/{patient_data['mobile_number']}")
        self.log(f"Get patient by mobile: {response.status_code}")

        # Update patient
        update_data = {
            "full_name": f"John Doe Updated {unique_id}",
            "medical_number": f"MED{unique_id[-3:]}-UPD"
        }
        response = self.make_request("PUT", f"/patients/{self.test_patient_id}", update_data)
        self.log(f"Update patient: {response.status_code}")

        # Get patients list
        response = self.make_request("GET", "/patients/")
        self.log(f"Get patients list: {response.status_code}")

        # Search patients
        response = self.make_request("GET", "/patients/", params={"search": "John"})
        self.log(f"Search patients: {response.status_code}")

        # Get patient count
        response = self.make_request("GET", "/patients/stats/count")
        self.log(f"Get patient count: {response.status_code}")

        return True

    def test_visit_endpoints(self):
        """Test visit CRUD operations"""
        self.log("=== Testing Visit Endpoints ===")

        # Create visit
        visit_data = {
            "patient_id": self.test_patient_id,  # Use UUID for visit creation
            "visit_date": (datetime.now() - timedelta(days=1)).isoformat(),  # 1 day ago
            "notes": "Test notes for API testing"
        }

        response = self.make_request("POST", "/visits/", visit_data)
        if response.status_code == 200:
            visit = response.json()
            self.test_visit_id = visit["id"]
            self.log(f"Created visit with ID: {self.test_visit_id}")
        else:
            self.log(f"Create visit failed: {response.status_code}", "ERROR")
            return False

        # Get visit by ID
        response = self.make_request("GET", f"/visits/{self.test_visit_id}")
        self.log(f"Get visit by ID: {response.status_code}")

        # Get visits list
        response = self.make_request("GET", "/visits/")
        self.log(f"Get visits list: {response.status_code}")

        # Get visits by patient
        response = self.make_request("GET", "/visits/", params={"patient_id": self.test_patient_id})
        self.log(f"Get visits by patient: {response.status_code}")

        # Update visit
        update_data = {
            "notes": "Updated test notes"
        }
        response = self.make_request("PUT", f"/visits/{self.test_visit_id}", update_data)
        self.log(f"Update visit: {response.status_code}")

        # Complete visit
        response = self.make_request("POST", f"/visits/{self.test_visit_id}/complete")
        self.log(f"Complete visit: {response.status_code}")

        # Get open visits count
        response = self.make_request("GET", "/visits/stats/open-count")
        self.log(f"Get open visits count: {response.status_code}")

        # Get today's visits
        response = self.make_request("GET", "/visits/today/list")
        self.log(f"Get today's visits: {response.status_code}")

        return True

    def test_assessment_endpoints(self):
        """Test assessment CRUD operations"""
        self.log("=== Testing Assessment Endpoints ===")

        # Skip assessment tests if no visit was created
        if not self.test_visit_id:
            self.log("Skipping assessment tests - no visit available", "ERROR")
            return False

        # Create nursing assessment
        nursing_data = {
            "visit_id": self.test_visit_id,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "temperature_celsius": 36.5,
            "pulse_bpm": 72,
            "respiratory_rate": 16,
            "oxygen_saturation_percent": 98,
            "weight_kg": 70.5,
            "height_cm": 170,
            "bmi": 24.4,
            "pain_scale": 2,
            "chief_complaint": "Test nursing assessment",
            "assessment_notes": "Test assessment notes"
        }

        response = self.make_request("POST", "/assessments/nursing/", nursing_data)
        if response.status_code == 200:
            assessment = response.json()
            self.test_nursing_assessment_id = assessment["assessment_id"]
            self.log(f"Created nursing assessment with ID: {self.test_nursing_assessment_id}")
        else:
            self.log(f"Create nursing assessment failed: {response.status_code}", "ERROR")

        # Create radiology assessment
        radiology_data = {
            "visit_id": self.test_visit_id,
            "modality": "X-ray",
            "body_region": "Chest",
            "findings": "Test radiology findings",
            "impression": "Test impression",
            "recommendations": "Test recommendations"
        }

        response = self.make_request("POST", "/assessments/radiology/", radiology_data)
        if response.status_code == 200:
            assessment = response.json()
            self.test_radiology_assessment_id = assessment["radiology_id"]
            self.log(f"Created radiology assessment with ID: {self.test_radiology_assessment_id}")
        else:
            self.log(f"Create radiology assessment failed: {response.status_code}", "ERROR")

        # Get nursing assessment by ID
        if self.test_nursing_assessment_id:
            response = self.make_request("GET", f"/assessments/nursing/{self.test_nursing_assessment_id}")
            self.log(f"Get nursing assessment by ID: {response.status_code}")

        # Get radiology assessment by ID
        if self.test_radiology_assessment_id:
            response = self.make_request("GET", f"/assessments/radiology/{self.test_radiology_assessment_id}")
            self.log(f"Get radiology assessment by ID: {response.status_code}")

        # Get assessments by visit
        response = self.make_request("GET", f"/assessments/visit/{self.test_visit_id}/nursing")
        self.log(f"Get nursing assessment by visit: {response.status_code}")

        response = self.make_request("GET", f"/assessments/visit/{self.test_visit_id}/radiology")
        self.log(f"Get radiology assessment by visit: {response.status_code}")

        # Get visit assessment status
        response = self.make_request("GET", f"/assessments/visit/{self.test_visit_id}/status")
        self.log(f"Get visit assessment status: {response.status_code}")

        # Get visit assessment summary
        response = self.make_request("GET", f"/assessments/visit/{self.test_visit_id}/summary")
        self.log(f"Get visit assessment summary: {response.status_code}")

        return True

    def test_document_endpoints(self):
        """Test document operations"""
        self.log("=== Testing Document Endpoints ===")

        # Skip document tests if no visit was created
        if not self.test_visit_id:
            self.log("Skipping document tests - no visit available", "ERROR")
            return False

        # Create a test file for upload
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document content for API testing")
            test_file_path = f.name

        try:
            # Upload document
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test_document.txt', f, 'text/plain')}
                params = {
                    'document_type': 'lab_result',
                    'title': 'Test Lab Result',
                    'description': 'Test document for API testing'
                }
                response = self.make_request(
                    "POST",
                    f"/documents/upload/{self.test_visit_id}",
                    files=files,
                    params=params
                )

            if response.status_code == 200:
                document = response.json()
                self.test_document_id = document["document"]["id"]
                self.log(f"Uploaded document with ID: {self.test_document_id}")
            else:
                self.log(f"Upload document failed: {response.status_code}", "ERROR")

            # Get document by ID
            if self.test_document_id:
                response = self.make_request("GET", f"/documents/{self.test_document_id}")
                self.log(f"Get document by ID: {response.status_code}")

            # Get visit documents
            response = self.make_request("GET", f"/documents/visit/{self.test_visit_id}")
            self.log(f"Get visit documents: {response.status_code}")

            # Update document
            if self.test_document_id:
                update_data = {
                    "title": "Updated Test Document",
                    "description": "Updated description"
                }
                response = self.make_request("PUT", f"/documents/{self.test_document_id}", update_data)
                self.log(f"Update document: {response.status_code}")

        finally:
            # Clean up test file
            os.unlink(test_file_path)

        return True

    def test_report_endpoints(self):
        """Test report endpoints"""
        self.log("=== Testing Report Endpoints ===")

        # Get dashboard report
        response = self.make_request("GET", "/reports/dashboard")
        self.log(f"Get dashboard report: {response.status_code}")

        # Get patient statistics (may require admin role)
        response = self.make_request("GET", "/reports/patients/statistics")
        self.log(f"Get patient statistics: {response.status_code}")

        # Get visit volume report
        response = self.make_request("GET", "/reports/visits/volume")
        self.log(f"Get visit volume report: {response.status_code}")

        # Get clinical assessments report
        response = self.make_request("GET", "/reports/clinical/assessments")
        self.log(f"Get clinical assessments report: {response.status_code}")

        # List available reports
        response = self.make_request("GET", "/reports/list")
        self.log(f"List available reports: {response.status_code}")

        return True

    def test_error_cases(self):
        """Test error scenarios"""
        self.log("=== Testing Error Cases ===")

        # Test invalid patient ID
        fake_uuid = str(uuid.uuid4())
        response = self.make_request("GET", f"/patients/{fake_uuid}")
        self.log(f"Get non-existent patient: {response.status_code} (expected 404)")

        # Test invalid visit ID
        response = self.make_request("GET", f"/visits/{fake_uuid}")
        self.log(f"Get non-existent visit: {response.status_code} (expected 404)")

        # Test invalid document ID
        response = self.make_request("GET", f"/documents/{fake_uuid}")
        self.log(f"Get non-existent document: {response.status_code} (expected 404)")

        # Test invalid assessment ID
        response = self.make_request("GET", f"/assessments/nursing/{fake_uuid}")
        self.log(f"Get non-existent nursing assessment: {response.status_code} (expected 404)")

        # Test unauthorized access (without token)
        old_token = self.token
        self.token = None
        response = self.make_request("GET", "/patients/")
        self.log(f"Access without token: {response.status_code} (expected 401)")
        self.token = old_token

        return True

    def run_all_tests(self):
        """Run all test suites"""
        self.log("Starting comprehensive API test suite")
        self.log("=" * 50)

        test_results = []

        # Test authentication first
        if not self.test_auth_endpoints():
            self.log("Authentication tests failed, cannot continue", "ERROR")
            return False

        # Test patient endpoints
        test_results.append(("Patient Endpoints", self.test_patient_endpoints()))

        # Test visit endpoints
        test_results.append(("Visit Endpoints", self.test_visit_endpoints()))

        # Test assessment endpoints
        test_results.append(("Assessment Endpoints", self.test_assessment_endpoints()))

        # Test document endpoints
        test_results.append(("Document Endpoints", self.test_document_endpoints()))

        # Test report endpoints
        test_results.append(("Report Endpoints", self.test_report_endpoints()))

        # Test error cases
        test_results.append(("Error Cases", self.test_error_cases()))

        # Summary
        self.log("=" * 50)
        self.log("TEST SUMMARY:")
        passed = 0
        total = len(test_results)

        for test_name, result in test_results:
            status = "PASS" if result else "FAIL"
            self.log(f"{test_name}: {status}")
            if result:
                passed += 1

        self.log(f"Overall: {passed}/{total} test suites passed")

        if passed == total:
            self.log("🎉 All tests passed successfully!", "SUCCESS")
            return True
        else:
            self.log(f"❌ {total - passed} test suites failed", "ERROR")
            return False


def main():
    """Main function"""
    print("Patient Visit Management System - API Test Script")
    print("=" * 60)

    tester = APITester()

    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()