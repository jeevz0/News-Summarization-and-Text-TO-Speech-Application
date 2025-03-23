# News Summarization & Sentiment Analysis Tool Documentation

## 1. Project Setup
### Prerequisites
- Python 3.8+
- virtual environment (recommended)
- Required libraries: 
```bash
pip install streamlit fastapi requests beautifulsoup4 pandas numpy textblob gtts googletrans-core httpx
```

### Installation & Execution
1. **Clone the repository** (if applicable) or place all files in a working directory.
2. **Set up a virtual environment** (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```
*This creates an isolated Python environment to avoid conflicts with other projects and system packages. The activate script loads this environment into your current terminal session.*

3. **Run the API**:
```bash
uvicorn api:app --reload
```
*This starts the FastAPI server with auto-reload enabled, which automatically restarts the server when code changes are detected. The API will be available at http://127.0.0.1:8000.*

4. **Run the Streamlit frontend**:
```bash
streamlit run app.py
```
*This launches the Streamlit web interface, which provides an interactive UI for the application. It will automatically open in your default browser, typically at http://localhost:8501.*

## 2. Model Details
### **Sentiment Analysis Implementation**
The sentiment analysis uses a hybrid approach combining:

#### **TextBlob - A primary NLP library used for base sentiment analysis:**
```python
analysis = TextBlob(text)
polarity = analysis.sentiment.polarity
subjectivity = analysis.sentiment.subjectivity
```
*TextBlob provides a simple API for common natural language processing tasks. The sentiment property returns polarity (negative to positive, -1.0 to 1.0) and subjectivity (objective to subjective, 0.0 to 1.0) scores for the given text.*

#### **Custom Lexicon-Based Analysis - The code supplements TextBlob with domain-specific lexicons:**
- Predefined sets of positive and negative terms specific to business/financial news.
- Separate weighted scoring for terms appearing in titles vs. body text.

```python
# Enhanced positive and negative term lists with context
positive_terms = {
    'growth', 'profit', 'success', 'innovation', 'launch', 'partnership',
    'achievement', 'record', 'breakthrough', 'leading', 'expansion', 'improvement',
    'strong', 'positive', 'rise', 'up', 'gain', 'boost', 'exceed', 'beat',
    'opportunity', 'advance', 'milestone', 'award', 'celebrate', 'strengthen',
    'surpass', 'outperform', 'win', 'best', 'excellent', 'superior', 'promising'
}

negative_terms = {
    'challenge', 'controversy', 'problem', 'issue', 'decline', 'drop', 'loss',
    'debt', 'crisis', 'risk', 'trouble', 'fail', 'poor', 'weak', 'worse',
    'criticism', 'dispute', 'lawsuit', 'scandal', 'investigation', 'concern',
    'threat', 'pressure', 'violation', 'penalty', 'fine', 'warning', 'struggle',
    'crash', 'bankruptcy', 'layoff', 'downgrade', 'recall', 'deficit', 'bearish'
}
```
*These custom lexicons contain domain-specific terms for financial news that might not be captured by general sentiment analysis. The use of sets enables efficient O(1) lookups when checking if a term appears in the text.*

#### **Weighted Scoring System - The final sentiment score combines multiple signals:**
```python
sentiment_score = (
    polarity * 0.4 +  # TextBlob sentiment (40% weight)
    (pos_count - neg_count) * 0.3 +  # Overall term frequency (30% weight)
    (title_pos - title_neg) * 0.3  # Title sentiment (30% weight)
)
```
*This weighted approach balances general sentiment with domain-specific term frequency. The title is given special weight (30%) because headlines often strongly influence the overall sentiment of news articles.*

#### **Confidence Calculation**
```python
confidence = (abs(sentiment_score) + (1 - subjectivity) + abs(pos_count - neg_count)/10) / 3
```
*This combines the strength of the sentiment score, the objectivity of the text, and the term frequency differential to estimate confidence. Higher absolute sentiment scores, more objective text, and clearer term frequency differences all contribute to higher confidence.*

### **Complete Sentiment Analysis Function**
```python
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    # Enhanced positive and negative term lists with context
    positive_terms = {
        'growth', 'profit', 'success', 'innovation', 'launch', 'partnership',
        'achievement', 'record', 'breakthrough', 'leading', 'expansion', 'improvement',
        'strong', 'positive', 'rise', 'up', 'gain', 'boost', 'exceed', 'beat',
        'opportunity', 'advance', 'milestone', 'award', 'celebrate', 'strengthen',
        'surpass', 'outperform', 'win', 'best', 'excellent', 'superior', 'promising'
    }
    
    negative_terms = {
        'challenge', 'controversy', 'problem', 'issue', 'decline', 'drop', 'loss',
        'debt', 'crisis', 'risk', 'trouble', 'fail', 'poor', 'weak', 'worse',
        'criticism', 'dispute', 'lawsuit', 'scandal', 'investigation', 'concern',
        'threat', 'pressure', 'violation', 'penalty', 'fine', 'warning', 'struggle',
        'crash', 'bankruptcy', 'layoff', 'downgrade', 'recall', 'deficit', 'bearish'
    }
    
    text_lower = text.lower()
    title_words = ' '.join(text_lower.split()[:20])  # Consider title and first few words more heavily
    
    pos_count = sum(1 for term in positive_terms if term in text_lower)
    neg_count = sum(1 for term in negative_terms if term in text_lower)
    title_pos = sum(1 for term in positive_terms if term in title_words)
    title_neg = sum(1 for term in negative_terms if term in title_words)
    
    # Weighted scoring system
    sentiment_score = (
        polarity * 0.4 +  # TextBlob sentiment
        (pos_count - neg_count) * 0.3 +  # Overall term frequency
        (title_pos - title_neg) * 0.3  # Title sentiment
    )
    
    # Determine sentiment with adjusted thresholds
    if sentiment_score > 0.1 or (pos_count > neg_count * 1.5):
        sentiment = "Positive"
    elif sentiment_score < -0.1 or (neg_count > pos_count):
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    
    confidence = (abs(sentiment_score) + (1 - subjectivity) + abs(pos_count - neg_count)/10) / 3
    return {"sentiment": sentiment, "confidence": f"{confidence:.2f}"}
```
*This comprehensive function combines TextBlob's general sentiment analysis with custom financial news lexicons. It applies different weights to different signals and includes specific thresholds to determine the final sentiment classification. The confidence score provides an estimate of how reliable the sentiment classification is.*

### **Summarization Implementation**
The text summarization uses an extractive approach rather than an abstractive model:

#### **Sentence Extraction - The code splits text into sentences and extracts the first two sentences as the summary:**
```python
def summarize_text(text):
    try:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) >= 2:
            main_points = sentences[:2]
            summary = ' '.join(main_points)
            return summary.strip() if len(summary) <= 200 else sentences[0].strip()
        return text[:200].strip() + "..."
    except Exception as e:
        print(f"Error in summarization: {e}")
        return text[:200].strip() + "..."
