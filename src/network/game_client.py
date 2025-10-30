# ABOUTME: Network game client for connecting to Boggle game server
# ABOUTME: Handles WebSocket connection and message routing

import asyncio
import json
from typing import Dict, Any, Optional
import websockets

from src.network.protocol import MessageType, encode_message, decode_message


class GameClient:
    """Network client for Boggle game."""
    
    def __init__(self, server_uri: str = "ws://localhost:8765") -> None:
        """Initialize the game client.
        
        Args:
            server_uri: WebSocket server URI
        """
        self.server_uri = server_uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None  # type: ignore[name-defined]
        
        # Game state
        self.room_id: Optional[str] = None
        self.player_name: Optional[str] = None
        self.current_turn: Optional[str] = None
        self.board: Optional[list[list[str]]] = None
        self.players: list[str] = []
        
        # Control flags
        self.connected = False
        self.in_game = False
    
    async def connect(self) -> None:
        """Connect to the game server."""
        print(f"Connecting to {self.server_uri}...")
        self.websocket = await websockets.connect(self.server_uri)
        self.connected = True
        print("Connected to server!")
    
    async def disconnect(self) -> None:
        """Disconnect from the server."""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        print("Disconnected from server.")
    
    async def send_message(self, message_type: MessageType, data: Dict[str, Any] | None = None) -> None:
        """Send a message to the server.
        
        Args:
            message_type: Type of message
            data: Message payload
        """
        if not self.websocket:
            return
        
        message = encode_message(message_type, data)
        await self.websocket.send(message)
    
    async def receive_messages(self) -> None:
        """Receive and handle messages from server."""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                # Handle both str and bytes
                if isinstance(message, bytes):
                    message_str = message.decode('utf-8')
                else:
                    message_str = message
                
                await self.handle_message(message_str)
        except websockets.exceptions.ConnectionClosed:
            print("\nConnection to server lost.")
            self.connected = False
        except Exception as e:
            print(f"\nError in receive loop: {e}")
            import traceback
            traceback.print_exc()
            self.connected = False
    
    async def handle_message(self, message_str: str) -> None:
        """Handle a message from the server.
        
        Args:
            message_str: JSON message string
        """
        try:
            message = decode_message(message_str)
            message_type = message.get("type")
            
            if message_type == MessageType.ROOM_CREATED:
                self.handle_room_created(message)
            elif message_type == MessageType.ROOM_JOINED:
                self.handle_room_joined(message)
            elif message_type == MessageType.PLAYER_JOINED:
                self.handle_player_joined(message)
            elif message_type == MessageType.PLAYER_LEFT:
                self.handle_player_left(message)
            elif message_type == MessageType.GAME_STARTED:
                self.handle_game_started(message)
            elif message_type == MessageType.WORD_ACCEPTED:
                self.handle_word_accepted(message)
            elif message_type == MessageType.WORD_REJECTED:
                self.handle_word_rejected(message)
            elif message_type == MessageType.GAME_ENDED:
                self.handle_game_ended(message)
            elif message_type == MessageType.ERROR:
                self.handle_error(message)
            else:
                print(f"Unknown message type: {message_type}")
                
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def handle_room_created(self, message: Dict[str, Any]) -> None:
        """Handle room created confirmation."""
        self.room_id = message.get("room_id")
        self.player_name = message.get("player_name")
        print(f"\n✓ Room created: {self.room_id}")
        print(f"You are: {self.player_name}")
        print("Share this room ID with other players!")
    
    def handle_room_joined(self, message: Dict[str, Any]) -> None:
        """Handle room joined confirmation."""
        self.room_id = message.get("room_id")
        self.player_name = message.get("player_name")
        self.players = message.get("players", [])
        print(f"\n✓ Joined room: {self.room_id}")
        print(f"You are: {self.player_name}")
        print(f"Players in room: {', '.join(self.players)}")
    
    def handle_player_joined(self, message: Dict[str, Any]) -> None:
        """Handle another player joining."""
        player_name = message.get("player_name")
        if player_name:
            self.players.append(player_name)
            print(f"\n→ {player_name} joined the room")
            print(f"Players: {', '.join(self.players)}")
            print("\n> ", end="", flush=True)  # Re-display prompt
    
    def handle_player_left(self, message: Dict[str, Any]) -> None:
        """Handle player leaving."""
        player_name = message.get("player_name")
        if player_name and player_name in self.players:
            self.players.remove(player_name)
            print(f"\n← {player_name} left the room")
    
    def handle_game_started(self, message: Dict[str, Any]) -> None:
        """Handle game start."""
        print("\n[DEBUG] Received GAME_STARTED message")
        self.board = message.get("board")
        self.players = message.get("players", [])
        time_limit = message.get("time_limit", 180)
        self.in_game = True
        
        print("\n" + "=" * 40)
        print("        GAME STARTED!")
        print("=" * 40)
        self.display_board()
        print(f"\nPlayers: {', '.join(self.players)}")
        print("Everyone can submit words concurrently!")
        print(f"⏱️  Time limit: {time_limit // 60} minutes")
    
    def handle_word_accepted(self, message: Dict[str, Any]) -> None:
        """Handle word acceptance."""
        player_name = message.get("player_name")
        word = message.get("word")
        score = message.get("score")
        print(f"\n✓ {player_name} found: {word} (+{score} points)")
        if self.in_game:
            print("\n> ", end="", flush=True)  # Re-display prompt
    
    def handle_word_rejected(self, message: Dict[str, Any]) -> None:
        """Handle word rejection."""
        word = message.get("word")
        print(f"\n✗ {word} was rejected")
        if self.in_game:
            print("\n> ", end="", flush=True)  # Re-display prompt
    
    def handle_turn_changed(self, message: Dict[str, Any]) -> None:
        """Handle turn change."""
        self.current_turn = message.get("current_turn")
        self.display_turn()
        if self.in_game:
            print("\n> ", end="", flush=True)  # Re-display prompt
    
    def handle_error(self, message: Dict[str, Any]) -> None:
        """Handle error message."""
        error = message.get("error")
        print(f"\n✗ Error: {error}")
    
    def handle_game_ended(self, message: Dict[str, Any]) -> None:
        """Handle game ended message with final scores."""
        self.in_game = False
        
        players_scores = message.get("players", [])
        duplicates = set(message.get("duplicates", []))
        
        print("\n" + "=" * 60)
        print("⏰ TIME'S UP! ⏰")
        print("=" * 60)
        
        # Sort by score
        players_scores.sort(key=lambda p: p["score"], reverse=True)
        
        print("\nFINAL SCORES:")
        print("=" * 60)
        for rank, player_data in enumerate(players_scores, 1):
            name = player_data["name"]
            score = player_data["score"]
            total_words = len(player_data["words"])
            valid_count = len(player_data["valid_words"])
            struck = total_words - valid_count
            
            print(f"{rank}. {name}: {score} points ({total_words} words, {struck} struck out)")
        
        print("\n" + "=" * 60)
        print("WORD BREAKDOWN:")
        print("=" * 60)
        
        for player_data in players_scores:
            name = player_data["name"]
            words = player_data["words"]
            valid_words = set(player_data["valid_words"])
            
            print(f"\n{name}'s words:")
            if valid_words:
                for word in sorted(valid_words):
                    print(f"  ✓ {word}")
            
            struck_words = [w for w in words if w in duplicates]
            if struck_words:
                print(f"  Struck out:")
                for word in sorted(struck_words):
                    print(f"  ✗ {word}")
        
        print("\n" + "=" * 60)
        print("Game over! Thanks for playing!")
        print("=" * 60 + "\n")
    
    def display_board(self) -> None:
        """Display the game board."""
        if not self.board:
            return
        
        print("\n" + "=" * 20)
        print("    BOGGLE BOARD")
        print("=" * 20)
        for row in self.board:
            print("  " + "  ".join(f"{cell:2}" for cell in row))
        print("=" * 20)
    
    def display_turn(self) -> None:
        """Display whose turn it is."""
        if not self.current_turn or not self.in_game:
            return
        
        # current_turn is a player_id, we don't have a mapping to names
        # For now, just indicate if game is active
        print(f"\nWaiting for turns...")
    
    async def create_room(self, player_name: str, max_players: int = 4, time_limit: int = 180) -> None:
        """Create a new game room.
        
        Args:
            player_name: Your name
            max_players: Maximum players allowed
            time_limit: Time limit in seconds
        """
        await self.send_message(MessageType.CREATE_ROOM, {
            "player_name": player_name,
            "max_players": max_players,
            "time_limit": time_limit
        })
    
    async def join_room(self, room_id: str, player_name: str) -> None:
        """Join an existing room.
        
        Args:
            room_id: Room ID to join
            player_name: Your name
        """
        await self.send_message(MessageType.JOIN_ROOM, {
            "room_id": room_id,
            "player_name": player_name
        })
    
    async def start_game(self) -> None:
        """Request to start the game."""
        await self.send_message(MessageType.START_GAME)
    
    async def submit_word(self, word: str) -> None:
        """Submit a word.
        
        Args:
            word: Word to submit
        """
        print(f"[DEBUG] Submitting word: {word}")
        await self.send_message(MessageType.SUBMIT_WORD, {"word": word})
        print(f"[DEBUG] Word sent to server")
    
    async def pass_turn(self) -> None:
        """Pass your turn."""
        await self.send_message(MessageType.PASS_TURN)
