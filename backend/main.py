import os
import sys

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from db import get_products
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(title="Salesvoice Token Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/token")
async def get_token():
    """
    Generates a LiveKit Access Token for the user.
    """
    room_name = "salesvoice-room"
    # Generate a random participant identity
    participant_identity = f"user-{os.urandom(4).hex()}"
    participant_name = "User"

    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not api_key or not api_secret:
        raise HTTPException(
            status_code=500, detail="LIVEKIT_API_KEY or LIVEKIT_API_SECRET not set"
        )

    grant = api.VideoGrants(room_join=True, room=room_name)
    token = (
        api.AccessToken(api_key, api_secret)
        .with_grants(grant)
        .with_identity(participant_identity)
        .with_name(participant_name)
    )

    livekit_url = os.getenv("LIVEKIT_URL")
    return {"token": token.to_jwt(), "livekit_url": livekit_url}


@app.get("/products")
async def get_products_endpoint():
    """
    Returns the list of available products.
    """
    return get_products()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
