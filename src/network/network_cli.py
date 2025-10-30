# ABOUTME: CLI interface for network Boggle game
# ABOUTME: Provides interactive menu and game interface

import asyncio
import aioconsole
from src.network.game_client import GameClient


async def main_menu(client: GameClient) -> None:
    """Display main menu and handle user choice.
    
    Args:
        client: The game client
    """
    print("\n" + "=" * 40)
    print("     NETWORK BOGGLE")
    print("=" * 40)
    print("\n1. Create a new room")
    print("2. Join an existing room")
    print("3. Quit")
    
    choice = input("\nChoose an option (1-3): ").strip()
    
    if choice == "1":
        await create_room_flow(client)
    elif choice == "2":
        await join_room_flow(client)
    elif choice == "3":
        print("Goodbye!")
        await client.disconnect()
    else:
        print("Invalid choice.")
        await main_menu(client)


async def create_room_flow(client: GameClient) -> None:
    """Handle room creation flow.
    
    Args:
        client: The game client
    """
    player_name = input("\nYour name: ").strip()
    if not player_name:
        player_name = "Player"
    
    max_players = input("Max players (2-4, default 4): ").strip()
    if not max_players or not max_players.isdigit():
        max_players_int = 4
    else:
        max_players_int = max(2, min(4, int(max_players)))
    
    time_limit = input("Time limit in seconds (default 180 = 3 min): ").strip()
    if not time_limit or not time_limit.isdigit():
        time_limit_int = 180
    else:
        time_limit_int = int(time_limit)
    
    await client.create_room(player_name, max_players_int, time_limit_int)
    
    # Wait a moment for room creation response
    await asyncio.sleep(0.5)
    
    # Enter lobby
    await lobby(client)


async def join_room_flow(client: GameClient) -> None:
    """Handle room joining flow.
    
    Args:
        client: The game client
    """
    print("[DEBUG] Starting join_room_flow")
    room_id = input("\nRoom ID: ").strip()
    if not room_id:
        print("Room ID required!")
        return
    
    player_name = input("Your name: ").strip()
    if not player_name:
        player_name = "Player"
    
    print(f"[DEBUG] Sending join_room: {room_id}, {player_name}")
    await client.join_room(room_id, player_name)
    
    # Wait a moment for join response
    print("[DEBUG] Waiting for join response...")
    await asyncio.sleep(0.5)
    
    print("[DEBUG] Entering lobby...")
    # Enter lobby
    await lobby(client)


async def lobby(client: GameClient) -> None:
    """Lobby where players wait before game starts.
    
    Args:
        client: The game client
    """
    print("\n" + "=" * 40)
    print("         LOBBY")
    print("=" * 40)
    print("\nCommands:")
    print("  start - Start the game (when ready)")
    print("  quit  - Leave the room")
    
    while client.connected and not client.in_game:
        # Create input task so we can check game state while waiting
        input_task = asyncio.create_task(aioconsole.ainput("\n> "))
        
        # Wait for input OR game to start
        while not input_task.done() and not client.in_game:
            await asyncio.sleep(0.1)  # Check game state every 0.1s
        
        # If game started while waiting for input, cancel input and exit
        if client.in_game:
            input_task.cancel()
            try:
                await input_task
            except asyncio.CancelledError:
                pass
            break
        
        # Got input
        command = input_task.result().strip().lower()
        
        # Check again if game started while getting input
        if client.in_game:
            break
        
        if command == "start":
            await client.start_game()
            await asyncio.sleep(0.5)  # Wait for game start message
        elif command == "quit":
            await client.disconnect()
            return
        elif command == "":
            continue
        else:
            print(f"Unknown command: {command}")
    
    # After exiting lobby, enter game if started
    if client.in_game:
        await game_loop(client)


async def game_loop(client: GameClient) -> None:
    """Main game loop for playing.
    
    Args:
        client: The game client
    """
    print("\n" + "=" * 40)
    print("         GAME ON!")
    print("=" * 40)
    print("\nCommands:")
    print("  <word> - Submit a word")
    print("  board  - Show the board again")
    print("  quit   - Leave the game")
    
    while client.connected and client.in_game:
        command = await aioconsole.ainput("\n> ")
        command = command.strip().lower()
        
        if not command:
            continue
        
        if command == "board":
            client.display_board()
        elif command == "quit":
            await client.disconnect()
            break
        else:
            # Assume it's a word submission
            await client.submit_word(command)


async def run_client() -> None:
    """Run the network game client."""
    client = GameClient()
    
    try:
        await client.connect()
        
        # Start receive loop in background
        receive_task = asyncio.create_task(client.receive_messages())
        
        # Show main menu
        await main_menu(client)
        
        # Wait for receive task to finish (or cancel it)
        if not receive_task.done():
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
                
    except ConnectionRefusedError:
        print("Error: Could not connect to server. Is it running?")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client.connected:
            await client.disconnect()


def main() -> None:
    """Entry point for network CLI."""
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")


if __name__ == "__main__":
    main()
