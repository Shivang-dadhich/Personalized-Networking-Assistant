
import json
import logging
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the file path using pathlib.Path for cross-platform safety.
# This creates a 'storage' folder in your project root to keep data organized.
HISTORY_FILE_PATH = Path(__file__).resolve().parent.parent.parent / "storage" / "conversation_history.json"


def load_history() -> List[Dict[str, Any]]:
    """
    Provides a clean read interface that always returns a list of past 
    conversations, even when no history file exists yet.
    
    :return: A list of dictionaries containing conversation history logs.
    """
    # Defensive programming: If the file doesn't exist yet, return an empty list gracefully
    if not HISTORY_FILE_PATH.exists():
        logger.info(f"No history file found at {HISTORY_FILE_PATH}. Returning empty list.")
        return []

    try:
        # Read the entire text file
        with open(HISTORY_FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                logger.warning("History file format was corrupted (not a list). Resetting to empty list.")
                return []
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read or parse history file: {str(e)}")
        # Return empty list instead of crashing the application
        return []


def log_conversation(event_description: str, extracted_themes: List[str], conversation_starters: List[str]) -> bool:
    """
    Appends a new conversation interaction record to the JSON history file 
    using a safe read-modify-write pattern.
    
    :param event_description: The original text description of the event.
    :param extracted_themes: The categories found by event_analyzer.py
    :param conversation_starters: The generated icebreakers from topic_generator.py
    :return: True if successfully logged, False otherwise.
    """
    # 1. Build the new data dictionary structure
    new_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(), # Standard ISO-formatted timestamp
        "event_description": event_description,
        "extracted_themes": extracted_themes,
        "conversation_starters": conversation_starters
    }

    try:
        # 2. Ensure the parent directory ('storage') exists before writing files
        HISTORY_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        # 3. Read-Modify-Write Pattern: Load existing history first
        history = load_history()
        
        # 4. Append the new log entry
        history.append(new_entry)
        
        # creating a temp file to write the updated history before replacing the original file
        temp_file = HISTORY_FILE_PATH.with_suffix(".json.tmp")

        # 5. Write the entire updated list to the temporary file first
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4, ensure_ascii=False)
            
        # 6. Atomically replace the old file with the new one
        # This OS-level operation is near-instantaneous. If the app closes before this line,
        # your old history remains perfectly safe.
        os.replace(temp_file, HISTORY_FILE_PATH)
        
        
        
        logger.info("Successfully logged conversation session to history.")
        return True

    except Exception as e:
        logger.error(f"Critical error writing to history log: {str(e)}")
        return False


# ==========================================
# EXAMPLE USAGE (For testing purposes)
# ==========================================
if __name__ == "__main__":
    print("\n--- Testing History Logger ---")
    
    # Mocking a session lifecycle output from your previous components
    mock_desc = "Networking summit for green energy startups in Jaipur."
    mock_themes = ["sustainability", "education"]
    mock_starters = [
        "Hey, are you currently working on any projects involving clean energy?",
        "What got you interested in attending the tech talks today?"
    ]
    
    # Test Logging
    print("Saving a new conversation session...")
    success = log_conversation(mock_desc, mock_themes, mock_starters)
    print(f"Log Status: {'SUCCESS' if success else 'FAILED'}\n")
    
    # Test Loading
    print("Reading past interactions from file...")
    saved_history = load_history()
    print(f"Total Saved Sessions: {len(saved_history)}")
    print(json.dumps(saved_history[-1], indent=2)) # Print out the most recent entry