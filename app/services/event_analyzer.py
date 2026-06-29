import logging
from typing import List, Optional
from transformers import pipeline

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
        candidate_labels = ["AI", "healthcare", "blockchain", "education", "sustainability"]
    
    # Validation check for empty text
    if not event_description.strip():
        logger.warning("Empty event description provided. Returning default top categories.")
        return candidate_labels[:3]

    try:
        # 2. Run the zero-shot classifier
        # multi_label=True allows topics to be scored independently
        result = theme_classifier(event_description, candidate_labels, multi_label=True)
        
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