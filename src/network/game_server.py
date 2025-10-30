# ABOUTME: GameServer for managing multiple game rooms
# ABOUTME: Routes messages, manages connections, broadcasts updates

import asyncio
import uuid
from typing import Dict
from websockets.legacy.server import WebSocketServerProtocol
import websockets

from src.network.protocol import MessageType, encode_message, decode_message
from src.network.game_room import GameRoom
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.config import GameConfig
from src.player import Player


class GameServer:
    """Manages multiple game rooms and WebSocket connections."""
    
    def __init__(self) -> None:
        """Initialize the game server."""
        self.rooms: Dict[str, GameRoom] = {}
        self.player_to_room: Dict[str, str] = {}  # player_id -> room_id
        
        # Shared game resources
        print("Loading dictionary...")
        self.dictionary = Dictionary("data/sowpods.txt")
        self.scorer = Scorer(min_word_length=3)
    
    async def handle_client(self, websocket: WebSocketServerProtocol) -> None:
        """Handle a client connection.
        
        Args:
            websocket: Client's WebSocket connection
        """
        player_id = str(uuid.uuid4())
        print(f"Client connected: {player_id} from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                # Handle both str and bytes
                if isinstance(message, bytes):
                    message_str = message.decode('utf-8')
                else:
                    message_str = message
                await self.handle_message(player_id, websocket, message_str)
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected: {player_id}")
        finally:
            await self.handle_disconnect(player_id)
    
    async def handle_message(
        self,
        player_id: str,
        websocket: WebSocketServerProtocol,
        message_str: str
    ) -> None:
        """Handle a message from a client.
        
        Args:
            player_id: ID of the sending player
            websocket: Player's WebSocket connection
            message_str: JSON message string
        """
        try:
            message = decode_message(message_str)
            message_type = message.get("type")
            
            print(f"Received from {player_id}: {message_type}")
            
            if message_type == MessageType.CREATE_ROOM:
                await self.handle_create_room(player_id, websocket, message)
            elif message_type == MessageType.JOIN_ROOM:
                await self.handle_join_room(player_id, websocket, message)
            elif message_type == MessageType.START_GAME:
                await self.handle_start_game(player_id)
            elif message_type == MessageType.SUBMIT_WORD:
                await self.handle_submit_word(player_id, message)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}")
                
        except Exception as e:
            print(f"Error handling message: {e}")
            await self.send_error(websocket, str(e))
    
    async def handle_create_room(
        self,
        player_id: str,
        websocket: WebSocketServerProtocol,
        message: Dict
    ) -> None:
        """Handle room creation request.
        
        Args:
            player_id: Creating player's ID
            websocket: Player's WebSocket connection
            message: Request message
        """
        room_id = str(uuid.uuid4())[:8]  # Short room ID
        player_name = message.get("player_name", "Player")
        
        # Create room with config
        config = GameConfig(
            max_players=message.get("max_players", 4),
            time_limit_seconds=message.get("time_limit", 180)
        )
        room = GameRoom(room_id, config)
        self.rooms[room_id] = room
        
        # Add creator to room
        room.add_player(player_id, player_name, websocket)
        self.player_to_room[player_id] = room_id
        
        # Send confirmation
        response = encode_message(MessageType.ROOM_CREATED, {
            "room_id": room_id,
            "player_name": player_name
        })
        await websocket.send(response)
        
        print(f"Room created: {room_id} by {player_name} (time limit: {config.time_limit_seconds}s)")
    
    async def handle_join_room(
        self,
        player_id: str,
        websocket: WebSocketServerProtocol,
        message: Dict
    ) -> None:
        """Handle room join request.
        
        Args:
            player_id: Joining player's ID
            websocket: Player's WebSocket connection
            message: Request message
        """
        room_id = message.get("room_id")
        player_name = message.get("player_name", "Player")
        
        if room_id not in self.rooms:
            await self.send_error(websocket, f"Room {room_id} not found")
            return
        
        room = self.rooms[room_id]
        
        if not room.add_player(player_id, player_name, websocket):
            await self.send_error(websocket, "Room is full")
            return
        
        self.player_to_room[player_id] = room_id
        
        # Send confirmation to joining player
        response = encode_message(MessageType.ROOM_JOINED, {
            "room_id": room_id,
            "player_name": player_name,
            "players": [p.name for p in room.players.values()]
        })
        await websocket.send(response)
        
        # Broadcast to other players
        broadcast = encode_message(MessageType.PLAYER_JOINED, {
            "player_name": player_name
        })
        await self.broadcast_to_room(room_id, broadcast, exclude=player_id)
        
        print(f"{player_name} joined room {room_id}")
        
        # Auto-start if room is full
        if len(room.players) == room.config.max_players:
            print(f"Room {room_id} is full - auto-starting game")
            await self.handle_start_game(player_id)
    
    async def handle_start_game(self, player_id: str) -> None:
        """Handle game start request.
        
        Args:
            player_id: Player requesting start
        """
        room_id = self.player_to_room.get(player_id)
        if not room_id:
            return
        
        room = self.rooms[room_id]
        room.start_game(self.dictionary, self.scorer)
        
        # Start timer if configured
        if room.game:
            room.game.start_timer()
        
        # Broadcast game started
        assert room.game is not None
        board_data = [[cell for cell in row] for row in room.game.board.grid]
        
        message = encode_message(MessageType.GAME_STARTED, {
            "board": board_data,
            "players": [p.name for p in room.players.values()],
            "time_limit": room.config.time_limit_seconds
        })
        await self.broadcast_to_room(room_id, message)
        
        print(f"Game started in room {room_id}")
        
        # Start timer task to end game when time expires
        asyncio.create_task(self.monitor_game_timer(room_id))
    
    async def handle_submit_word(self, player_id: str, message: Dict) -> None:
        """Handle word submission.
        
        Args:
            player_id: Submitting player's ID
            message: Request message with word
        """
        room_id = self.player_to_room.get(player_id)
        if not room_id:
            return
        
        room = self.rooms[room_id]
        if not room.game or not room.is_started:
            return
        
        word = message.get("word", "").upper()
        player = room.players[player_id]
        
        # Try to submit word (no turn checking - concurrent submission)
        if room.game.submit_word(word, player):
            score = room.game.scorer.score_word(word)
            
            # Broadcast word accepted
            broadcast = encode_message(MessageType.WORD_ACCEPTED, {
                "player_name": player.name,
                "word": word,
                "score": score
            })
            await self.broadcast_to_room(room_id, broadcast)
        else:
            # Send rejection only to submitter
            response = encode_message(MessageType.WORD_REJECTED, {
                "word": word
            })
            await room.connections[player_id].send(response)
    
    async def handle_pass_turn(self, player_id: str) -> None:
        """Handle pass turn request.
        
        Args:
            player_id: Player passing
        """
        room_id = self.player_to_room.get(player_id)
        if not room_id:
            return
        
        room = self.rooms[room_id]
        if not room.is_started:
            return
        
        room.next_turn()
        
        # Broadcast turn change
        message = encode_message(MessageType.TURN_CHANGED, {
            "current_turn": room.get_current_player_id()
        })
        await self.broadcast_to_room(room_id, message)
    
    async def handle_disconnect(self, player_id: str) -> None:
        """Handle player disconnect.
        
        Args:
            player_id: Disconnected player's ID
        """
        room_id = self.player_to_room.get(player_id)
        if not room_id:
            return
        
        room = self.rooms[room_id]
        player_name = room.players.get(player_id, Player(player_id, "Unknown")).name
        
        room.remove_player(player_id)
        del self.player_to_room[player_id]
        
        # Broadcast player left
        if not room.is_empty():
            message = encode_message(MessageType.PLAYER_LEFT, {
                "player_name": player_name
            })
            await self.broadcast_to_room(room_id, message)
        else:
            # Clean up empty room
            del self.rooms[room_id]
            print(f"Room {room_id} deleted (empty)")
    
    async def broadcast_to_room(
        self,
        room_id: str,
        message: str,
        exclude: str | None = None
    ) -> None:
        """Broadcast a message to all players in a room.
        
        Args:
            room_id: Room to broadcast to
            message: JSON message string
            exclude: Optional player ID to exclude
        """
        room = self.rooms.get(room_id)
        if not room:
            return
        
        websockets_to_send = []
        for pid, ws in room.connections.items():
            if pid != exclude:
                websockets_to_send.append(ws)
        
        if websockets_to_send:
            await asyncio.gather(
                *[ws.send(message) for ws in websockets_to_send],
                return_exceptions=True
            )
    
    async def send_error(self, websocket: WebSocketServerProtocol, error: str) -> None:
        """Send an error message to a client.
        
        Args:
            websocket: Client's WebSocket
            error: Error message
        """
        message = encode_message(MessageType.ERROR, {"error": error})
        await websocket.send(message)
    
    async def monitor_game_timer(self, room_id: str) -> None:
        """Monitor game timer and end game when time expires.
        
        Args:
            room_id: Room to monitor
        """
        room = self.rooms.get(room_id)
        if not room or not room.game:
            return
        
        time_limit = room.config.time_limit_seconds
        
        # Wait for time to expire
        await asyncio.sleep(time_limit)
        
        # Check if room still exists and game is still running
        room = self.rooms.get(room_id)
        if not room or not room.game or not room.is_started:
            return
        
        print(f"Time expired for room {room_id}")
        
        # Calculate final scores
        players_scores = []
        for player in room.players.values():
            score = room.game.get_player_score(player)
            valid_words = room.game.get_player_valid_words(player)
            players_scores.append({
                "name": player.name,
                "score": score,
                "words": list(player.get_words()),
                "valid_words": valid_words
            })
        
        # Broadcast game ended
        message = encode_message(MessageType.GAME_ENDED, {
            "players": players_scores,
            "duplicates": list(room.game.get_duplicate_words())
        })
        await self.broadcast_to_room(room_id, message)
        
        # Mark game as ended
        room.is_started = False


async def main() -> None:
    """Start the game server."""
    server = GameServer()
    
    host = "localhost"
    port = 8765
    
    print(f"Starting Boggle game server on {host}:{port}")
    
    async with websockets.serve(server.handle_client, host, port):  # type: ignore[arg-type]
        print("Game server is running. Press Ctrl+C to stop.")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
