from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
import requests
from pydantic import BaseModel
from agent.controller import run_agent
import os
from dotenv import load_dotenv
import msal



load_dotenv()

app = FastAPI(title="Excel AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

# JWKS_URL = "https://login.microsoftonline.com/common/discovery/keys"
JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/keys"

jwks_cache = None


# =========================
# 🔑 Fetch JWKS (cached)
# =========================
def get_jwks():
    global jwks_cache

    if jwks_cache is None:
        try:
            jwks_cache = requests.get(JWKS_URL).json()
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to fetch JWKS")

    return jwks_cache


# =========================
# 🔑 Get signing key
# =========================
def get_signing_key(token):
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")

    print("🔑 TOKEN KID:", kid)

    jwks = get_jwks()

    for key in jwks["keys"]:
        if key["kid"] == kid:
            print("✅ MATCHED KEY")
            return key

    print("❌ NO MATCHING KEY FOUND")
    raise HTTPException(status_code=401, detail="Invalid token key")


# =========================
# 🔐 Verify Token
# =========================
import msal

def get_graph_token(user_assertion_token: str):
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=os.getenv("SECRET"),
    )

    # Exchange the "API Token" for a "Graph Token"
    result = app.acquire_token_on_behalf_of(
        user_assertion=user_assertion_token,
        scopes=["https://graph.microsoft.com/User.Read", "Files.ReadWrite"] # Scopes for Graph
    )

    return result.get("access_token")


import jwt  # PyJWT (NOT jose)
import json
from jwt.algorithms import RSAAlgorithm
# from jose.backends.rsa_backend import RSAAlgorithm

def verify_token(token: str):
    try:
        headers = jwt.get_unverified_header(token)
        kid = headers["kid"]

        print("🔑 TOKEN KID:", kid)

        jwks = get_jwks()

        key = None
        for k in jwks["keys"]:
            if k["kid"] == kid:
                key = k
                break

        if not key:
            raise HTTPException(status_code=401, detail="Public key not found")

        # 🔥 Convert JWKS → RSA Public Key (THIS FIXES YOUR ERROR)
        public_key = RSAAlgorithm.from_jwk(json.dumps(key))

        expected_audience = f"api://{CLIENT_ID}"

        # ✅ Decode + verify signature properly
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=expected_audience,  
        )

        print("✅ TOKEN VERIFIED")
        print("DECODED:", decoded)

        # =========================
        # VALIDATIONS
        # =========================

        # if decoded.get("tid") != TENANT_ID:
        #     raise HTTPException(status_code=401, detail="Invalid tenant")

        # if TENANT_ID not in decoded.get("iss", ""):
        #     raise HTTPException(status_code=401, detail="Invalid issuer")

        # scopes = decoded.get("scp", "")
        # if "User.Read" not in scopes:
        #     raise HTTPException(status_code=403, detail="Insufficient permissions")

        return decoded
    except jwt.InvalidAudienceError:
        print("❌ Audience mismatch!")
        # Add this print to see what the token actually expected
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
        print(f"Token Audience is: {unverified_claims.get('aud')}")
        raise HTTPException(status_code=401, detail="Audience mismatch")

    # except Exception as e:
    #     print("❌ TOKEN VALIDATION ERROR:", str(e))
    #     raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")
# =========================
# 👤 Auth Dependency
# =========================
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    print("🔥 AUTH HEADER:", auth_header)

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    print("🔥 TOKEN (first 50):", token[:50])

    return verify_token(token)


# =========================
# 📦 Request Schema
# =========================
class QueryRequest(BaseModel):
    query: str


# =========================
# 🧪 Test Endpoint
# =========================
@app.get("/test")
def test(request: Request, user=Depends(get_current_user)):
    # 1. Get the original token sent by React
    auth_header = request.headers.get("Authorization")
    user_token = auth_header.split(" ")[1]

    # 2. Get a token that actually works for Microsoft Graph
    graph_token = get_graph_token(user_token)

    # 3. Use graph_token to call Microsoft APIs...
    
    return {"message": "Success", "user": user.get("name")}

# =========================
# 🤖 Ask Agent Endpoint
# =========================
# main.py

@app.post("/ask")
def ask_agent(body: QueryRequest, request: Request, user=Depends(get_current_user)):
    try:
        # 1. Get the raw Bearer token from the header
        auth_header = request.headers.get("Authorization")
        user_token = auth_header.split(" ")[1]

        # 2. Exchange it for a Graph Token
        graph_token = get_graph_token(user_token)
        
        if not graph_token:
            raise HTTPException(status_code=401, detail="Could not obtain Graph access")

        # 3. Pass the graph_token to the agent
        response = run_agent(body.query, graph_token)

        return {
            "query": body.query,
            "response": response,
            "user": user.get("name"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))