import streamlit as st
import pandas as pd
import requests
import json
import os
import base64
import tempfile
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API URL - change this to your deployed API endpoint when available
API_URL = "http://localhost:8000"

def main():
    """Main Streamlit application."""
    # Set page config
    st.set_page_config(
        page_title="News Sentiment Analyzer",
        page_icon="📰",
        layout="wide"
    )
    
    # Page title and description
    st.title("📰 News Sentiment Analyzer")
    st.markdown("""
    This application analyzes news articles for a given company, performs sentiment analysis, 
    and provides a comparative analysis with Hindi text-to-speech output.
    """)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Company Selection")
        
        # Company input
        company_options = [
            "Apple", "Microsoft", "Google", "Amazon", "Tesla", 
            "Walmart", "Reliance Industries", "Tata", "Infosys", "Adani"
        ]
        company_input_method = st.radio("Select Input Method:", ["Dropdown", "Text Input"])
        
        if company_input_method == "Dropdown":
            company_name = st.selectbox("Select Company:", company_options)
        else:
            company_name = st.text_input("Enter Company Name:", "")
        
        # Number of articles
        num_articles = st.slider("Number of Articles:", min_value=3, max_value=15, value=5)
        
        # Option to use dummy data (for development/testing)
        use_dummy_data = st.checkbox("Use Demo Data", value=True, help="Use dummy data for demonstration purposes")
        
        # Submit button
        analyze_button = st.button("Analyze News")
    
    # Main content area
    if analyze_button:
        if not company_name:
            st.error("Please enter or select a company name.")
            return
        
        with st.spinner(f"Analyzing news for {company_name}..."):
            try:
                # Call API to analyze company news
                analysis = get_company_analysis(company_name, num_articles, use_dummy_data)
                
                if not analysis:
                    st.error(f"No analysis results found for {company_name}.")
                    return
                
                # Display results
                display_results(analysis, company_name)
                
                # Generate TTS
                with st.spinner("Generating Hindi audio..."):
                    audio_data = generate_tts(company_name, num_articles, use_dummy_data)
                    if audio_data and 'audio_path' in audio_data:
                        st.audio(audio_data['audio_path'])
                    else:
                        st.warning("Could not generate audio output.")
                
            except Exception as e:
                logger.error(f"Error in analysis: {e}")
                st.error(f"An error occurred: {str(e)}")
    
    # Display instructions when first loading
    if not analyze_button:
        st.info("👈 Select a company from the sidebar and click 'Analyze News' to start.")
        
        # Example output
        st.subheader("Example Output")
        st.markdown("""
        The analysis will provide:
        - Sentiment analysis of news articles (Positive, Negative, Neutral)
        - Key topics covered in each article
        - Comparative analysis across articles
        - Hindi text-to-speech summary
        """)
        
        # Sample visualization
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Sample Sentiment Distribution")
            sample_data = pd.DataFrame({
                'Sentiment': ['Positive', 'Negative', 'Neutral'],
                'Count': [5, 3, 2]
            })
            st.bar_chart(sample_data.set_index('Sentiment'))
        with col2:
            st.markdown("#### Sample Topics")
            st.markdown("- Financial Performance\n- Product Launch\n- Market Competition\n- Innovation\n- Regulation")

