import re
import os
import nltk
import requests
import numpy as np
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud, STOPWORDS
from flask import Flask, render_template, request

# NLTK Downloads
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('wordnet')

# Flask app config
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# NLP tools
wnl = WordNetLemmatizer()
sia = SentimentIntensityAnalyzer()
stop_words = stopwords.words('english')

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def returnytcomments(video_id):
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("YouTube API key not set in environment variables.")

    comments = []
    url = f"https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        'part': 'snippet',
        'videoId': video_id,
        'key': api_key,
        'textFormat': 'plainText',
        'maxResults': 100
    }

    while True:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"YouTube API error: {response.status_code} - {response.text}")

        data = response.json()
        for item in data.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        if 'nextPageToken' in data:
            params['pageToken'] = data['nextPageToken']
        else:
            break

    return comments

def clean(org_comments):
    y = []
    for x in org_comments:
        x = x.split()
        x = [i.lower().strip() for i in x]
        x = [i for i in x if i not in stop_words]
        x = [i for i in x if len(i) > 2]
        x = [wnl.lemmatize(i) for i in x]
        y.append(' '.join(x))
    return y

def returnsentiment(x):
    score = sia.polarity_scores(x)['compound']
    if score > 0:
        sent = 'Positive'
    elif score == 0:
        sent = 'Neutral'
    else:
        sent = 'Negative'
    return score, sent

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results', methods=['GET'])
def result():
    url = request.args.get('url')
    video_id = extract_video_id(url)

    if not video_id:
        return "Invalid YouTube URL.", 400

    try:
        org_comments = returnytcomments(video_id)
    except Exception as e:
        return f"Error fetching comments: {e}", 500

    org_comments = [i for i in org_comments if 5 < len(i) <= 500]
    clean_comments = clean(org_comments)

    np_count, nn, nne = 0, 0, 0
    predictions = []
    scores = []

    for i in clean_comments:
        score, sent = returnsentiment(i)
        scores.append(score)
        if sent == 'Positive':
            predictions.append('POSITIVE')
            np_count += 1
        elif sent == 'Negative':
            predictions.append('NEGATIVE')
            nn += 1
        else:
            predictions.append('NEUTRAL')
            nne += 1

    dic = []
    for i, cc in enumerate(clean_comments):
        x = {
            'sent': predictions[i],
            'clean_comment': cc,
            'org_comment': org_comments[i],
            'score': scores[i]
        }
        dic.append(x)

    return render_template('result.html', n=len(clean_comments), nn=nn, np=np_count, nne=nne, dic=dic)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
