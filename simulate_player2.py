import asyncio
import httpx
import websockets
import json

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def simulate_player2():
    print("Registering player2...")
    async with httpx.AsyncClient() as client:
        # Register
        try:
            await client.post(f"{API_URL}/api/auth/register", json={
                "username": "player2",
                "email": "player2@example.com",
                "password": "password123"
            })
        except Exception as e:
            pass # Might already exist
            
        # Login
        resp = await client.post(f"{API_URL}/api/auth/jwt/login", data={
            "username": "player2",
            "password": "password123"
        })
        token = resp.json()["access_token"]
        print("Player2 logged in.")
        
    print("Connecting WS...")
    async with websockets.connect(f"{WS_URL}/api/ws/battle?token={token}") as ws:
        # Wait for connected
        msg = await ws.recv()
        print("WS connected:", msg)
        
        # Join queue
        print("Joining matchmaking queue...")
        await ws.send(json.dumps({"type": "join_queue"}))
        
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            print("Received:", data["type"])
            if data["type"] == "match_found":
                print("Match found! Player2 is in the match.")
                # Just keep connection alive so the match doesn't abort
            elif data["type"] == "match_ended":
                print("Match ended:", data)
                break

if __name__ == "__main__":
    asyncio.run(simulate_player2())
