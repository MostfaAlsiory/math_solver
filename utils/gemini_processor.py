import os
import logging
import requests
import json

logger = logging.getLogger(__name__)

# The endpoint for Google's Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"

def process_with_gemini(query_text):
    """
    Process the natural language query using Google Gemini AI
    and convert it to a format suitable for Wolfram Alpha
    
    Args:
        query_text (str): The natural language query provided by the user
        
    Returns:
        str: The processed query optimized for Wolfram Alpha, or None if processing fails
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY environment variable not set")
        return None
    
    try:
        logger.debug(f"Using Gemini API URL: {GEMINI_API_URL}")
        logger.debug(f"API Key available: {bool(GEMINI_API_KEY)}")
        
        # Prepare the prompt for Gemini
        prompt = f"""
        You are a scientific query processor. Your task is to convert the following natural language question 
        into a precise query that can be processed by Wolfram Alpha's computational engine.
        
        Focus on extracting the key scientific or mathematical concepts and reformulate them into clear, 
        direct syntax that Wolfram Alpha can understand.
        
        Original question: "{query_text}"
        
        Output ONLY the reformulated query for Wolfram Alpha, nothing else.
        """
        
        # Prepare the API request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Headers for the API request
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        # Make the API call
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        
        response_data = response.json()
        
        # Extract the processed query from the response
        if response.status_code == 200 and "candidates" in response_data:
            text_response = response_data["candidates"][0]["content"]["parts"][0]["text"]
            processed_query = text_response.strip()
            logger.debug(f"Original query: {query_text}")
            logger.debug(f"Processed query: {processed_query}")
            return processed_query
        else:
            logger.error(f"Error from Gemini API: {response_data}")
            return None
            
    except Exception as e:
        logger.error(f"Error processing query with Gemini: {e}")
        return None
