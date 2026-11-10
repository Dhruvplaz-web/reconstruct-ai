"""
Reconstruct.ai — Render Automated Deployment Script
Deploys both FastAPI backend and Next.js frontend to Render via Render Public REST API v1.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

RENDER_API_BASE = "https://api.render.com/v1"
REPO_URL = "https://github.com/Dhruvplaz-web/reconstruct-ai"
DEFAULT_BRANCH = "main"

def get_render_api_key() -> str:
    # 1. Check environment variable
    key = os.environ.get("RENDER_API_KEY", "").strip()
    if key:
        return key

    # 2. Check local .env file
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("RENDER_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val

    # 3. Check CLI argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        return sys.argv[1].strip()

    return ""

def api_request(endpoint: str, api_key: str, method: str = "GET", data: dict = None) -> dict:
    url = f"{RENDER_API_BASE}{endpoint}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            if res_body:
                return json.loads(res_body)
            return {}
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        try:
            parsed = json.loads(error_msg)
            raise RuntimeError(f"Render API error HTTP {e.code}: {parsed.get('message', error_msg)}")
        except Exception:
            raise RuntimeError(f"Render API error HTTP {e.code}: {error_msg}")
    except Exception as e:
        raise RuntimeError(f"Network error communicating with Render API: {e}")

def main():
    print("=" * 65)
    print("  🚀 RECONSTRUCT.AI — RENDER AUTOMATED CLOUD DEPLOYER")
    print("  TEAM DOMINATOR • JSPM RSCOE, PUNE")
    print("=" * 65)

    api_key = get_render_api_key()
    if not api_key:
        print("\n❌ Error: RENDER_API_KEY is not set.")
        print("Please provide your Render API key:")
        print("  1. Pass as environment variable: set RENDER_API_KEY=rnd_...")
        print("  2. Or in .env file: RENDER_API_KEY=rnd_...")
        print("  3. Or pass as argument: python scripts/deploy_to_render.py rnd_...\n")
        sys.exit(1)

    print("\n🔍 1. Validating Render API key...")
    try:
        owners = api_request("/owners", api_key)
        if not owners:
            print("❌ No owners found associated with this API key.")
            sys.exit(1)
        owner_obj = owners[0].get("owner", owners[0])
        owner_id = owner_obj["id"]
        owner_name = owner_obj.get("name", "Render User")
        owner_email = owner_obj.get("email", "")
        print(f"  ✅ Authenticated as: {owner_name} ({owner_email}) [ID: {owner_id}]")
    except Exception as e:
        print(f"  ❌ Authentication failed: {e}")
        sys.exit(1)

    print("\n📦 2. Checking existing services...")
    services = api_request("/services?limit=100", api_key)
    existing_services = {}
    for item in services:
        svc = item.get("service", item)
        existing_services[svc.get("name")] = svc

    backend_name = "reconstruct-ai-backend"
    frontend_name = "reconstruct-ai-frontend"

    # --- Deploy Backend ---
    backend_svc = existing_services.get(backend_name)
    backend_url = ""

    if backend_svc:
        print(f"  ℹ️ Found existing service: {backend_name} [ID: {backend_svc['id']}]")
        backend_url = backend_svc.get("serviceDetails", {}).get("url", f"https://{backend_name}.onrender.com")
        print(f"  🔄 Triggering fresh deployment for backend...")
        deploy_res = api_request(f"/services/{backend_svc['id']}/deploys", api_key, method="POST", data={})
        print(f"  ✅ Backend deploy triggered (ID: {deploy_res.get('id', 'active')})")
    else:
        print(f"  ✨ Creating new Web Service: {backend_name}...")
        backend_payload = {
            "type": "web_service",
            "name": backend_name,
            "ownerId": owner_id,
            "repo": REPO_URL,
            "branch": DEFAULT_BRANCH,
            "autoDeploy": "yes",
            "serviceDetails": {
                "env": "python",
                "plan": "free",
                "region": "oregon",
                "buildCommand": "pip install -r backend/requirements.txt",
                "startCommand": "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT",
                "envVars": [
                    {"key": "PYTHON_VERSION", "value": "3.12.0"}
                ]
            }
        }
        res = api_request("/services", api_key, method="POST", data=backend_payload)
        backend_svc = res.get("service", res)
        backend_url = backend_svc.get("serviceDetails", {}).get("url", f"https://{backend_name}.onrender.com")
        print(f"  ✅ Backend service created [ID: {backend_svc.get('id')}]")

    print(f"  🌐 Backend API URL: {backend_url}")

    # Ensure backend API base format
    api_url = f"{backend_url.rstrip('/')}/api"

    # --- Deploy Frontend ---
    frontend_svc = existing_services.get(frontend_name)
    frontend_url = ""

    if frontend_svc:
        print(f"\n  ℹ️ Found existing service: {frontend_name} [ID: {frontend_svc['id']}]")
        frontend_url = frontend_svc.get("serviceDetails", {}).get("url", f"https://{frontend_name}.onrender.com")
        print(f"  🔄 Triggering fresh deployment for frontend...")
        deploy_res = api_request(f"/services/{frontend_svc['id']}/deploys", api_key, method="POST", data={})
        print(f"  ✅ Frontend deploy triggered (ID: {deploy_res.get('id', 'active')})")
    else:
        print(f"\n  ✨ Creating new Web Service: {frontend_name}...")
        frontend_payload = {
            "type": "web_service",
            "name": frontend_name,
            "ownerId": owner_id,
            "repo": REPO_URL,
            "branch": DEFAULT_BRANCH,
            "rootDir": "frontend",
            "autoDeploy": "yes",
            "serviceDetails": {
                "env": "node",
                "plan": "free",
                "region": "oregon",
                "buildCommand": "pnpm install && pnpm run build",
                "startCommand": "pnpm start",
                "envVars": [
                    {"key": "NODE_VERSION", "value": "20"},
                    {"key": "NEXT_PUBLIC_API_URL", "value": api_url}
                ]
            }
        }
        res = api_request("/services", api_key, method="POST", data=frontend_payload)
        frontend_svc = res.get("service", res)
        frontend_url = frontend_svc.get("serviceDetails", {}).get("url", f"https://{frontend_name}.onrender.com")
        print(f"  ✅ Frontend service created [ID: {frontend_svc.get('id')}]")

    print(f"  🌐 Frontend Web URL: {frontend_url}")

    print("\n" + "=" * 65)
    print("  🎉 DEPLOYMENT ORCHESTRATION COMPLETED!")
    print(f"  🌐 Frontend App: {frontend_url}")
    print(f"  ⚙️ Backend API:  {backend_url}")
    print(f"  📑 Swagger Docs: {backend_url}/docs")
    print(f"  📊 Dashboard:    https://dashboard.render.com")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()

