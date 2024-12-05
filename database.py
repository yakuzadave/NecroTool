import json
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from typing import Optional, Dict
import contextlib

DB_FILE_PATH = 'data/game_data.json'


class Database:
    """A class to handle database operations for the Necromunda simulation."""

    def __init__(self):
        """Initialize the Database instance with a TinyDB connection."""
        self.db = None

    @contextlib.contextmanager
    def get_connection(self):
        """
        Get a database connection that will be automatically closed.

        This uses a caching middleware to improve TinyDB performance.
        """
        try:
            self.db = TinyDB(DB_FILE_PATH, storage=CachingMiddleware(JSONStorage))
            yield self
        finally:
            if self.db:
                self.db.close()
                self.db = None

    def save_game_state(self, game_state: Dict) -> None:
        """
        Save the current game state to the database.

        Args:
            game_state (Dict): The game state to be saved.
        """
        with self.get_connection() as conn:
            conn.db.truncate()  # Clear the current game state.
            conn.db.insert(game_state)

    def load_game_state(self) -> Optional[Dict]:
        """
        Load the saved game state from the database.

        Returns:
            Optional[Dict]: The loaded game state if it exists, None otherwise.
        """
        with self.get_connection() as conn:
            try:
                data = conn.db.all()
                return data[0] if data else None
            except Exception as e:
                print(f"Error loading game state: {e}")
                return None

    def backup_database(self, backup_file: str) -> None:
        """
        Export the database to a backup JSON file.

        Args:
            backup_file (str): The file path to save the backup.
        """
        with self.get_connection() as conn:
            data = conn.db.all()
            with open(backup_file, 'w') as file:
                json.dump(data, file, indent=4)
        print(f"Database backed up to {backup_file}")

    def restore_database(self, backup_file: str) -> None:
        """
        Import the database from a backup JSON file.

        Args:
            backup_file (str): The file path to load the backup from.
        """
        with self.get_connection() as conn:
            with open(backup_file, 'r') as file:
                data = json.load(file)
                conn.db.truncate()
                conn.db.insert_multiple(data)
        print(f"Database restored from {backup_file}")

    def query_game_state(self, key: str, value) -> Optional[Dict]:
        """
        Query the game state for a specific key-value pair.

        Args:
            key (str): The key to query.
            value: The value to match.

        Returns:
            Optional[Dict]: The matched game state entry if it exists, None otherwise.
        """
        with self.get_connection() as conn:
            GameQuery = Query()
            result = conn.db.search(GameQuery[key] == value)
            return result[0] if result else None


def initialize_database() -> Database:
    """
    Initialize and return a Database instance.

    Returns:
        Database: An initialized Database instance.
    """
    return Database()


# Example Usage
if __name__ == "__main__":
    db = initialize_database()

    # Example game state
    game_state = {
        "turn": 1,
        "active_gang": "Iron Lords",
        "scenario": "Ambush",
        "battlefield": {"width": 10, "height": 10},
    }

    # Save game state
    db.save_game_state(game_state)

    # Load game state
    loaded_state = db.load_game_state()
    print("Loaded Game State:", loaded_state)

    # Backup database
    db.backup_database("backup.json")

    # Restore database
    db.restore_database("backup.json")
