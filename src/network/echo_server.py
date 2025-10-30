# ABOUTME: Simple WebSocket echo server for learning WebSocket basics
# ABOUTME: Server echoes back any message it receives

import asyncio
import websockets
from websockets.legacy.server import WebSocketServerProtocol


async def echo_handler(websocket: WebSocketServerProtocol) -> None:
    """Handle a WebSocket connection by echoing messages back.
    
    Args:
        websocket: The WebSocket connection
    """
    print(f"Client connected from {websocket.remote_address}")
    
    try:
        async for message in websocket:
            # Handle both str and bytes
            if isinstance(message, bytes):
                message_str = message.decode('utf-8')
            else:
                message_str = message
            
            print(f"Received: {message_str}")
            response = f"Echo: {message_str}"
            await websocket.send(response)
            print(f"Sent: {response}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} disconnected")


async def main() -> None:
    """Start the echo server."""
    host = "localhost"
    port = 8765
    
    print(f"Starting echo server on {host}:{port}")
    
    async with websockets.serve(echo_handler, host, port):  # type: ignore[arg-type]
        print("Echo server is running. Press Ctrl+C to stop.")
        # Keep server running forever
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
