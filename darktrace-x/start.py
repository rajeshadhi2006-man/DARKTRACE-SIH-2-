#!/usr/bin/env python3
"""
DARKTRACE-X // Integrated Platform Launcher
Runs the FastAPI intelligence engine and opens the React investigation console.
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
    print(" DARKTRACE-X // THREAT INTELLIGENCE & ENTITY RESOLUTION PLATFORM")
    print("=" * 76)
    print("[+] Core Architecture:")
    print("    • React 18 + TypeScript + Tailwind CSS Frontend (#05070A dark mode)")
    print("    • FastAPI REST API with JWT Auth & Role-Based Access Control")
    print("    • PostgreSQL / SQLite Storage + Neo4j / NetworkX Graph Engine")
    print("    • Multi-Factor Evidence Fusion & Contradiction Detection Engine")
    print("    • ReportLab Forensic Investigation Dossier PDF Generator")
    print("-" * 76)
    print("[+] Access Credentials:")
    print("    • Lead Analyst:  username: investigator  | password: Investigator2026!")
    print("    • Administrator: username: admin         | password: DarktraceAdmin2026!")
    print("    • Supervisor:    username: supervisor    | password: Supervisor2026!")
    print("    • Viewer:        username: viewer        | password: Viewer2026!")
    print("=" * 76)
    print("[+] Starting Server on http://127.0.0.1:8000 ...")

    threading.Thread(target=open_browser, daemon=True).start()

    # Change directory to backend to ensure relative path resolution
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.insert(0, backend_dir)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
