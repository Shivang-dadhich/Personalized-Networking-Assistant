import logging
from typing import List, Optional
from transformers import pipeline
import re

# Configure logging to monitor model loading
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# MODULE-LEVEL INITIALIZATION (Eager Loading)
# ==========================================
# This code executes EXACTLY ONCE when the module is first imported.
# It loads the model into memory so subsequent requests are fast.
logger.info("Initializing DistilBERT zero-shot classification pipeline...")

try:
    # Using 'valhalla/distilbart-mnli-12-1' or 'typeform/distilbert-base-uncased-mnli' 
    # as the highly optimized DistilBERT-based zero-shot model.
    theme_classifier = pipeline(
        "zero-shot-classification", 
        model="typeform/distilbert-base-uncased-mnli"
    )
    logger.info("DistilBERT pipeline successfully loaded into memory.")
except Exception as e:
    logger.error(f"Failed to load the model pipeline: {str(e)}")
    raise e


# Assuming your pipeline is initialized (using the instruct model)
label_generator = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-360M-Instruct")

def generate_custom_labels(event_description: str) -> List[str]:
    """
    Uses SmolLM2 to dynamically extract 4 to 5 highly relevant, distinct
    industry macro-categories and domain labels from raw event text.
    """
    if not event_description.strip():
        return []

    # Direct system instruction optimizing label generation criteria
    prompt = (
        "<|im_start|>system\n"
        "You are an elite text analytics assistant. Your sole task is to analyze an event description "
        "and return exactly 4 to 5 distinct, highly-relevant, high-level industry or niche domain labels "
        "(e.g., 'Politics & Elections', 'Digital Marketing', 'Agricultural Tech', 'Governance'). "
        "Format the output strictly as a single line of labels separated by commas. "
        "Do not include numbers, bullet points, introductory remarks, or conversational headers.\n"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        f"Extract 4 to 5 specific labels for this event: {event_description}\n"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    
    try:
        outputs = label_generator(
            prompt, 
            max_new_tokens=60,      # INCREASED: Gives model space to output 5 clean phrases safely
            max_length=None,       
            generation_config=None, 
            do_sample=True,         # ENABLED: Allows the model to find varied, relatable terms
            temperature=0.3,        # LOW: Keeps results focused and highly analytical
            top_p=0.90,
            pad_token_id=0
        )
        
        raw_text = outputs[0]["generated_text"][len(prompt):].strip()
        logger.info(f"Raw Dynamic Labels Output: {raw_text}")
        
        # FIX: Split by newline first, then split by comma to handle both formats cleanly
        raw_lines = re.split(r"[\n,]+", raw_text)
        
        custom_labels = []
        for item in raw_lines:
            cleaned = item.strip()
            # Clean out numbers like "1.", "2)", "-", etc.
            cleaned = re.sub(r"^[\s\d\.\)\-\*•]+", "", cleaned).strip()
            
            # Capitalize each word properly (e.g., "bjp" -> "Bjp")
            cleaned = cleaned.title()
            
            # Now, a single label like "Political" or "Bjp" will pass beautifully
            if cleaned and len(cleaned) > 2 and len(cleaned) < 25:
                custom_labels.append(cleaned)
                
        return list(set(custom_labels))
        
    except Exception as e:
        logger.error(f"Error extracting labels dynamically: {str(e)}")
        return []
    
    

# ==========================================
# FUNCTIONAL CALL
# ==========================================
def extract_event_themes(event_description: str, candidate_labels: Optional[List[str]] = None) -> List[str]:
    """
    Analyzes an event description and extracts the top 3 relevant themes.
    
    :param event_description: The string text describing the event.
    :param candidate_labels: Optional list of strings to match against. 
                             Defaults to professional networking themes.
    :return: A list of the top 3 highest-scoring theme strings.
    """
    # 1. Fallback to default professional networking themes if none provided
    if not candidate_labels:
        #Broad universal taxonomy covering modern industries, tech domains, and events
        candidate_labels = [
            "AI & Machine Learning", "Software Development", "Cybersecurity", "Cloud Computing",
            "Blockchain & Web3", "Fintech & Finance", "Healthcare & Biotech", "Data Science",
            "Sustainability & Environment", "Agriculture & Farming", "Education Tech", 
            "E-commerce & Retail", "Sports & Entertainment", "Gaming & Animation", 
            "Hardware & IoT", "Marketing & Branding", "Social Networking", "Aerospace"
        ]
        
    #  Get custom labels dynamically from SmolLM2
    dynamic_labels = generate_custom_labels(event_description)
    
    #  Merge them with your original list (using a set to prevent duplicates)
    combined_labels = list(set(candidate_labels + dynamic_labels))
    
    # Validation check for empty text
    if not event_description.strip():
        logger.warning("Empty event description provided. Returning default top categories.")
        return candidate_labels[:3]

    try:
        # 2. Run the zero-shot classifier
        # multi_label=True allows topics to be scored independently
        result = theme_classifier(event_description, combined_labels, multi_label=True)
        
        # The Hugging Face pipeline automatically sorts 'labels' by their 'scores' in descending order.
        # We grab the top 3 labels directly from the sorted results.
        top_themes = result.get("labels", [])[:3]
        
        logger.info(f"Successfully extracted themes: {top_themes}")
        return top_themes

    except Exception as e:
        logger.error(f"Error during theme extraction: {str(e)}")
        # Graceful fallback to avoid breaking the application pipeline
        return candidate_labels[:3]


# ==========================================
# EXAMPLE USAGE (For testing purposes)
# ==========================================
if __name__ == "__main__":
    # Test case 1: Using default labels
    sample_desc_1 = (
        "Join us for an evening exploring how machine learning algorithms are being utilized "
        "to reduce carbon footprints in smart cities and promote green energy grids."
    )
    print("\n--- Test 1: Default Labels ---")
    print(f"Description: {sample_desc_1}")
    themes_1 = extract_event_themes(sample_desc_1)
    print(f"Extracted Themes: {themes_1}")

    # Test case 2: Using custom labels
    sample_desc_2 = (
        "A deep dive into decentralized finance, smart contract security audits, "
        "and how Web3 technologies are changing global banking protocols."
    )
    custom_labels = ["finance", "cybersecurity", "gaming", "art", "blockchain", "politics"]
    print("\n--- Test 2: Custom Labels ---")
    print(f"Description: {sample_desc_2}")
    themes_2 = extract_event_themes(sample_desc_2, candidate_labels=custom_labels)
    print(f"Extracted Themes: {themes_2}")