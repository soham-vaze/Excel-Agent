import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

def get_delegated_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"

    data = {
        "client_id": CLIENT_ID,
        "scope": "Files.ReadWrite.All Sites.ReadWrite.All offline_access"
    }

    res = requests.post(url, data=data).json()

    print("\n🔐 LOGIN REQUIRED:")
    print(res["message"])

    device_code = res["device_code"]
    interval = res["interval"]

    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

    while True:
        time.sleep(interval)

        token_res = requests.post(token_url, data={
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": CLIENT_ID,
            "device_code": device_code
        }).json()

        if "access_token" in token_res:
            print("✅ Login successful!")
            return token_res["access_token"]

        elif token_res.get("error") == "authorization_pending":
            continue
        else:
            print("❌ Token Error:", token_res)
            return None