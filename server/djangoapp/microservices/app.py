from pathlib import Path
from flask import Flask, jsonify
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask('Sentiment Analyzer')
nltk.data.path.insert(0, str(Path(__file__).resolve().parent))
sia = SentimentIntensityAnalyzer(lexicon_file='sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt')

@app.get('/')
def home():
    return jsonify(service='VADER sentiment analysis', status='ready')

@app.get('/analyze/<path:input_txt>')
def analyze_sentiment(input_txt):
    scores = sia.polarity_scores(input_txt)
    score = scores['compound']
    sentiment = 'positive' if score >= 0.05 else 'negative' if score <= -0.05 else 'neutral'
    return jsonify(sentiment=sentiment, scores=scores)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
