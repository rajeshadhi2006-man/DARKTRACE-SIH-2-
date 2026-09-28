import sys
import os
import json
import pytest
from datetime import datetime

# Set backend path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import engine, Base, SessionLocal
from app.security.auth import seed_default_roles_and_users
from app.database.seed_data import seed_complete_synthetic_intelligence

client = TestClient(app)

def setup_module():
    """Ensure database schema and synthetic intelligence are initialized."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_roles_and_users(db)
        seed_complete_synthetic_intelligence(db)
    finally:
        db.close()

def test_01_system_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "components" in data
    print("\n[PASS] 01: System Health Check verified.")

def test_02_authentication_and_rbac():
    # Test lead investigator login
    res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    token = data["access_token"]

    # Test /api/auth/me
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "investigator"
    assert res_me.json()["role_id"] == "ANALYST"

    # Test invalid login rejection
    res_bad = client.post("/api/auth/login/json", json={"username": "fake_analyst", "password": "WrongPassword"})
    assert res_bad.status_code in [400, 401]
    print("[PASS] 02: Authentication & RBAC verified.")

def test_03_showcase_actor_ta001_nightfox():
    login_res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # Query TA-001
    res = client.get("/api/actors/TA-001", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "TA-001"
    assert data["primary_name"] == "NightFox"
    assert data["confidence_score"] == 0.82
    assert len(data["personas"]) >= 3
    print(f"[PASS] 03: TA-001 (NightFox) Profile verified: {data['primary_name']} ({int(data['confidence_score']*100)}% Confidence).")

def test_04_attribution_assessment_and_contradiction():
    login_res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = client.get("/api/attribution/TA-001", headers=headers)
    assert res.status_code == 200
    assessments = res.json()
    assert len(assessments) >= 1
    ass = assessments[0]
    assert ass["confidence_score"] == 0.82
    assert len(ass["supporting_evidence"]) >= 7
    assert len(ass["contradicting_evidence"]) >= 1
    assert ass["recommendation"] == "REQUIRES HUMAN VALIDATION"
    print(f"[PASS] 04: Attribution Engine verified: {len(ass['supporting_evidence'])} Supporting vs {len(ass['contradicting_evidence'])} Contradicting Evidence items.")

def test_05_investigations_and_correlation_pipeline():
    login_res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # 1. List investigations
    res_list = client.get("/api/investigations", headers=headers)
    assert res_list.status_code == 200
    invs = res_list.json()
    assert len(invs) >= 1

    # 2. Run correlation pipeline on seed 'nightfox_404'
    inv_id = invs[0]["id"]
    res_corr = client.post(
        f"/api/investigations/{inv_id}/correlate",
        headers=headers,
        json={"seed_type": "alias", "seed_value": "nightfox_404"}
    )
    assert res_corr.status_code == 200
    corr_data = res_corr.json()
    assert corr_data["status"] == "CORRELATION_COMPLETE"
    assert corr_data["actor"]["name"] == "NightFox"
    assert len(corr_data["pipeline_steps"]) == 7
    print(f"[PASS] 05: 7-Stage Correlation Pipeline verified: Seed 'nightfox_404' -> {corr_data['actor']['name']} ({corr_data['actor']['confidence']}%).")

def test_06_campaigns_clustering():
    login_res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = client.get("/api/campaigns", headers=headers)
    assert res.status_code == 200
    campaigns = res.json()
    assert len(campaigns) >= 3
    camp_names = [c["name"] for c in campaigns]
    assert "Operation DarkHydra" in camp_names
    print(f"[PASS] 06: Campaign Clustering verified: {len(campaigns)} Campaigns tracked ({', '.join(camp_names[:2])}).")

def test_07_alerts_engine():
    login_res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = client.get("/api/alerts", headers=headers)
    assert res.status_code == 200
    alerts = res.json()
    assert len(alerts) >= 3
    # Acknowledge first alert
    ack_res = client.post(f"/api/alerts/{alerts[0]['id']}/ack", headers=headers)
    assert ack_res.status_code == 200
    print(f"[PASS] 07: Alert Engine verified: {len(alerts)} alerts active. Acknowledgment validated.")

def test_08_mitre_attack_mapping():
    login_res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = client.get("/api/mitre", headers=headers)
    assert res.status_code == 200
    techniques = res.json()
    assert len(techniques) >= 4
    tech_ids = [t["id"] for t in techniques]
    assert "T1566.001" in tech_ids
    print(f"[PASS] 08: MITRE ATT&CK Mapping verified: {len(techniques)} TTP techniques mapped.")

def test_09_stix_21_bundle_export():
    login_res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = client.get("/api/stix/actor/TA-001", headers=headers)
    assert res.status_code == 200
    bundle = res.json()
    assert bundle["type"] == "bundle"
    assert len(bundle["objects"]) >= 3
    obj_types = [obj["type"] for obj in bundle["objects"]]
    assert "threat-actor" in obj_types
    assert "indicator" in obj_types
    print(f"[PASS] 09: STIX 2.1 Bundle Exporter verified: {len(bundle['objects'])} STIX objects generated.")

def test_10_forensic_pdf_report_generation():
    login_res = client.post("/api/auth/login/json", json={"username": "investigator", "password": "Investigator2026!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = client.post("/api/reports/generate", headers=headers, json={"actor_id": "TA-001", "format": "PDF"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["file_size"] > 0
    print(f"[PASS] 10: ReportLab Forensic Dossier PDF generated: {data['report_id']} ({data['file_size']} bytes).")

if __name__ == "__main__":
    setup_module()
    test_01_system_health()
    test_02_authentication_and_rbac()
    test_03_showcase_actor_ta001_nightfox()
    test_04_attribution_assessment_and_contradiction()
    test_05_investigations_and_correlation_pipeline()
    test_06_campaigns_clustering()
    test_07_alerts_engine()
    test_08_mitre_attack_mapping()
    test_09_stix_21_bundle_export()
    test_10_forensic_pdf_report_generation()
    print("\n============================================================")
    print(" ALL 10 SIH VERIFICATION MODULES PASSED WITH 100% SUCCESS!")
    print("============================================================\n")
