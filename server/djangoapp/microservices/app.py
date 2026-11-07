from pathlib import Path
import nltk
from flask import Flask, jsonify
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.data.path.insert(0,str(Path(__file__).resolve().parent))
app=Flask(__name__)
sia=SentimentIntensityAnalyzer()
@app.get('/')
def home():
    return jsonify(service='VADER sentiment analyzer',status='ready')
@app.get('/analyze/<path:text>')
def analyze(text):
    if len(text)>4000:
        return jsonify(error='Text is too long'),400
    scores=sia.polarity_scores(text)
    score=scores['compound']
    return jsonify(sentiment='positive' if score>=0.05 else 'negative' if score<=-0.05 else 'neutral',scores=scores)
if __name__=='__main__':
    app.run(host='127.0.0.1',port=5050)
