# import requests
# import time
# import os
# from dotenv import load_dotenv

# load_dotenv()

# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_ID = os.getenv("CLIENT_ID")


# def get_delegated_token():
#     print("🔐 Getting token...")

#     device_code_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"

#     data = {
#         "client_id": CLIENT_ID,
#         "scope": "Files.ReadWrite.All Sites.ReadWrite.All offline_access"
#     }

#     res = requests.post(device_code_url, data=data).json()

#     print(res["message"])

#     device_code = res["device_code"]
#     interval = res["interval"]

#     token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

#     while True:
#         time.sleep(interval)

#         token_res = requests.post(token_url, data={
#             "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
#             "client_id": CLIENT_ID,
#             "device_code": device_code
#         }).json()

#         if "access_token" in token_res:
#             print("✅ Token acquired")
#             return token_res["_token"]

#         elif token_res.get("error") == "authorization_pending":
#             continue
#         else:
#             print("❌ Token error:", token_res)
#             return None


import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

# 🔥 Global cache (VERY IMPORTANT)
ACCESS_TOKEN = None
TOKEN_EXPIRY = 0  # epoch time


def get_delegated_token():
    """
    Device login (ONLY FIRST TIME)
    """
    print("🔐 Performing first-time login...")

    device_code_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"

    data = {
        "client_id": CLIENT_ID,
        "scope": "Files.ReadWrite.All Sites.ReadWrite.All offline_access"
    }

    res = requests.post(device_code_url, data=data).json()

    print("\n🔐 LOGIN REQUIRED:")
    print(res["message"])
    print(f"Device code: {res['device_code']}")

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

            return token_res  # 🔥 RETURN FULL RESPONSE

        elif token_res.get("error") == "authorization_pending":
            continue

        else:
            print("❌ Token error:", token_res)
            return None


def get_valid_token():
    """
    🔥 Smart token manager:
    - Login only once
    - Reuse token until expiry
    """

    global ACCESS_TOKEN, TOKEN_EXPIRY

    # ✅ If token still valid → reuse
    if ACCESS_TOKEN and time.time() < TOKEN_EXPIRY:
        return ACCESS_TOKEN

    # 🔐 First-time login (or expired token)
    token_data = get_delegated_token()

    if not token_data:
        return None

    ACCESS_TOKEN = token_data["access_token"]

    # ⏳ Set expiry (subtract buffer for safety)
    expires_in = token_data.get("expires_in", 3600)
    TOKEN_EXPIRY = time.time() + expires_in - 60  # 1 min buffer

    return ACCESS_TOKEN