```
*This function uses regular expressions to split text into sentences at punctuation followed by whitespace. It extracts the first two sentences as they typically contain the most important information in news articles. If the resulting summary exceeds 200 characters, it falls back to just the first sentence, with a character limit fallback for error cases.*

### **Text-to-Speech Implementation**
The TTS functionality uses Google's gTTS (Google Text-to-Speech) API:
```python
def create_audio_summary(summary):
    try:
        translator = Translator()
        hindi_summary = translator.translate(summary, dest='hi').text
        
        # Create audio file
        tts = gTTS(text=hindi_summary, lang='hi')
        audio_filename = f"summary_{time.strftime('%Y%m%d_%H%M%S')}.mp3"
        tts.save(audio_filename)
        
        return {
            "hindi_summary": hindi_summary,
            "audio_file": audio_filename
        }
    except Exception as e:
        print(f"Error creating audio summary: {e}")
        return {
            "hindi_summary": None,
            "audio_file": None
        }
```
*This function first translates the English summary to Hindi using Google Translate. It then uses Google's Text-to-Speech service to convert the Hindi text into spoken audio. The resulting MP3 file is saved with a timestamp-based filename to prevent overwriting previous files.*

### **Additional Model-Related Components**
#### **Keyword Extraction - A frequency-based approach with stopword filtering:**
```python
def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "about", "into", "over", "after", "this", "that", "these", "those", "has", "was", "said", "says", "will", "would", "could", "should", "may", "might", "must", "can"}
    words = [word for word in words if word not in stop_words and len(word) > 3]
    return [word for word, count in Counter(words).most_common(5)]
