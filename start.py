#!/usr/bin/env python3
"""
DARKTRACE-X // Dark Web Threat Actor Intelligence & Attribution Platform
Primary System Launcher
"""
import sys
import os
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(2.0)
    url = "http://127.0.0.1:8000/login"
    print(f"\n[*] Launching DARKTRACE-X Command Center in default browser: {url} ...\n")
    webbrowser.open(url)

def main():
    print("=" * 76)
    print(" DARKTRACE-X // THREAT ACTOR INTELLIGENCE & ATTRIBUTION PLATFORM")
    print("=" * 76)
    print("[+] Core Architecture:")
    print("    • React 18 + TypeScript + Tailwind CSS Frontend (#05070A dark mode)")
    print("    • FastAPI REST API with JWT Auth & Role-Based Access Control")
    print("    • Multi-Signal Entity Resolution & False Positive Rejection Engine")
    print("    • Passive Infrastructure Correlation (TLS SANs, Apache leaks, Favicon)")
    print("    • AI Stylometric Profiling (Yule's K, Character 3-5 gram TF-IDF)")
    print("    • Diurnal Behavioral Timezone Estimator & Persona Migration Detection")
    print("    • Multi-Relational NetworkX & Neo4j Forensic Graph Engine")
    print("    • Multi-Factor Attribution Scoring with Human-in-the-Loop Arbitration")
    print("    • STIX 2.1 Standardized CTI Exporter & ReportLab PDF Dossier Generator")
    print("-" * 76)
    print("[+] Demo Investigator Accounts:")
    print("    • Lead Analyst:  username: investigator  | password: Investigator2026!")
    print("    • Administrator: username: admin         | password: DarktraceAdmin2026!")
    print("    • Supervisor:    username: supervisor    | password: Supervisor2026!")
    print("    • Viewer:        username: viewer        | password: Viewer2026!")
    print("=" * 76)
    print("[+] Starting Server on http://127.0.0.1:8000 ...")

    threading.Thread(target=open_browser, daemon=True).start()

    # Change directory to darktrace-x backend to resolve local SQLite/Data assets
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "darktrace-x", "backend")
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
