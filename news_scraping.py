import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import json
from collections import Counter
from textblob import TextBlob
import urllib.parse
from gtts import gTTS
from googletrans import Translator
import os

# Function to fetch content from a URL
def fetch_content(url):
    """
    Extract article content from a URL.
    
    Args:
        url (str): The URL to fetch content from
        
    Returns:
        str: The extracted text content from the article
    """
    # Set user agent to mimic browser behavior
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # Send request and get response
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to locate main article content using common patterns
        article_content = soup.find('article') or soup.find(class_=re.compile(r'article|content|story'))
        
        # Extract paragraphs from article or fallback to all paragraphs if article not found
        paragraphs = article_content.find_all('p') if article_content else soup.find_all('p')
        
        # Join all paragraph text into a single string
        content = ' '.join([para.get_text().strip() for para in paragraphs if para.get_text().strip()])
        return content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

# Function to analyze sentiment of text
def analyze_sentiment(text):
    """
    Perform sentiment analysis on the given text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: Dictionary containing sentiment classification and confidence score
    """
    # Use TextBlob for initial sentiment analysis
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    # Define financial/business-specific positive terms
    positive_terms = {
        'growth', 'profit', 'success', 'innovation', 'launch', 'partnership',
        'achievement', 'record', 'breakthrough', 'leading', 'expansion', 'improvement',
        'strong', 'positive', 'rise', 'up', 'gain', 'boost', 'exceed', 'beat',
        'opportunity', 'advance', 'milestone', 'award', 'celebrate', 'strengthen',
        'surpass', 'outperform', 'win', 'best', 'excellent', 'superior', 'promising'
    }
    
    # Define financial/business-specific negative terms
    negative_terms = {
        'challenge', 'controversy', 'problem', 'issue', 'decline', 'drop', 'loss',
        'debt', 'crisis', 'risk', 'trouble', 'fail', 'poor', 'weak', 'worse',
        'criticism', 'dispute', 'lawsuit', 'scandal', 'investigation', 'concern',
        'threat', 'pressure', 'violation', 'penalty', 'fine', 'warning', 'struggle',
        'crash', 'bankruptcy', 'layoff', 'downgrade', 'recall', 'deficit', 'bearish'
    }
    
    # Prepare text for analysis
    text_lower = text.lower()
    # Consider the first 20 words more heavily (likely title and opening)
    title_words = ' '.join(text_lower.split()[:20])  
    
    # Count occurrences of positive and negative terms
    pos_count = sum(1 for term in positive_terms if term in text_lower)
    neg_count = sum(1 for term in negative_terms if term in text_lower)
    title_pos = sum(1 for term in positive_terms if term in title_words)
    title_neg = sum(1 for term in negative_terms if term in title_words)
    
    # Calculate weighted sentiment score using multiple factors
    sentiment_score = (
        polarity * 0.4 +                # TextBlob sentiment weight
        (pos_count - neg_count) * 0.3 + # Overall term frequency weight
        (title_pos - title_neg) * 0.3   # Title sentiment weight
    )
    
    # Classify sentiment based on score and term frequency
    if sentiment_score > 0.1 or (pos_count > neg_count * 1.5):
        sentiment = "Positive"
    elif sentiment_score < -0.1 or (neg_count > pos_count):
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    
    # Calculate confidence score based on sentiment strength, subjectivity, and term frequency
    confidence = (abs(sentiment_score) + (1 - subjectivity) + abs(pos_count - neg_count)/10) / 3
    return {"sentiment": sentiment, "confidence": f"{confidence:.2f}"}

# Function to generate a summary from text
def summarize_text(text):
    """
    Create a brief summary of the given text.
    
    Args:
        text (str): The text to summarize
        
    Returns:
        str: A brief summary (first 1-2 sentences or first 200 chars)
    """
    try:
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Use first two sentences if available
        if len(sentences) >= 2:
            main_points = sentences[:2]
            summary = ' '.join(main_points)
            # Limit summary length to 200 characters or first sentence
            return summary.strip() if len(summary) <= 200 else sentences[0].strip()
        
        # Fallback to first 200 characters if less than 2 sentences
        return text[:200].strip() + "..."
    except Exception as e:
        print(f"Error in summarization: {e}")
        return text[:200].strip() + "..."

