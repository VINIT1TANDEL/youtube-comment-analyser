import re
import os
import nltk
import joblib
import requests
import numpy as np
from bs4 import BeautifulSoup
import urllib.request as urllib
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud, STOPWORDS
from flask import Flask, render_template, request
import time

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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


def returnytcomments(url):
    data = []

    # Set up Chrome with webdriver-manager
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Comment out this line if you want to see the browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) as driver:
        wait = WebDriverWait(driver, 15)
        driver.get(url)

        for item in range(5):
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(2)

        for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#content"))):
            data.append(comment.text)

    return data


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


def create_wordcloud(clean_reviews):
    for_wc = ' '.join(clean_reviews)
    wcstops = set(STOPWORDS)
    wc = WordCloud(width=1400, height=800, stopwords=wcstops, background_color='white').generate(for_wc)
    plt.figure(figsize=(20, 10), facecolor='k', edgecolor='k')
    plt.imshow(wc, interpolation='bicubic')
    plt.axis('off')
    plt.tight_layout()
    CleanCache(directory='static/images')
    plt.savefig('static/images/woc.png')
    plt.close()


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

    org_comments = returnytcomments(url)
    temp = []

    for i in org_comments:
        if 5 < len(i) <= 500:
            temp.append(i)

    org_comments = temp
    clean_comments = clean(org_comments)

    create_wordcloud(clean_comments)

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


@app.route('/wc')
def wc():
    return render_template('wc.html')


class CleanCache:
    '''
    This class is responsible for clearing any residual image files
    from past searches.
    '''
    def __init__(self, directory=None):
        self.clean_path = directory
        if os.listdir(self.clean_path) != list():
            files = os.listdir(self.clean_path)
            for fileName in files:
                print(f"Removing file: {fileName}")
                os.remove(os.path.join(self.clean_path, fileName))
        print("Cache cleaned!")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # 10000 is fallback for local dev
    app.run(host='0.0.0.0', port=port)
    app.run(debug=True)