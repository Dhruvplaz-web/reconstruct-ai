"""
Reconstruct.ai — Local Dual-Server Orchestrator
Starts both FastAPI backend (port 8000) and Next.js frontend (port 3000) concurrently.
"""

import subprocess
import sys
import time
import os
import signal

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=" * 65)
    print("  🚀 RECONSTRUCT.AI — LOCAL DEVELOPMENT RUNNER")
    print("  TEAM DOMINATOR • JSPM RSCOE, PUNE")
    print("=" * 65)
    print("\nStarting backend on http://127.0.0.1:8000 ...")

    # Start FastAPI
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=root_dir
    )

    print("Starting Next.js frontend on http://localhost:3000 ...\n")

    # Start Next.js
    frontend_proc = subprocess.Popen(
        "pnpm dev",
        cwd=frontend_dir,
        shell=True
    )

    time.sleep(3)
    print("\n" + "=" * 65)
    print("  ✅ BOTH SERVICES ARE LIVE & CONNECTED!")
    print("  🌐 Web Continuation Hub:    http://localhost:3000")
    print("  📑 OpenAPI Interactive Docs: http://127.0.0.1:8000/docs")
    print("  📜 Official W3C PROV Export: http://127.0.0.1:8000/api/export/w3c-prov")
    print("  🏛️ Architecture ADR Export:  http://127.0.0.1:8000/api/export/adr")
    print("=" * 65)
    print("Press Ctrl+C to terminate both servers cleanly.\n")

    def shutdown(signum, frame):
        print("\nStopping services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
