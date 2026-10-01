import os
os.environ["DATABASE_URL"]="sqlite:///./test.db"
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def register_login():
    email="test@example.com"
    client.post('/api/auth/register',json={"name":"Test User","email":email,"password":"secret123"})
    r=client.post('/api/auth/login',json={"email":email,"password":"secret123"})
    assert r.status_code==200

def test_health():
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_auth_and_home_fallback():
    register_login()
    r=client.post('/api/generate-home',json={"budget":50000,"rooms":["Living Room"],"style":"modern","notes":"","quantities":{"lights":2}})
    assert r.status_code==200
    data=r.json(); assert data['planner']=='home'; assert len(data['recommendations'])>0