# Function to extract important keywords from text
def extract_keywords(text):
    """
    Extract key terms from the text after removing stopwords.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        list: Top 5 keywords from the text
    """
    # Extract words using regex
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Common English stopwords to filter out
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "about", "into", "over", "after", "this", "that", "these", "those", "has", "was", "said", "says", "will", "would", "could", "should", "may", "might", "must", "can"}
    
    # Filter out stopwords and short words
    words = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Return 5 most frequent words
    return [word for word, count in Counter(words).most_common(5)]

# Function to extract the title from HTML
def extract_title(soup, url):
    """
    Extract the article title from HTML.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        url (str): URL as fallback for title generation
        
    Returns:
        str: The extracted title
    """
    # Try to get title from HTML title tag
    title = soup.title.string if soup.title else None
    
    # If no title found, try h1 tag
    if not title:
        h1_tag = soup.find('h1')
        # If still no title, generate from URL
        title = h1_tag.get_text().strip() if h1_tag else url.split('/')[-1].replace('-', ' ').title()
    
    return title.strip()

# Function to search for news articles about a company
def search_news(company):
    """
    Search for recent news articles about the specified company.
    
    Args:
        company (str): The company name to search for
        
    Returns:
        list: List of article URLs
    """
    # Multiple search engines and queries for better coverage
    search_engines = [
        f"https://www.bing.com/news/search?q={urllib.parse.quote(company)}+news",
        f"https://www.bing.com/news/search?q={urllib.parse.quote(company)}+latest",
        f"https://news.google.com/search?q={urllib.parse.quote(company)}+when:7d",
        f"https://duckduckgo.com/html/?q={urllib.parse.quote(company)}+news",
        f"https://duckduckgo.com/html/?q={urllib.parse.quote(company)}+latest+news",
        f"https://www.bing.com/news/search?q={urllib.parse.quote(company)}+business"
    ]
    
    # Set browser-like headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    links = set()
    
    # Iterate through each search engine
    for search_url in search_engines:
        try:
            # Send request and get response
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract links based on the search engine's HTML structure
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
            
            # Stop if we have enough links
            if len(links) >= 30:
                break
                
            # Delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching news from {search_url}: {e}")
            continue
    
    # Filter out social media links
    excluded_domains = {'twitter.com', 'facebook.com', 'instagram.com', 'youtube.com', 'linkedin.com'}
    valid_links = [link for link in links if not any(domain in link.lower() for domain in excluded_domains)]
    
    # Return the top 15 links
    return valid_links[:15]

# Function to process a single URL and extract article data
def process_url(url):
    """
    Process a single news article URL to extract relevant information.
    
    Args:
        url (str): The article URL to process
        
    Returns:
        dict: Dictionary containing article data (title, summary, sentiment, etc.)
    """
    try:
        print(f"Processing: {url}")
        
        # Fetch the article content
        content = fetch_content(url)
        
        if content:
            # Get full HTML for title extraction
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract article metadata
            title = extract_title(soup, url)
            summary = summarize_text(content)
            keywords = extract_keywords(content)
            
            # Analyze sentiment (combining title and article beginning for better accuracy)
            sentiment_analysis = analyze_sentiment(title + " " + content[:500])
            
            # Return structured article data
            return {
                "title": title,
                "summary": summary,
                "link": url,
                "keywords": keywords,
                "sentiment": sentiment_analysis["sentiment"],
                "confidence": sentiment_analysis["confidence"],
                "source": urllib.parse.urlparse(url).netloc
            }
    except Exception as e:
        print(f"Error processing {url}: {e}")
    return None

