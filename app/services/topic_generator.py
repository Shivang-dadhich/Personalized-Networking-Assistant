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
    
    :param extracted_themes: Top themes from event_analyzer (e.g., ['AI', 'sustainability'])
    :param user_interests: The user's personal interests (e.g., ['coding', 'green tech'])
    :return: A list of 3 clean conversation starter strings.
    """
    if not extracted_themes and not user_interests:
        logger.warning("No themes or interests provided. Returning generic icebreakers.")
        return [
            "What brings you to this event today?",
            "Have you heard any interesting speakers so far?",
            "What projects are you currently working on?"
        ]

    # 1. Prompt Engineering: Create a narrative context to guide GPT-2
    themes_str = ", ".join(extracted_themes)
    interests_str = ", ".join(user_interests)
    
    # We guide the model by formatting the prompt as a pre-started list
    prompt = (
        f"I am attending a networking event focused on {themes_str}. "
        f"My professional interests are {interests_str}. "
        f"Here are 3 unique, engaging conversation starters I can use to talk to someone:\n"
        "1."
    )

    try:
        logger.info("Generating raw conversation text from GPT-2...")
        # 2. Run the generator with max_length restriction
        # pad_token_id handles end-of-text settings cleanly
        raw_outputs = conversation_generator(
            prompt, 
            max_length=110,  # Elevated slightly to accommodate the prompt length safely
            num_return_sequences=1,
            pad_token_id=50256  # Standard GPT-2 EOS token ID
        )
        
        raw_text = raw_outputs[0]["generated_text"]
        
        # 3. Post-Processing: Isolate the generated part and clean it up
        # Remove the prompt prefix so we only analyze what GPT-2 invented
        generated_part = raw_text[len(prompt):]
        
        # Split by newlines to break down the list items
        lines = generated_part.split("\n")
        
        clean_starters = []
        for line in lines:
            # Clean up leading numbers, bullet points, hyphens, and whitespace
            cleaned = re.sub(r"^[\s\d\.\-\*•]+", "", line).strip()
            
            # Ensure the line actually has meaningful text and isn't empty
            if cleaned and len(cleaned) > 10:
                clean_starters.append(cleaned)
            
            # Stop once we have our target 3 conversation starters
            if len(clean_starters) == 3:
                break

        # Fallback security check: if GPT-2 failed to generate clean lines, provide defaults
        while len(clean_starters) < 3:
            clean_starters.append(f"Hey! Are you working on anything related to {extracted_themes[0] if extracted_themes else 'tech'} lately?")

        logger.info("Successfully generated and cleaned conversation starters.")
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