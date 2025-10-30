# ABOUTME: Message protocol definitions for network game
# ABOUTME: Defines message types and structures for client-server communication

from typing import Any, Dict
from enum import Enum
import json


class MessageType(str, Enum):
    """Types of messages exchanged between client and server."""
    
    # Client → Server
    CREATE_ROOM = "create_room"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    START_GAME = "start_game"
    SUBMIT_WORD = "submit_word"
    PASS_TURN = "pass_turn"
    
    # Server → Client
    ROOM_CREATED = "room_created"
    ROOM_JOINED = "room_joined"
    ROOM_LEFT = "room_left"
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    GAME_STARTED = "game_started"
    WORD_ACCEPTED = "word_accepted"
    WORD_REJECTED = "word_rejected"
    TURN_CHANGED = "turn_changed"
    GAME_ENDED = "game_ended"
    ERROR = "error"


def encode_message(message_type: MessageType, data: Dict[str, Any] | None = None) -> str:
    """Encode a message as JSON string.
    
    Args:
        message_type: Type of message
        data: Message payload (optional)
        
    Returns:
        JSON string
    """
    message = {"type": message_type.value}
    if data:
        message.update(data)
    return json.dumps(message)


def decode_message(message_str: str) -> Dict[str, Any]:
    """Decode a JSON message string.
    
    Args:
        message_str: JSON string
        
    Returns:
        Message dictionary
        
    Raises:
        json.JSONDecodeError: If message is not valid JSON
    """
    result: Dict[str, Any] = json.loads(message_str)
    return result