```
*This function extracts keywords from text using a simple but effective approach. It first finds all word tokens using regex, then filters out common stopwords and short words (3 characters or less). Finally, it uses Counter to identify the most frequent remaining words, returning the top 5 as keywords.*

#### **News Fetching Implementation**
```python
def search_news(company):
    search_engines = [
        f"https://www.bing.com/news/search?q={urllib.parse.quote(company)}+news",
        f"https://www.bing.com/news/search?q={urllib.parse.quote(company)}+latest",
        f"https://news.google.com/search?q={urllib.parse.quote(company)}+when:7d",
        f"https://duckduckgo.com/html/?q={urllib.parse.quote(company)}+news",
        f"https://duckduckgo.com/html/?q={urllib.parse.quote(company)}+latest+news",
        f"https://www.bing.com/news/search?q={urllib.parse.quote(company)}+business"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    links = set()
    
    for search_url in search_engines:
        try:
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if 'bing.com' in search_url:
                for article in soup.select('.news-card, .newsitem'):
                    link = article.select_one('a[href^="http"]')
                    if link and 'microsoft' not in link['href']:
                        links.add(link['href'])
            
            elif 'news.google.com' in search_url:
                for article in soup.select('article'):
                    for link in article.select('a[href^="./article"]'):
                        real_link = f"https://news.google.com{link['href'][1:]}"
                        links.add(real_link)
            
            elif 'duckduckgo.com' in search_url:
                for result in soup.select('.result'):
                    link = result.select_one('a[href^="http"]')
                    if link:
                        links.add(link['href'])
            
            if len(links) >= 30:
                break
                
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching news from {search_url}: {e}")
            continue
    
    excluded_domains = {'twitter.com', 'facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com'}
    valid_links = [link for link in links if not any(domain in link.lower() for domain in excluded_domains)]
    
    return valid_links[:15]
```
*This function searches multiple news sources (Bing, Google News, DuckDuckGo) to find recent articles about a company. It uses different search patterns to maximize coverage and employs custom parsing logic for each search engine. The code includes user-agent spoofing to avoid being blocked, filters out social media links, and limits results to 15 articles to manage processing time.*

#### **Final Summary Generation**
```python
def final_summary(articles, company_name):
    if not articles:
        return "No articles available for summary."
    
    # Analyze sentiments
    sentiments = [article['sentiment'] for article in articles]
    pos_count = sentiments.count("Positive")
    neg_count = sentiments.count("Negative")
    total = len(articles)
    
    # Get key topics
    all_keywords = []
    for article in articles:
        all_keywords.extend(article['keywords'])
    main_topics = [topic for topic, _ in Counter(all_keywords).most_common(3)]
    
    # Generate comprehensive summary
    summary = f"Analysis of {total} recent articles shows {pos_count} positive and {neg_count} negative articles. "
    
    if pos_count > neg_count:
        summary += f"{company_name}'s latest news coverage is mostly positive ({(pos_count/total*100):.1f}%). "
        summary += "Market sentiment appears favorable, suggesting potential growth. The company continues to establish a strong market presence, gaining positive public attention and maintaining steady growth. With a solid customer base and strategic innovations, the company remains competitive and relevant in its industry. Recent developments, partnerships, or product launches have contributed to its sustained success. Market analysts and consumers alike recognize its value, reinforcing confidence in its brand and future prospects."
    elif neg_count > pos_count:
        summary += f"{company_name}'s recent coverage leans negative ({(neg_count/total*100):.1f}%). "
        summary += "It is experiencing difficulties, facing negative public attention due to recent setbacks. Concerns from customers, investors, or industry analysts suggest potential instability, and the company may need to take corrective measures to regain confidence. Ongoing controversies, financial struggles, or leadership changes could further affect its market position."
    else:
        summary += "Coverage shows balanced sentiment. "
    
    summary += f"Key topics discussed: {', '.join(main_topics)}. "
    summary += "Market implications depend on how these developments unfold."
    
    return summary
```
*This function generates a comprehensive summary of all analyzed news articles about a company. It counts positive and negative articles, identifies the main topics across all articles using keyword frequency, and generates different summary text based on the overall sentiment distribution. The summary includes the ratio of positive to negative articles, key topics, and contextual interpretation of the sentiment trends.*

## 3. API Development
The backend API is developed using **FastAPI**.

### FastAPI Implementation
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
from news_analyzer import process_news, comparative_analysis, final_summary
from tts_generator import create_audio_summary

app = FastAPI(title="News Summarization API")

class CompanyRequest(BaseModel):
    company: str

class TTSRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "News Summarization and Sentiment Analysis API is running!"}

@app.post("/fetch_news/")
def fetch_news(request: CompanyRequest):
    try:
        company = request.company
        news_data = process_news(company)
        
        if not news_data:
            raise HTTPException(status_code=404, detail="No news articles found for this company")
            
        analysis = comparative_analysis(news_data)
        summary_text = final_summary(news_data, company)
        
        # Generate Hindi summary and audio
        tts_result = create_audio_summary(summary_text)
        
        output = {
            "company": company,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "articles": news_data,
            "comparative_analysis": analysis,
            "final_summary": summary_text,
            "hindi_summary": tts_result["hindi_summary"]
        }
        
        return output
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/generate_tts/")
def generate_tts(text: str):
    try:
        result = create_audio_summary(text)
        if not result["audio_file"]:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
```
*This FastAPI implementation creates a RESTful API with two main endpoints: one for fetching and analyzing news, and another for generating text-to-speech audio. It uses Pydantic models for request validation and provides detailed error handling. The `/fetch_news/` endpoint processes a company name, retrieves articles, analyzes sentiment, and returns a comprehensive response including summaries and analysis.*

### Streamlit Frontend Implementation
```python
import streamlit as st
import requests
import json
import pandas as pd
import time
import base64

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="News Analyzer & Summarizer",
    page_icon="📰",
    layout="wide"
)

st.title("News Summarization & Sentiment Analysis")

with st.sidebar:
    st.header("Search Options")
    company_name = st.text_input("Enter Company Name")
    search_btn = st.button("Analyze News")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool analyzes recent news about a company, 
    performs sentiment analysis, and generates a summary 
    in both English and Hindi with audio narration.
    """)

if search_btn and company_name:
    with st.spinner(f"Fetching and analyzing news for {company_name}..."):
        try:
            response = requests.post(
                f"{API_URL}/fetch_news/",
                json={"company": company_name},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Display summary
                st.header("News Analysis Summary")
                st.markdown(f"**{data['final_summary']}**")
                
                # Display audio
                if data.get("hindi_summary"):
                    st.subheader("Hindi Summary")
                    st.markdown(data["hindi_summary"])
                    
                    # Request audio file
                    audio_response = requests.get(
                        f"{API_URL}/generate_tts/?text={data['final_summary']}"
                    )
                    if audio_response.status_code == 200:
                        audio_data = audio_response.json()
                        audio_file = audio_data.get("audio_file")
                        if audio_file:
                            st.audio(f"{API_URL}/audio/{audio_file}")
                
                # Display articles
                st.header("Articles Found")
                articles_df = pd.DataFrame([
                    {
                        "Title": article["title"],
                        "Source": article["source"],
                        "Sentiment": article["sentiment"],
                        "Confidence": article["confidence"]
                    }
                    for article in data["articles"]
                ])
                st.dataframe(articles_df)
                
                # Display sentiment distribution
                st.subheader("Sentiment Distribution")
                sentiment_data = data["comparative_analysis"]["sentiment_distribution"]
                sentiment_df = pd.DataFrame({
                    "Sentiment": list(sentiment_data.keys()),
                    "Percentage": [float(p.strip('%')) for p in sentiment_data.values()]
                })
                st.bar_chart(sentiment_df.set_index("Sentiment"))
                
                # Display topic analysis
                st.subheader("Topic Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Common Topics")
                    common_topics = data["comparative_analysis"]["topic_overlap"]["common_topics"]
                    if common_topics:
                        for topic in common_topics:
                            st.markdown(f"- {topic}")
                    else:
                        st.markdown("No common topics found")
                
                with col2:
                    st.markdown("### Unique Topics")
                    unique_topics = data["comparative_analysis"]["topic_overlap"]["unique_topics"]
                    if unique_topics:
                        for topic in unique_topics:
                            st.markdown(f"- {topic}")
                    else:
                        st.markdown("No unique topics found")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Default content when no search is performed
if not search_btn or not company_name:
    st.info("Enter a company name and click 'Analyze News' to get started.")
    st.markdown("""
    ## How It Works
    1. Enter a company name in the sidebar
    2. Our system searches for recent news articles
    3. Articles are analyzed for sentiment and key topics
    4. A comprehensive summary is generated
    5. The summary is translated to Hindi with audio narration
    
    ## Features
    - Multi-source news aggregation
    - Sentiment analysis with confidence scoring
    - Topic extraction and comparison
    - Text-to-speech in Hindi
    """)
```
*This Streamlit implementation creates an interactive web interface for the news analysis system. It features a sidebar for input controls, a spinner for loading states, and multiple visualization components. When a company name is submitted, it calls the FastAPI backend, then displays the results in multiple sections: a text summary, Hindi translation with audio playback, a table of articles with sentiment, interactive charts for sentiment distribution, and topic analysis presented in a two-column layout.*

## 4. API Usage
### Using Postman
1. Open Postman and create a new request.
2. Set request type to `POST` and enter `http://127.0.0.1:8000/fetch_news/`.
3. In the **Body** tab, select **raw** and set the format to JSON.
4. Enter the request JSON:
```json
{
  "company": "Tesla"
}
```
*This setup configures a POST request to your local FastAPI server with a JSON payload containing the company name. Postman provides a UI-based approach to test APIs and inspect responses.*

5. Click **Send** and review the response.

### Using cURL
```bash
curl -X POST "http://127.0.0.1:8000/fetch_news/" \
     -H "Content-Type: application/json" \
     -d '{"company":"Tesla"}'
```
*This cURL command makes the same request from a command line interface. The -X flag specifies the HTTP method, -H adds the Content-Type header, and -d provides the JSON data payload. This approach is useful for scripting and automation.*

## 5. Assumptions & Limitations
### Assumptions
- News sources provide reliable and updated information.
- Google Translate provides an accurate Hindi translation.
- Sentiment analysis based on TextBlob may not capture all nuances.

### Limitations
- **News Scraping Issues:** Some news sources may block automated requests.
- **Translation Accuracy:** Google Translate is not 100% accurate.
- **TTS Quality:** Generated Hindi audio might lack natural intonations.
- **Google Blocks Scraping:** Google and other search engines may block scraping attempts, leading to incomplete data retrieval.
- **Time Consumption:** Obtaining and processing news articles takes some time, especially when fetching multiple sources.
- **Web App Deployment Issues:** Couldn't implement the web app using Ngrok as its servers were down.
- **Free Domain Integration Challenges:** Other free domains were difficult to integrate properly, making public hosting problematic.