# Function to process multiple news articles in parallel
def process_news(company):
    """
    Search for and process news articles about the company in parallel.
    
    Args:
        company (str): The company name to search for
        
    Returns:
        list: List of dictionaries containing processed article data
    """
    # Search for news articles
    links = search_news(company)
    
    # Process URLs in parallel using thread pool
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_url, links))
    
    # Filter out any failed processing attempts
    return [result for result in results if result]

# Function to perform comparative analysis of multiple articles
def comparative_analysis(articles):
    """
    Compare and analyze multiple articles to identify patterns and differences.
    
    Args:
        articles (list): List of processed article dictionaries
        
    Returns:
        dict: Dictionary containing comparative analysis results
    """
    if not articles:
        return {}
        
    # Calculate sentiment distribution statistics
    sentiments = [article['sentiment'] for article in articles]
    total = len(sentiments)
    sentiment_stats = {
        "positive": f"{sentiments.count('Positive') / total * 100:.2f}%",
        "negative": f"{sentiments.count('Negative') / total * 100:.2f}%",
        "neutral": f"{sentiments.count('Neutral') / total * 100:.2f}%"
    }
    
    # Analyze content differences between articles
    coverage_differences = []
    for i in range(len(articles)-1):
        for j in range(i+1, len(articles)):
            art1_topics = set(articles[i]['keywords'])
            art2_topics = set(articles[j]['keywords'])
            
            comparison = {
                "Comparison": f"Article {i+1} focuses on {', '.join(art1_topics - art2_topics)}, "
                            f"while Article {j+1} discusses {', '.join(art2_topics - art1_topics)}",
                "Impact": f"Different aspects affecting market perception: "
                         f"{articles[i]['sentiment']} vs {articles[j]['sentiment']} sentiment"
            }
            coverage_differences.append(comparison)
    
    # Analyze topic overlap across all articles
    all_topics = set()
    for article in articles:
        all_topics.update(article['keywords'])
    
    # Find common topics across all articles
    common_topics = set.intersection(*[set(article['keywords']) for article in articles])
    
    # Return structured analysis
    return {
        "sentiment_distribution": sentiment_stats,
        "coverage_differences": coverage_differences[:2],  # Limit to first 2 comparisons
        "topic_overlap": {
            "common_topics": list(common_topics),
            "unique_topics": list(all_topics - common_topics)
        }
    }

# Function to generate a final summary of all articles
def final_summary(articles, company_name):
    """
    Generate a comprehensive summary of all news articles.
    
    Args:
        articles (list): List of processed article dictionaries
        company_name (str): Name of the company
        
    Returns:
        dict: Dictionary containing text summary, Hindi translation, and audio file path
    """
    if not articles:
        return "No articles available for summary."
    
    # Analyze overall sentiment distribution
    sentiments = [article['sentiment'] for article in articles]
    pos_count = sentiments.count("Positive")
    neg_count = sentiments.count("Negative")
    total = len(articles)
    
    # Extract key topics from all articles
    all_keywords = []
    for article in articles:
        all_keywords.extend(article['keywords'])
    main_topics = [topic for topic, _ in Counter(all_keywords).most_common(3)]
    
    # Generate summary based on sentiment analysis
    summary = f"Analysis of {total} recent articles shows {pos_count} positive and {neg_count} negative articles. "
    
    # Add context based on overall sentiment
    if pos_count > neg_count:
        summary += f"{company_name}'s latest news coverage is mostly positive ({(pos_count/total*100):.1f}%). "
        summary += "Market sentiment appears favorable, suggesting potential growth, continues to establish a strong market presence, gaining positive public attention and maintaining steady growth. With a solid customer base and strategic innovations, the company remains competitive and relevant in its industry. Recent developments, partnerships, or product launches have contributed to its sustained success. Market analysts and consumers alike recognize its value, reinforcing confidence in its brand and future prospects."
    elif neg_count > pos_count:
        summary += f"{company_name}'s recent coverage leans negative ({(neg_count/total*100):.1f}%). "
        summary += "It is experiencing difficulties, facing negative public attention due to recent setbacks. Concerns from customers, investors, or industry analysts suggest potential instability, and the company may need to take corrective measures to regain confidence. Ongoing controversies, financial struggles, or leadership changes could further affect its market position. "
    else:
        summary += "Coverage shows balanced sentiment. "
    
    # Add key topics and conclusion
    summary += f"Key topics discussed: {', '.join(main_topics)}. "
    summary += "Market implications depend on how these developments unfold."
    
    try:
        # Translate summary to Hindi
        translator = Translator()
        hindi_summary = translator.translate(summary, dest='hi').text
        
        # Create audio file of Hindi summary
        tts = gTTS(text=hindi_summary, lang='hi')
        audio_filename = f"summary_{time.strftime('%Y%m%d_%H%M%S')}.mp3"
        tts.save(audio_filename)
        
        # Return all summary formats
        return {
            "text_summary": summary,
            "hindi_summary": hindi_summary,
            "audio_file": audio_filename
        }
    except Exception as e:
        print(f"Error creating audio summary: {e}")
        # Return text-only summary if translation/audio fails
        return {
            "text_summary": summary,
            "hindi_summary": None,
            "audio_file": None
        }

