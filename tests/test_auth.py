
import json
from pkg.models import db, User, Organisation, UserOrganisation
from flask_jwt_extended import decode_token
from datetime import datetime


def test_register_user_successfully(client):
    response = client.post('/auth/register', json={
        "first_name": "Tansi",
        "last_name": "Chinua",
        "email": "tansi@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    data = response.get_json()
    assert response.status_code == 201
    assert data['data']['user']['first_name'] == "John"
    assert "accessToken" in data['data']

def test_login_user_successfully(client):
    # Register a user first
    client.post('/auth/register', json={
        "first_name": "Tansi",
        "last_name": "Chinua",
        "email": "tansi@example.com",
        "password": "password123",
        "phone": "0987654321"
    })

    response = client.post('/auth/login', json={
        "email": "tansi@example.com",
        "password": "password123"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data['data']['user']['first_name'] == "Tansi"
    assert "accessToken" in data['data']

def test_register_user_missing_fields(client):
    response = client.post('/auth/register', json={
        "first_name": "John",
        "last_name": "Doe",
        # Missing email and password
        "phone": "1234567890"
    })
    data = response.get_json()
    assert response.status_code == 422
    assert len(data['errors']) > 0

def test_register_duplicate_email(client):
    client.post('/auth/register', json={
        "first_name": "Chibuzor",
        "last_name": "Godwin",
        "email": "chibuzor@example.com",
        "password": "password123",
        "phone": "1234567890"
    })

    response = client.post('/auth/register', json={
        "first_name": "Chikaodi",
        "last_name": "Mathias",
        "email": "chibuzor@example.com",
        "password": "password456",
        "phone": "0987654321"
    })
    assert response.status_code == 400

def test_token_generation(client):
    response = client.post('/auth/register', json={
        "first_name": "Emeka",
        "last_name": "Valentine",
        "email": "val@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    data = response.get_json()
    token = data['data']['accessToken']
    decoded_token = decode_token(token)
    assert decoded_token['identity'] == "charlie@example.com"
    assert decoded_token['exp'] > int(datetime.utcnow().timestamp())

def test_access_protected_organisation_data(client):
    # Register and log in a user
    client.post('/auth/register', json={
        "first_name": "Peter",
        "last_name": "Sunday",
        "email": "peter@example.com",
        "password": "password123",
        "phone": "1234567890"
    })
    login_response = client.post('/auth/login', json={
        "email": "peter@example.com",
        "password": "password123"
    })
    token = login_response.get_json()['data']['accessToken']

    # Access protected organisation data
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get('/api/organisations', headers=headers)
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['data']['organisations']) > 0

def test_prevent_unauthorised_organisation_access(client):
    # Register and log in the first user
    client.post('/auth/register', json={
        "first_name": "Arinze",
        "last_name": "Edet",
        "email": "arinze@example.com",
        "password": "password123",
        "phone": "08034449193"
    })
    login_response = client.post('/auth/login', json={
        "email": "arinze@example.com",
        "password": "password123"
    })
    token = login_response.get_json()['data']['accessToken']

    # Create an organisation with a second user
    client.post('/auth/register', json={
        "first_name": "Mulumba",
        "last_name": "Uchenna",
        "email": "mulumba@example.com",
        "password": "password123",
        "phone": "07069741483"
    })
    mulumba_login_response = client.post('/auth/login', json={
        "email": "mulumba@example.com",
        "password": "password123"
    })
    mulumba_token = mulumba_login_response.get_json()['data']['accessToken']
    headers = {"Authorization": f"Bearer {mulumba_token}"}
    client.post('/api/organisations', headers=headers, json={
        "name": "Mulumba's Organisation",
        "description": "Description"
    })

    #accessing Mulumba's organisation with Eva's token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get('/api/organisations', headers=headers)
    data = response.get_json()
    assert response.status_code == 200
    assert all(org['name'] != "Mulumba's Organisation" for org in data['data']['organisations'])