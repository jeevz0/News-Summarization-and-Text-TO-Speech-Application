from fastapi import FastAPI
from pydantic import BaseModel
import time
from gtts import gTTS
from googletrans import Translator
from typing import Dict, Any
from news_scraping import process_news, comparative_analysis, final_summary  # Import backend functions

# Initialize the FastAPI application
app = FastAPI()

# Define the request model for the `/fetch_news/` endpoint
class NewsRequest(BaseModel):
    company: str  # The company name for which news articles will be fetched

@app.get("/")
def home():
    """Home endpoint to check if the API is running."""
    return {"message": "News Summarization and Sentiment Analysis API is running!"}

@app.post("/fetch_news/")
def fetch_news(data: NewsRequest):
    """
    Fetch news articles, analyze sentiment, and generate summaries.
    
    Args:
        data (NewsRequest): The request body containing the company name.
    
    Returns:
        dict: A dictionary containing fetched articles, comparative analysis, 
              and summaries in English and Hindi.
    """
    company = data.company  # Extract the company name from the request
    news_data = process_news(company)  # Fetch news articles
    
    if not news_data:
        # Return an error message if no articles are found
        return {"error": "No news articles found."}
    
    # Perform comparative analysis and generate summaries
    analysis = comparative_analysis(news_data)
    final_summ = final_summary(news_data, company)

    # Prepare the output response
    output = {
        "company": company,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),  # Current timestamp
        "articles": news_data,  # List of fetched articles
        "comparative_analysis": analysis,  # Sentiment and topic analysis
        "final_summary": final_summ["text_summary"],  # Final summary in English
        "hindi_summary": final_summ["hindi_summary"]  # Final summary in Hindi
    }

    return output  # Return the response as JSON

@app.get("/generate_tts/")
def generate_tts(text: str):
    """
    Generate Hindi Text-to-Speech (TTS) from the given text.
    
    Args:
        text (str): The input text to be converted to Hindi TTS.
    
    Returns:
        dict: A dictionary containing the translated Hindi text and the audio file name.
    """
    try:
        # Translate the input text to Hindi
        translator = Translator()
        hindi_text = translator.translate(text, dest='hi').text

        # Generate TTS audio from the Hindi text
        tts = gTTS(text=hindi_text, lang='hi')
        audio_filename = f"summary_{time.strftime('%Y%m%d_%H%M%S')}.mp3"  # Unique filename
        tts.save(audio_filename)  # Save the audio file

        # Return the Hindi text and audio file name
        return {"hindi_text": hindi_text, "audio_file": audio_filename}
    except Exception as e:
        # Handle any errors during translation or TTS generation
        return {"error": str(e)}