# Main function to execute the entire analysis
def main():
    """
    Main function to run the complete news analysis process.
    - Gets company name from user
    - Searches for and processes news
    - Performs analysis and generates summary
    - Outputs results to console and JSON file
    """
    try:
        # Get company name from user
        company = input("Enter Company Name: ")
        print("\nFetching news articles...\n")
        
        # Process news articles
        news_data = process_news(company)
        
        # Handle case where no articles are found
        if not news_data:
            print("No news articles found.")
            return
        
        # Perform analysis    
        analysis = comparative_analysis(news_data)
        final_summ = final_summary(news_data, company)
        
        # Create output structure
        output = {
            "company": company,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "articles": news_data,
            "comparative_analysis": analysis,
            "final_summary": final_summ["text_summary"],
            "hindi_summary": final_summ["hindi_summary"]
        }

        # Display JSON output
        print("\nJSON Output:")
        print("=" * 50)
        print(json.dumps(output, indent=2))
        
        # Display individual article details
        print("\nProcessed Articles:")
        print("=" * 100)
        for idx, article in enumerate(news_data, 1):
            print(f"\nArticle {idx}:")
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Link: {article['link']}")
            print(f"Summary: {article['summary']}")
            print(f"Keywords: {', '.join(article['keywords'])}")
            print(f"Sentiment: {article['sentiment']} (Confidence: {article['confidence']})")
            print("-" * 100)
        
        # Display comparative analysis
        print("\nComparative Analysis:")
        print("=" * 50)
        print(f"Total Articles: {len(news_data)}")
        for sentiment, percentage in analysis['sentiment_distribution'].items():
            print(f"{sentiment.title()}: {percentage}")
            
        print("\nCoverage Differences:")
        for diff in analysis['coverage_differences']:
            print(f"\nComparison: {diff['Comparison']}")
            print(f"Impact: {diff['Impact']}")
            
        print("\nTopic Analysis:")
        print(f"Common Topics: {', '.join(analysis['topic_overlap']['common_topics'])}")
        print(f"Unique Topics: {', '.join(analysis['topic_overlap']['unique_topics'])}")
        
        # Display final summary
        print("\nFinal Summary:")
        print("=" * 50)
        print(final_summ["text_summary"])
        
        # Display Hindi summary if available
        if final_summ["hindi_summary"]:
            print("\nहिंदी सारांश (Hindi Summary):")
            print("=" * 50)
            print(final_summ["hindi_summary"])
            print(f"\nAudio summary saved as: {final_summ['audio_file']}")
        
        # Save results to JSON file
        filename = f"news_analysis_{company.replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to: {filename}")
        
    except Exception as e:
        print(f"Error in main: {e}")

# Entry point of the script
if __name__ == "__main__":
    main()
