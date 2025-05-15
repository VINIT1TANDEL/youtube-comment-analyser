# YouTube Comment Sentiment Analysis 🌐

This project is a Flask-based web application that performs **Sentiment Analysis** on YouTube video comments. It fetches comments using the YouTube Data API, processes and cleans them using NLP techniques, and classifies the sentiment as **Positive**, **Negative**, or **Neutral** using NLTK's VADER Sentiment Analyzer.

---

## 📌 Features

- Extracts YouTube video ID from the provided URL.
- Fetches top-level comments using the YouTube Data API v3.
- Cleans and lemmatizes text using `nltk` preprocessing tools.
- Analyzes sentiment using `SentimentIntensityAnalyzer`.
- Displays total comment count and sentiment distribution.
- Visualizes results on a simple HTML page.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **NLP Tools**: NLTK (VADER, WordNetLemmatizer, Stopwords)
- **API**: YouTube Data API v3
- **Frontend**: HTML (Jinja2 Templates), Bootstrap (optional for styling)

---

## 📁 Project Structure