def get_company_analysis(company_name: str, num_articles: int, use_dummy_data: bool) -> Dict[str, Any]:
    """
    Get company news analysis from the API.
    
    Args:
        company_name: Name of the company
        num_articles: Number of articles to analyze
        use_dummy_data: Whether to use dummy data
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Define the API endpoint
        endpoint = f"{API_URL}/analyze"
        
        # Prepare the request payload
        payload = {
            "company_name": company_name,
            "num_articles": num_articles,
            "use_dummy_data": use_dummy_data
        }
        
        # Make the request
        response = requests.post(endpoint, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            st.error(f"API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting company analysis: {e}")
        raise

def generate_tts(company_name: str, num_articles: int, use_dummy_data: bool) -> Dict[str, Any]:
    """
    Generate text-to-speech from the API.
    
    Args:
        company_name: Name of the company
        num_articles: Number of articles to analyze
        use_dummy_data: Whether to use dummy data
        
    Returns:
        Dictionary with audio path
    """
    try:
        # Define the API endpoint
        endpoint = f"{API_URL}/tts"
        
        # Prepare the request payload
        payload = {
            "company_name": company_name,
            "num_articles": num_articles,
            "use_dummy_data": use_dummy_data
        }
        
        # Make the request
        response = requests.post(endpoint, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"TTS API error: {response.status_code} - {response.text}")
            st.error(f"TTS API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise

def display_results(analysis: Dict[str, Any], company_name: str):
    """
    Display analysis results in Streamlit.
    
    Args:
        analysis: Dictionary with analysis results
        company_name: Name of the company
    """
    # Display final sentiment analysis
    st.subheader("📊 Overall Sentiment Analysis")
    final_sentiment = analysis.get('final_sentiment_analysis', 'No analysis available')
    st.markdown(f"**{final_sentiment}**")
    
    # Display sentiment distribution
    st.subheader("Sentiment Distribution")
    sentiment_dist = analysis.get('comparative_sentiment_score', {}).get('sentiment_distribution', {})
    if sentiment_dist:
        sentiment_data = pd.DataFrame({
            'Sentiment': ['Positive', 'Negative', 'Neutral'],
            'Count': [
                sentiment_dist.get('positive', 0),
                sentiment_dist.get('negative', 0),
                sentiment_dist.get('neutral', 0)
            ]
        })
        
        # Display sentiment bar chart
        st.bar_chart(sentiment_data.set_index('Sentiment'))
    
    # Display articles
    st.subheader("📰 News Articles")
    articles = analysis.get('articles', [])
    if articles:
        for i, article in enumerate(articles):
            with st.expander(f"Article {i+1}: {article.get('title', 'Untitled')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Summary:** {article.get('summary', 'No summary available')}")
                    
                    if article.get('url'):
                        st.markdown(f"**Source:** [{article.get('source', 'Unknown')}]({article.get('url')})")
                    
                    if article.get('date'):
                        st.markdown(f"**Date:** {article.get('date')}")
                
                with col2:
                    sentiment = article.get('sentiment', 'Neutral')
                    sentiment_color = {
                        'Positive': 'green',
                        'Negative': 'red',
                        'Neutral': 'gray'
                    }.get(sentiment, 'gray')
                    
                    st.markdown(f"**Sentiment:** <span style='color:{sentiment_color};'>{sentiment}</span>", unsafe_allow_html=True)
                    
                    st.markdown("**Topics:**")
                    for topic in article.get('topics', []):
                        st.markdown(f"- {topic}")
    
    # Display comparative analysis
    st.subheader("📈 Comparative Analysis")
    comparative = analysis.get('comparative_sentiment_score', {})
    
    # Display coverage differences
    coverage_diffs = comparative.get('coverage_differences', [])
    if coverage_diffs:
        for i, diff in enumerate(coverage_diffs):
            st.markdown(f"**Finding {i+1}:** {diff.get('comparison', '')}")
            st.markdown(f"**Impact:** {diff.get('impact', '')}")
    
    # Display topic overlap
    topic_overlap = comparative.get('topic_overlap', {})
    if topic_overlap:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Common Topics Across Articles:**")
            common_topics = topic_overlap.get('common_topics', [])
            if common_topics:
                for topic in common_topics:
                    st.markdown(f"- {topic}")
            else:
                st.markdown("No common topics found")
        
        with col2:
            st.markdown("**Unique Topics by Article:**")
            unique_topics = topic_overlap.get('unique_topics', {})
            if unique_topics:
                for article_id, topics in unique_topics.items():
                    st.markdown(f"**{article_id}:** {', '.join(topics)}")
            else:
                st.markdown("No unique topics found")

if __name__ == "__main__":
    main()
