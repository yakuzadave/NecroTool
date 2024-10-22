import json
from tinydb import TinyDB, Query
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
        """Get a database connection that will be automatically closed."""
        try:
            self.db = TinyDB(DB_FILE_PATH)
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
        self.db.truncate()
        self.db.insert(game_state)

    def load_game_state(self) -> Optional[Dict]:
        """
        Load the saved game state from the database.

        Returns:
            Optional[Dict]: The loaded game state if it exists, None otherwise.
        """
        try:
            data = self.db.all()
            return data[0] if data else None
        except Exception as e:
            print(f"Error loading game state: {e}")
            return None

def initialize_database() -> Database:
    """
    Initialize and return a Database instance.

    Returns:
        Database: An initialized Database instance.
    """
    return Database()
