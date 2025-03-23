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

# Function to fetch content from a given URL
def fetch_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract article content
        article_content = soup.find('article') or soup.find(class_=re.compile(r'article|content|story'))
        paragraphs = article_content.find_all('p') if article_content else soup.find_all('p')
        content = ' '.join([para.get_text().strip() for para in paragraphs if para.get_text().strip()])
        return content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

# Function to analyze sentiment of a given text
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    # Define positive and negative terms
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
    
    # Calculate sentiment score
    text_lower = text.lower()
    title_words = ' '.join(text_lower.split()[:20])
    pos_count = sum(1 for term in positive_terms if term in text_lower)
    neg_count = sum(1 for term in negative_terms if term in text_lower)
    title_pos = sum(1 for term in positive_terms if term in title_words)
    title_neg = sum(1 for term in negative_terms if term in title_words)
    sentiment_score = (
        polarity * 0.4 +
        (pos_count - neg_count) * 0.3 +
        (title_pos - title_neg) * 0.3
    )
    
    # Determine sentiment and confidence
    if sentiment_score > 0.1 or (pos_count > neg_count * 1.5):
        sentiment = "Positive"
    elif sentiment_score < -0.1 or (neg_count > pos_count):
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    confidence = (abs(sentiment_score) + (1 - subjectivity) + abs(pos_count - neg_count)/10) / 3
    return {"sentiment": sentiment, "confidence": f"{confidence:.2f}"}

# Function to summarize text
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

# Function to extract keywords from text
def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "about", "into", "over", "after", "this", "that", "these", "those", "has", "was", "said", "says", "will", "would", "could", "should", "may", "might", "must", "can"}
    words = [word for word in words if word not in stop_words and len(word) > 3]
    return [word for word, count in Counter(words).most_common(5)]

# Function to extract the title of an article
def extract_title(soup, url):
    title = soup.title.string if soup.title else None
    if not title:
        h1_tag = soup.find('h1')
        title = h1_tag.get_text().strip() if h1_tag else url.split('/')[-1].replace('-', ' ').title()
    return title.strip()

# Function to search for news articles about a company
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
            
            # Extract links based on the search engine
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

# Function to process a single URL and extract relevant information
def process_url(url):
    try:
        print(f"Processing: {url}")
        content = fetch_content(url)
        if content:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = extract_title(soup, url)
            summary = summarize_text(content)
            keywords = extract_keywords(content)
            sentiment_analysis = analyze_sentiment(title + " " + content[:500])
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

# Function to process news articles for a company
def process_news(company):
    links = search_news(company)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_url, links))
    return [result for result in results if result]

# Function to perform comparative analysis on articles
def comparative_analysis(articles):
    if not articles:
        return {}
        
    # Basic sentiment statistics
    sentiments = [article['sentiment'] for article in articles]
    total = len(sentiments)
    sentiment_stats = {
        "positive": f"{sentiments.count('Positive') / total * 100:.2f}%",
        "negative": f"{sentiments.count('Negative') / total * 100:.2f}%",
        "neutral": f"{sentiments.count('Neutral') / total * 100:.2f}%"
    }
    
    # Analyze coverage differences
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
    
    # Topic overlap analysis
    all_topics = set()
    for article in articles:
        all_topics.update(article['keywords'])
    
    common_topics = set.intersection(*[set(article['keywords']) for article in articles])
    
    return {
        "sentiment_distribution": sentiment_stats,
        "coverage_differences": coverage_differences[:2],
        "topic_overlap": {
            "common_topics": list(common_topics),
            "unique_topics": list(all_topics - common_topics)
        }
    }

# Function to generate a final summary of articles
def final_summary(articles):
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
        summary += f"The company's latest news coverage is mostly positive ({(pos_count/total*100):.1f}%). "
        summary += "Market sentiment appears favorable, suggesting potential stock growth. "
    elif neg_count > pos_count:
        summary += f"Recent coverage leans negative ({(neg_count/total*100):.1f}%). "
        summary += "Investors should monitor developments closely. "
    else:
        summary += "Coverage shows balanced sentiment. "
    
    summary += f"Key topics discussed: {', '.join(main_topics)}. "
    summary += "Market implications depend on how these developments unfold."
    try:
        translator = Translator()
        hindi_summary = translator.translate(summary, dest='hi').text
        
        # Create audio file
        tts = gTTS(text=hindi_summary, lang='hi')
        audio_filename = f"summary_{time.strftime('%Y%m%d_%H%M%S')}.mp3"
        tts.save(audio_filename)
        
        return {
            "text_summary": summary,
            "hindi_summary": hindi_summary,
            "audio_file": audio_filename
        }
    except Exception as e:
        print(f"Error creating audio summary: {e}")
        return {
            "text_summary": summary,
            "hindi_summary": None,
            "audio_file": None
        }

__all__ = [
    'process_news',
    'comparative_analysis',
    'final_summary'
]
