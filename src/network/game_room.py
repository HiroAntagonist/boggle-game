# ABOUTME: GameRoom class for managing a single game session
# ABOUTME: Handles players, game state, and broadcasting updates

from typing import Dict, Set
import uuid
from websockets.legacy.server import WebSocketServerProtocol

from src.board import Board
from src.dictionary import Dictionary
from src.scorer import Scorer
from src.game import Game
from src.player import Player
from src.config import GameConfig


class GameRoom:
    """Manages a single game session with multiple players."""
    
    def __init__(self, room_id: str, config: GameConfig | None = None) -> None:
        """Initialize a game room.
        
        Args:
            room_id: Unique identifier for this room
            config: Game configuration
        """
        self.room_id = room_id
        self.config = config or GameConfig()
        
        # Player management
        self.players: Dict[str, Player] = {}  # player_id -> Player
        self.connections: Dict[str, WebSocketServerProtocol] = {}  # player_id -> websocket
        
        # Game state
        self.game: Game | None = None
        self.is_started = False
        self.current_turn_index = 0
        
    def add_player(self, player_id: str, player_name: str, websocket: WebSocketServerProtocol) -> bool:
        """Add a player to the room.
        
        Args:
            player_id: Unique player ID
            player_name: Player's display name
            websocket: Player's WebSocket connection
            
        Returns:
            True if added successfully, False if room is full
        """
        if len(self.players) >= self.config.max_players:
            return False
        
        if player_id in self.players:
            return False
        
        player = Player(player_id=player_id, name=player_name)
        self.players[player_id] = player
        self.connections[player_id] = websocket
        
        return True
    
    def remove_player(self, player_id: str) -> None:
        """Remove a player from the room.
        
        Args:
            player_id: Player to remove
        """
        if player_id in self.players:
            del self.players[player_id]
        if player_id in self.connections:
            del self.connections[player_id]
    
    def start_game(self, dictionary: Dictionary, scorer: Scorer) -> None:
        """Start the game.
        
        Args:
            dictionary: Word dictionary
            scorer: Scoring calculator
        """
        if self.is_started:
            return
        
        if len(self.players) < 2:
            return
        
        # Create board
        board = Board(size=self.config.board_size)
        
        # Create game
        self.game = Game(
            board=board,
            dictionary=dictionary,
            scorer=scorer,
            config=self.config
        )
        
        # Add players to game
        for player in self.players.values():
            self.game.add_player(player)
        
        self.is_started = True
        self.current_turn_index = 0
    
    def get_current_player_id(self) -> str | None:
        """Get the ID of the player whose turn it is.
        
        Returns:
            Player ID, or None if game not started
        """
        if not self.is_started or not self.players:
            return None
        
        player_ids = list(self.players.keys())
        return player_ids[self.current_turn_index]
    
    def next_turn(self) -> None:
        """Move to the next player's turn."""
        if not self.players:
            return
        
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
    
    def get_all_websockets(self) -> Set[WebSocketServerProtocol]:
        """Get all WebSocket connections in this room.
        
        Returns:
            Set of WebSocket connections
        """
        return set(self.connections.values())
    
    def is_empty(self) -> bool:
        """Check if room has no players.
        
        Returns:
            True if empty
        """
        return len(self.players) == 0
