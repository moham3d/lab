#!/usr/bin/env python3
"""
Quick test to verify assessment creation works with open visits
"""

import requests
import json
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def test_assessment_creation():
    """Test assessment creation with open visit"""
    
    # Generate unique identifiers
    random_suffix = random.randint(10000, 99999)
    
    # Login first using form data
    login_data = {"username": "admin", "password": "admin"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Login successful with token: {token[:20]}...")
    
    # Create a patient
    patient_data = {
        "ssn": f"123456789{random_suffix}",
        "mobile_number": f"010{random_suffix}001",
        "phone_number": f"011{random_suffix}001",
        "medical_number": f"TEST{random_suffix}",
        "full_name": f"Test Patient for Assessment {random_suffix}",
        "date_of_birth": "1990-01-01",
        "gender": "male"
    }
    
    response = requests.post(f"{BASE_URL}/patients/", json=patient_data, headers=headers)
    if response.status_code != 200:
        print(f"Patient creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    patient = response.json()
    patient_id = patient["id"]
    print(f"Created patient: {patient_id}")
    
    # Create a visit (and keep it open)
    visit_data = {
        "patient_id": patient_id,
        "visit_date": (datetime.now() - timedelta(days=1)).isoformat(),
        "notes": "Test visit for assessment testing"
    }
    
    response = requests.post(f"{BASE_URL}/visits/", json=visit_data, headers=headers)
    if response.status_code != 200:
        print(f"Visit creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    visit = response.json()
    visit_id = visit["id"]
    print(f"Created visit: {visit_id} (status: {visit['status']})")
    
    # Create nursing assessment
    nursing_data = {
        "visit_id": visit_id,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "temperature_celsius": 36.5,
        "pulse_bpm": 72,
        "respiratory_rate_per_min": 16,
        "oxygen_saturation_percent": 98.0,
        "weight_kg": 70.5,
        "height_cm": 170.0,
        "notes": "Test nursing assessment"
    }
    
    response = requests.post(f"{BASE_URL}/assessments/nursing/", json=nursing_data, headers=headers)
    print(f"Nursing assessment creation: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Nursing assessment created successfully")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"✗ Nursing assessment failed")
        print(f"Response: {response.text}")
    
    # Create radiology assessment
    radiology_data = {
        "visit_id": visit_id,
        "modality": "X-ray",
        "body_region": "Chest", 
        "findings": "Test radiology findings for assessment",
        "diagnosis": "Test diagnosis",
        "recommendations": "Test recommendations"
    }
    
    response = requests.post(f"{BASE_URL}/assessments/radiology/", json=radiology_data, headers=headers)
    print(f"Radiology assessment creation: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Radiology assessment created successfully")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"✗ Radiology assessment failed")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_assessment_creation()