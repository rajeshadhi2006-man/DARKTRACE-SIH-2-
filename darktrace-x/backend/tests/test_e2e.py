import os
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_full_pipeline():
    # 1. Health check
    r_health = requests.get(f"{BASE_URL}/api/health")
    assert r_health.status_code == 200, f"Health failed: {r_health.status_code}"
    health_data = r_health.json()
    assert health_data["status"] == "HEALTHY"
    print("\n[PASS] Health Check Passed: Service status is HEALTHY")

    # 2. Authentication
    r_login = requests.post(
        f"{BASE_URL}/api/auth/login/json",
        json={"username": "investigator", "password": "Investigator2026!"}
    )
    assert r_login.status_code == 200, f"Login failed: {r_login.text}"
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] Authentication Passed: Investigator token acquired")

    # 3. Dashboard Stats
    r_stats = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
    assert r_stats.status_code == 200, f"Stats failed: {r_stats.text}"
    stats = r_stats.json()
    assert stats["total_actors"] >= 20, "Expected >= 20 actors"
    assert stats["evidence_items"] >= 100, "Expected >= 100 evidence records"
    print(f"[PASS] Dashboard Metrics Passed: {stats['total_actors']} Actors, {stats['total_personas']} Personas, {stats['evidence_items']} Evidence, {stats['total_relationships']} Relationships")

    # 4. Graph API
    r_graph = requests.get(f"{BASE_URL}/api/graph/ACT-0042", headers=headers)
    assert r_graph.status_code == 200, f"Graph failed: {r_graph.text}"
    graph = r_graph.json()
    assert graph["total_nodes"] > 0
    print(f"[PASS] Cytoscape Graph Passed: {graph['total_nodes']} Nodes, {graph['total_edges']} Edges for ACT-0042")

    # 5. Attribution & Contradiction Detection
    r_attr = requests.get(f"{BASE_URL}/api/attribution/ACT-0042", headers=headers)
    assert r_attr.status_code == 200, f"Attribution failed: {r_attr.text}"
    ass_list = r_attr.json()
    assert len(ass_list) > 0
    ass = ass_list[0]
    assert len(ass["supporting_evidence"]) >= 3
    assert len(ass["contradicting_evidence"]) >= 1
    assert ass["recommendation"] == "MANUAL_INVESTIGATOR_REVIEW"
    print(f"[PASS] Attribution Engine Passed: {ass['candidate_persona_a']} <-> {ass['candidate_persona_b']}")
    print(f"    Confidence: {ass['analytical_confidence']} ({int(ass['confidence_score']*100)}%)")
    print(f"    Supporting Evidence: {len(ass['supporting_evidence'])} | Contradicting Evidence: {len(ass['contradicting_evidence'])}")
    print(f"    Recommendation: {ass['recommendation']}")

    # 6. Evidence Integrity Check
    r_evid = requests.get(f"{BASE_URL}/api/evidence/EVID-0001", headers=headers)
    assert r_evid.status_code == 200, f"Evidence failed: {r_evid.text}"
    evid = r_evid.json()
    assert evid["integrity_status"] == "VERIFIED_INTEGRITY"
    assert len(evid["content_hash"]) == 64
    print(f"[PASS] Evidence Integrity Passed: [{evid['id']}] Status: {evid['integrity_status']} (SHA-256: {evid['content_hash'][:16]}...)")

    # 7. PDF Report Compilation
    r_rep = requests.post(f"{BASE_URL}/api/reports/generate", headers=headers, json={"actor_id": "ACT-0042", "format": "PDF"})
    assert r_rep.status_code == 200, f"Report failed: {r_rep.text}"
    rep = r_rep.json()
    assert rep["status"] == "SUCCESS"
    assert rep["file_size"] > 0
    print(f"[PASS] ReportLab PDF Generator Passed: Report ID {rep['report_id']} ({rep['file_size']} bytes)")

    # 8. Frontend React Shell Serving
    r_fe = requests.get(f"{BASE_URL}/")
    assert r_fe.status_code == 200, f"Frontend failed: {r_fe.status_code}"
    assert "DARKTRACE-X" in r_fe.text
    print("[PASS] React + TypeScript Frontend Served Successfully at /")

if __name__ == "__main__":
    test_full_pipeline()
    print("\n============================================================")
    print(" ALL END-TO-END VALIDATION TESTS PASSED (100%)!")
    print("============================================================\n")
