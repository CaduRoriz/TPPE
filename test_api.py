import requests
import json

# Test creating a hospital
hospital_data = {
    "nome": "Hospital Universitário de Brasília",
    "cnpj": "12345678901234",
    "endereco": "Campus Darcy Ribeiro, Asa Norte, Brasília - DF",
    "telefone": "(61) 3107-1000"
}

print("Testing hospital creation...")
try:
    response = requests.post(
        "http://localhost:8000/hospitais/",
        json=hospital_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200 or response.status_code == 201:
        hospital = response.json()
        print(f"Hospital created successfully: {hospital}")
        hospital_id = hospital['id']
        
        # Test creating a patient
        patient_data = {
            "nome": "João Silva",
            "cpf": "12345678901",
            "data_nascimento": "1990-01-15",
            "status_saude": "Estável",
            "hospital_id": hospital_id
        }
        
        print("\nTesting patient creation...")
        patient_response = requests.post(
            "http://localhost:8000/pacientes/",
            json=patient_data
        )
        print(f"Patient Status Code: {patient_response.status_code}")
        print(f"Patient Response: {patient_response.text}")
        
        # Test listing hospitals
        print("\nTesting listing hospitals...")
        list_response = requests.get("http://localhost:8000/hospitais/")
        print(f"List Status Code: {list_response.status_code}")
        print(f"List Response: {list_response.text}")
    
    else:
        print(f"Error creating hospital: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
