# News Summarization and Text-to-Speech ApplicationNews Summarization and Text-to-Speech Application

## Overview

This project is a News Summarization and Text-to-Speech (TTS) ApplicationNews Summarization and Text-to-Speech (TTS) Application that extracts news articles, performs sentiment analysis, conducts comparative analysis,
and generates Hindi TTS output. The application is built using PythonPython, with a web interface powered by GradioGradio, and is deployed on Hugging Face SpacesHugging Face Spaces.

## Features


-News ScrapingNews Scraping: Extracts news articles from various sources using BeautifulSoup.

-SummarizationSummarization: Generates concise summaries of extracted news articles.

-Sentiment AnalysisSentiment Analysis: Analyzes the sentiment (positive, negative, neutral) of the news content.

-Comparative AnalysisComparative Analysis: Compares different news sources for similar topics.

-Text-to-Speech (TTS)Text-to-Speech (TTS): Converts Hindi text into speech output.

-Web InterfaceWeb Interface: Provides an interactive UI using Streamlit.

-FastAPI IntegrationFastAPI Integration: Exposes API endpoints for various functionalities.

-Deployment on Hugging Face SpacesDeployment on Hugging Face Spaces: Makes the app easily accessible online.

## Project Structure

```
├── news_scraping.py # Backend script for web scraping
├── api.py # FastAPI implementation for handling API requests
├── app.py # Gradio frontend for the web interface
├── requirements.txt # List of required Python packages
├── README.md # Project documentation
```
## Installation and Setup


## PrerequisitesPrerequisites

Ensure you have the following installed:

```
Python 3.7+
pip (Python package manager)
Virtual environment (optional but recommended)
```
## Steps to Run Locally


1. Use VS Code or any coding environment to verify the Python version by running

```
python --version
```

2. Create a virtual environment (optional but recommended):

```
python -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Run the FastAPI backend

```
uvicorn api:app --reload
```

5. Run the Streamlit frontend

```
python app.py
```

6. Access the web interface or the hugging face link: https://huggingface.co/spaces/jeez21/21 using your browser

## Deployment on Hugging Face Spaces


1. Prepare your repository:
Ensure app.py is set as the entry point.
Include a requirements.txt file.

2. Push to Hugging Face Spaces
Create a new Space on Hugging Face.
Choose Streamlit as the SDK.
Push the code to the repository.

3. Run the application:
Hugging Face will automatically build and deploy the app.
Access the deployed URL.


## Future Enhancements


Add support for multiple languages.
Improve the summarization model for better accuracy.
Integrate additional news sources.
Enhance UI with more interactive features.

## Contact

For any questions or issues, feel free to reach out:


Email: jeevz0211@gmail.com
LinkedIn:(https://www.linkedin.com/in/jeevan-v-3640841a7/)

Enjoy using the News Summarization and TTS Application! 

