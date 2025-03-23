import streamlit as st
import requests
import json
import asyncio
from googletrans import Translator
from gtts import gTTS  # For Text to Speech conversion
import os

# Importing the functions from your backend
from news_scraping import process_news, comparative_analysis, final_summary  

# Function to display articles in the Streamlit app
def display_articles(news_data):
    for idx, article in enumerate(news_data, 1):
        st.subheader(f"Article {idx}: {article['title']}")  # Display article title
        st.markdown(f"**Source:** {article['source']}")  # Display article source
        st.markdown(f"[Read more]({article['link']})")  # Link to the full article
        st.markdown(f"**Summary:** {article['summary']}")  # Display article summary
        st.markdown(f"**Keywords:** {', '.join(article['keywords'])}")  # Display extracted keywords
        st.markdown(f"**Sentiment:** {article['sentiment']} (Confidence: {article['confidence']})")  # Sentiment analysis
        st.write("-" * 100)  # Separator for better readability

# Function to display comparative analysis results
def display_comparative_analysis(analysis):
    st.write("## Comparative Analysis")  # Section header
    st.write(f"Total Articles: {len(analysis['sentiment_distribution'])}")  # Total articles analyzed
    for sentiment, percentage in analysis['sentiment_distribution'].items():
        st.write(f"{sentiment.title()}: {percentage}")  # Display sentiment distribution
    
    st.write("### Coverage Differences")  # Subsection for coverage differences
    for diff in analysis['coverage_differences']:
        st.write(f"**Comparison:** {diff['Comparison']}")  # Display comparison details
        st.write(f"**Impact:** {diff['Impact']}")  # Display impact details
    
    st.write("### Topic Analysis")  # Subsection for topic analysis
    st.write(f"**Common Topics:** {', '.join(analysis['topic_overlap']['common_topics'])}")  # Common topics
    st.write(f"**Unique Topics:** {', '.join(analysis['topic_overlap']['unique_topics'])}")  # Unique topics

# Asynchronous function to generate Hindi summary and audio file
async def generate_hindi_summary_and_audio(text_summary):
    # Translate the English summary to Hindi
    translator = Translator()
    translated = await translator.translate(text_summary, src='en', dest='hi')
    hindi_summary = translated.text  # Extract translated text
    
    # Convert the Hindi summary to audio using gTTS
    audio_file_path = "hindi_summary.mp3"
    tts = gTTS(hindi_summary, lang='hi', slow=False)
    tts.save(audio_file_path)  # Save the audio file
    
    return hindi_summary, audio_file_path  # Return the Hindi summary and audio file path

# Main function to run the Streamlit app
def main():
    st.title("News Summarization & Sentiment Analysis")  # App title

    # Input field for the company name
    company_name = st.text_input("Enter the Company Name:")
    
    # Button to fetch news articles
    if st.button("Fetch News"):
        if company_name:
            with st.spinner("Fetching news articles..."):  # Show a spinner while fetching data
                news_data = process_news(company_name)  # Fetch news articles
                
                if not news_data:
                    st.error("No news articles found.")  # Display error if no articles are found
                else:
                    st.success(f"Fetched {len(news_data)} articles!")  # Success message
                    display_articles(news_data)  # Display the fetched articles
                    
                    # Perform comparative analysis
                    analysis = comparative_analysis(news_data)
                    display_comparative_analysis(analysis)  # Display analysis results

                    # Generate the final summary
                    final_summ = final_summary(news_data, company_name)
                    st.write("## Final Summary")  # Section header
                    st.write(final_summ["text_summary"])  # Display the final summary
                    
                    # Generate Hindi summary and TTS audio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    hindi_summary, audio_file_path = loop.run_until_complete(generate_hindi_summary_and_audio(final_summ["text_summary"]))

                    # Debugging lines to verify Hindi summary and audio file path
                    st.write("Final Hindi Summary Check:", hindi_summary)
                    st.write("Audio File Path:", audio_file_path)

                    if hindi_summary:
                        st.write("### Hindi Summary")  # Subsection for Hindi summary
                        st.write(hindi_summary)  # Display the Hindi summary
                        st.audio(audio_file_path)  # Play the generated audio
                    
                    # Prepare downloadable JSON output
                    output = {
                        "company": company_name,
                        "articles": news_data,
                        "comparative_analysis": analysis,
                        "final_summary": final_summ["text_summary"],
                        "hindi_summary": hindi_summary
                    }
                    
                    # Provide a download button for the JSON output
                    json_filename = f"news_analysis_{company_name.replace(' ', '_')}.json"
                    st.download_button(
                        label="Download Results",
                        data=json.dumps(output, indent=2),
                        file_name=json_filename,
                        mime="application/json"
                    )
        else:
            st.warning("Please enter a company name.")  # Warning if no company name is entered

# Entry point of the script
if __name__ == "__main__":
    main()