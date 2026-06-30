import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fact_check(query: str) -> str:
    """
    Queries the Wikipedia REST API to verify facts or fetch a quick summary text 
    about a specific topic or event concept.
    
    :param query: The search term or concept string to verify (e.g., "Machine Learning", "Blockchain").
    :return: A short text extract paragraph from Wikipedia, or a friendly fallback error string.
    """
    # Defensive Check: Ensure the query string isn't empty or blank spaces
    if not query or not query.strip():
        logger.warning("Empty query passed to fact_checker.")
        return "No verification topic was provided. Please specify a topic to search."

    # Clean the query string for URL safety
    cleaned_query = query.strip()
    
    # Using the Wikipedia REST API 'summary' endpoint which returns a clean, structured JSON 
    # response containing the first introductory paragraph of the closest matching article.
    # Format: https://en.wikipedia.org/api/rest_v1/page/summary/{title}
    api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{cleaned_query.replace(' ', '_')}"
    
    # Defining a clean user-agent header as requested by the Wikimedia API policy
    headers = {
        "User-Agent": "PersonalizedNetworkingAssistant/1.0 (backend service component)"
    }

    try:
        logger.info(f"Querying Wikipedia API for topic: '{cleaned_query}'")
        
        # Make the HTTP GET request with a strict timeout (e.g., 5 seconds) 
        # so the backend doesn't hang indefinitely if Wikipedia is slow.
        response = requests.get(api_url, headers=headers, timeout=5)
        
        # If the page isn't found (404) or something else went wrong, raise an HTTPError
        response.raise_for_status()
        
        # Parse the structured JSON response
        data: Dict[str, Any] = response.json()
        
        # Extract the pure text summary abstract
        extract = data.get("extract")
        
        if extract:
            logger.info("Successfully retrieved factual extract from Wikipedia.")
            return extract
        else:
            logger.warning(f"No text extract available in the JSON response for '{cleaned_query}'.")
            return f"Could not find a structured description for '{cleaned_query}' on Wikipedia."

    # Defensive Programming: Catching specific network/API failure states gracefully
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error while connecting to Wikipedia API for query '{cleaned_query}'.")
        return "Fact verification is temporarily unavailable because the knowledge server timed out."
        
    except requests.exceptions.HTTPError as http_err:
        status_code = response.status_code if 'response' in locals() else 'Unknown'
        logger.error(f"HTTP error occurred ({status_code}) for query '{cleaned_query}': {str(http_err)}")
        # Check if it was simply a missing page error
        if status_code == 404:
            return f"Sorry, no matching factual records were found for '{cleaned_query}'."
        return "An external data error occurred while verifying this topic."
        
    except requests.exceptions.RequestException as net_err:
        logger.error(f"Network request connection error for query '{cleaned_query}': {str(net_err)}")
        return "Network connection issue encountered. Unable to reach the fact-verification service right now."
        
    except ValueError as json_err:
        logger.error(f"Failed to parse JSON data from response for query '{cleaned_query}': {str(json_err)}")
        return "Received an invalid data payload format from the verification provider."
        
    except Exception as unexpected_err:
        logger.error(f"Unexpected systems failure inside fact_checker: {str(unexpected_err)}")
        return "An unexpected local component issue occurred during fact-checking."


# ==========================================
# EXAMPLE USAGE (For testing purposes)
# ==========================================
if __name__ == "__main__":
    print("\n--- Test 1: Successful Verification ---")
    topic_1 = "Artificial Intelligence"
    result_1 = fact_check(topic_1)
    print(f"Query: {topic_1}\nResult: {result_1}\n")

    print("--- Test 2: Another Successful Concept ---")
    topic_2 = "Sustainability"
    result_2 = fact_check(topic_2)
    print(f"Query: {topic_2}\nResult: {result_2}\n")

    print("--- Test 3: Handling Missing Pages (404 Error) ---")
    topic_3 = "NonExistentRandomWord12345"
    result_3 = fact_check(topic_3)
    print(f"Query: {topic_3}\nResult: {result_3}\n")