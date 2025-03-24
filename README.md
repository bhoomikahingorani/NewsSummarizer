# News Sentiment Analysis and Text-to-Speech Application

This application extracts news articles related to a specified company, performs sentiment analysis, conducts comparative analysis across articles, and generates a Hindi text-to-speech output of the analysis.

## Overview

The application works as follows:

1. Users input a company name via a web interface
2. The system extracts news articles related to the company
3. Sentiment analysis is performed on each article
4. A comparative analysis is generated across all articles
5. A Hindi text-to-speech output is created summarizing the findings
6. Results are displayed in a user-friendly interface

## Features

- **News Extraction**: Extracts news articles related to the specified company using web scraping with BeautifulSoup
- **Sentiment Analysis**: Analyzes the sentiment of each article (positive, negative, neutral)
- **Topic Extraction**: Identifies key topics covered in each article
- **Comparative Analysis**: Compares sentiment and topics across articles
- **Text-to-Speech**: Converts the summarized analysis to Hindi speech
- **Web Interface**: Provides a clean, user-friendly web interface using Streamlit

## Project Structure

```
news-sentiment-app/
├── app.py                 # Main Streamlit application
├── api.py                 # API endpoints
├── requirements.txt       # Dependencies
├── README.md              # Documentation
└── utils/
    ├── __init__.py
    ├── news_extractor.py  # News extraction functionality
    ├── sentiment.py       # Sentiment analysis
    ├── comparative.py     # Comparative analysis
    ├── tts.py             # Text-to-speech conversion
    └── models.py          # Data models/structures
```

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/NewsSummerizer.git
   cd NewsSummerizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download required NLTK data:
   ```python
   python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('stopwords')"
   ```

### Running the Application

1. Start the API server:
   ```
   python api_file.py
   ```

2. In a separate terminal, run the Streamlit app:
   ```
   streamlit run app_file.py
   ```

3. Access the application in your browser at: http://localhost:8501

## API Documentation

The application provides the following API endpoints:

### 1. Analyze Company News

**Endpoint**: `/analyze`
**Method**: POST
**Request Body**:
```json
{
  "company_name": "Tesla",
  "num_articles": 10,
  "use_dummy_data": false
}
```

**Response**: JSON object containing the analysis results

### 2. Generate Text-to-Speech

**Endpoint**: `/tts`
**Method**: POST
**Request Body**:
```json
{
  "company_name": "Tesla",
  "num_articles": 10,
  "use_dummy_data": false
}
```

**Response**: JSON object with the path to the generated audio file

## Implementation Details

### News Extraction

The application uses BeautifulSoup to scrape news articles from various sources. It extracts the article title, content, date, and source URL. For demonstration purposes, a dummy data generator is also available.

### Sentiment Analysis

Sentiment analysis is performed using a combination of the NLTK VADER sentiment analyzer and a transformer-based model (FinBERT) for financial news. The sentiment is classified as positive, negative, or neutral.

### Topic Extraction

Topics are extracted using a simple keyword frequency approach. In a production environment, more sophisticated methods like LDA (Latent Dirichlet Allocation) or transformer-based models could be used.

### Comparative Analysis

The comparative analysis identifies trends across articles, compares sentiment distribution, and analyzes topic overlap. It generates insights on how coverage varies across different sources.

### Text-to-Speech

Hindi text-to-speech conversion is performed using a pre-trained model from Hugging Face. The text is first translated to Hindi using the Google Translate API, then converted to speech.

## Deployment

### Hugging Face Spaces Deployment

The application is deployed on Hugging Face Spaces:

1. Create a new Space on Hugging Face Spaces
2. Set up the Git repository
3. Add the required dependencies in the `requirements.txt` file
4. Add the application files to the repository
5. Access the application through the provided URL

## Assumptions and Limitations

- The application assumes that news articles are accessible via web scraping and don't require JavaScript rendering.
- The sentiment analysis might not be domain-specific, which could lead to misclassifications in specialized contexts.
- The topic extraction is based on simple keyword frequency, which might miss complex themes.
- Hindi translation is done via Google Translate, which might not be perfect for domain-specific terminology.
- The application doesn't store historical data for long-term trend analysis.

## Future Enhancements

- Integrate paid news APIs for more reliable article extraction
- Implement domain-specific sentiment analysis models
- Use more sophisticated topic modeling techniques
- Add support for more languages
- Implement a database for storing analysis results and tracking trends over time
- Add visualization dashboards for better data representation
- Include entity recognition for identifying key players and relationships

## License

This project is licensed under the MIT License - see the LICENSE file for details.
