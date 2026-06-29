import logging
import re
from typing import List
from transformers import pipeline, set_seed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# MODULE-LEVEL INITIALIZATION & SEEDING
# ==========================================
# Fixing the random seed ensures consistent, reproducible results for debugging
logger.info("Setting random seed to 42 for reproducibility.")
set_seed(42)

logger.info("Initializing GPT-2 text generation pipeline...")
try:
    # Loading the standard GPT-2 model into memory once at startup
    conversation_generator = pipeline(
        "text-generation", 
        model="gpt2"
    )
    logger.info("GPT-2 pipeline successfully loaded into memory.")
except Exception as e:
    logger.error(f"Failed to load the GPT-2 pipeline: {str(e)}")
    raise e


# ==========================================
# FUNCTIONAL CALL
# ==========================================
def generate_topics(extracted_themes: List[str], user_interests: List[str]) -> List[str]:
    """
    Constructs a prompt from themes and interests, generates raw text using GPT-2,
    and cleans/formats the output into 3 distinct conversation starters.
    """
    if not extracted_themes and not user_interests:
        return [
            "What brings you to this event today?",
            "Have you heard any interesting speakers so far?",
            "What projects are you currently working on?"
        ]

    themes_str = ", ".join(extracted_themes)
    interests_str = ", ".join(user_interests)
    
    # Clean, direct narrative prompt
    prompt = (
        f"Event Topics: {themes_str}. My Interests: {interests_str}.\n"
        "Here are 3 unique, practical conversation starters to break the ice:\n"
        "1."
    )

    try:
        logger.info("Generating raw conversation text from GPT-2...")
        
        # Enhanced parameters to fix text quality and clear warnings
        raw_outputs = conversation_generator(
            prompt, 
            max_new_tokens=60,         # Controls exact number of newly generated words
            do_sample=True,            # Enables creative sampling instead of rigid guessing
            temperature=0.8,           # Adds a balance of creativity and structure (0.7-0.9 is ideal)
            top_k=50,                  # Keeps the words focused on top probabilities
            repetition_penalty=1.2,    # STRICTLY prevents the model from repeating words/phrases
            pad_token_id=50256,
            clean_up_tokenization_spaces=False  # Silences the BPE tokenizer warning
        )
        
        raw_text = raw_outputs[0]["generated_text"]
        generated_part = raw_text[len(prompt):]
        
        # Split by newlines or sentence endings to capture independent clean lines
        lines = re.split(r'\n|\d\.', generated_part)
        
        clean_starters = []
        for line in lines:
            cleaned = re.sub(r"^[\s\d\.\-\*•]+", "", line).strip()
            
            # Ensure it looks like a meaningful phrase and isn't just a fragment
            if cleaned and len(cleaned) > 15 and (cleaned.endswith('?') or cleaned.endswith('.')):
                clean_starters.append(cleaned)
            
            if len(clean_starters) == 3:
                break

        # Fallback strings if GPT-2 output cuts off awkwardly
        fallbacks = [
            f"Hey, are you working on anything interesting related to {extracted_themes[0]}?",
            f"What got you interested in studying {user_interests[0] if user_interests else 'this field'}?",
            f"Are there any specific sessions or trends in {themes_str} you are following today?"
        ]
        
        while len(clean_starters) < 3:
            clean_starters.append(fallbacks[len(clean_starters)])

        return clean_starters[:3]

    except Exception as e:
        logger.error(f"Error during conversation generation: {str(e)}")
        return [
            "What brings you to this event today?",
            "How do you think the core topics of this event will affect the industry next year?",
            "Are there any specific sessions or people you're hoping to connect with?"
        ]

# ==========================================
# EXAMPLE USAGE (For testing purposes)
# ==========================================
if __name__ == "__main__":
    # Simulating data that would come out of your event_analyzer.py and user profile
    sample_themes = ["AI", "sustainability"]
    sample_interests = ["Software Engineering", "Renewable Energy"]
    
    print("\n--- Running Conversation Generator ---")
    starters = generate_topics(sample_themes, sample_interests)
    
    print("\nGenerated Conversation Starters:")
    for i, starter in enumerate(starters, 1):
        print(f"{i}. {starter}")