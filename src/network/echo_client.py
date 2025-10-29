# ABOUTME: Simple WebSocket echo client for learning WebSocket basics
# ABOUTME: Client sends messages and prints responses

import asyncio
import websockets


async def echo_client() -> None:
    """Connect to echo server and send/receive messages."""
    uri = "ws://localhost:8765"
    
    print(f"Connecting to {uri}...")
    
    async with websockets.connect(uri) as websocket:
        print("Connected! Type messages (or 'quit' to exit)")
        
        while True:
            # Get message from user
            message = input("\nYou: ").strip()
            
            if message.lower() == "quit":
                print("Disconnecting...")
                break
            
            if not message:
                continue
            
            # Send to server
            await websocket.send(message)
            print(f"Sent: {message}")
            
            # Receive response
            response = await websocket.recv()
            print(f"Server: {response}")


if __name__ == "__main__":
    try:
        asyncio.run(echo_client())
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except ConnectionRefusedError:
        print("Error: Could not connect to server. Is it running?")
