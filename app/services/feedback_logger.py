# app/services/feedback_logger.py

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Explicit path mapping relative to this directory, saving to 'feedback.json' in your project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FEEDBACK_FILE = Path(__file__).resolve().parent.parent.parent / "storage" / "feedback.json"

def load_feedback() -> list:
    """
    Reads the existing feedback logs from disk. Returns an empty list 
    if the file does not exist or is corrupted.
    """
    if not FEEDBACK_FILE.exists():
        return []
        
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:  
                return []
            return json.loads(content)
            
    except (json.JSONDecodeError, IOError) as e:
        print(f"WARNING: feedback.json is unreadable ({str(e)}). Fallback to empty list.")
        return []


def log_feedback(suggestion_text: str, action: str) -> bool:
    """
    Logs a user's thumbs-up or thumbs-down action on a specific conversation starter.
    
    :param suggestion_text: The exact conversation starter text string.
    :param action: Either 'like' or 'dislike' based on UI interaction.
    :return: True if successfully logged, False otherwise.
    """
    # Defensive validation: Ensure action is strictly limited to like or dislike
    if action not in ["like", "dislike"]:
        print(f"ERROR: Invalid feedback action received: '{action}'. Must be 'like' or 'dislike'.")
        return False

    # 1. Build the structured data entry
    new_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "suggestion_text": suggestion_text.strip(),
        "action": action
    }
    
    # 2. Load existing data array
    feedback_list = load_feedback()
    feedback_list.append(new_entry)
    
    # 3. Ensure target directory exists
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 4. Atomic Write Sequence to prevent file corruption
    temp_file = FEEDBACK_FILE.with_suffix(".json.tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, indent=2, ensure_ascii=False)
            
        os.replace(temp_file, FEEDBACK_FILE)
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to save user feedback atomically: {str(e)}")
        if temp_file.exists():
            temp_file.unlink()
        return False


# ==========================================
# EXAMPLE USAGE (For testing purposes)
# ==========================================
if __name__ == "__main__":
    print("\n--- Testing Feedback Logger ---")
    
    # Simulating a user clicking Thumbs Up on a generator suggestion
    sample_suggestion = "Hey, are you currently working on any projects involving clean energy?"
    
    print("Logging a 'like' action...")
    success = log_feedback(sample_suggestion, "like")
    print(f"Log Status: {'SUCCESS' if success else 'FAILED'}\n")
    
    # Print out results
    current_feedback = load_feedback()
    print(f"Total Feedback Records: {len(current_feedback)}")
    print(json.dumps(current_feedback[-1], indent=2))