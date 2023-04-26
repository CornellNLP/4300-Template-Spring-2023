import json
import os
import re
import math
import numpy as np
import nltk
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
from dotenv import load_dotenv
import preprocessing
import text_mining

load_dotenv()
nltk.download("punkt")

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ["ROOT_PATH"] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = os.getenv("MYSQL_USER_PASSWORD")
MYSQL_PORT = 3306
MYSQL_DATABASE = "playlistsdb"

mysql_engine = MySQLDatabaseHandler(
    MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE
)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
# albert xiao is so hot
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

preprocessing.preprocess()
text_mining.init()


def accumulate_dot_scores(query_word_counts):
    doc_scores = {}
    for term, count in query_word_counts.items():
        if term in preprocessing.idf:
            for doc in preprocessing.inv_idx[term]:
                doc_scores[doc] = doc_scores.get(doc, 0) + (
                    preprocessing.idf[term] * count * preprocessing.idf[term]
                )
    return doc_scores


def index_search(query, index, idf, doc_norms):
    """
    Search the collection of documents for the given query.

    Returns
    =======
    results: sorted tuple list (score, pid)
    """
    results = []

    query_tokens = nltk.word_tokenize(query)
    lemmatizer = nltk.WordNetLemmatizer()
    query_tokens = [lemmatizer.lemmatize(tok) for tok in query_tokens]

    query_word_counts = {t: 0 for t in query_tokens}
    for token in query_tokens:
        query_word_counts[token] += 1

    query_norm = 0
    for i, tf in query_word_counts.items():
        if i in idf:
            query_norm += (tf * idf[i]) ** 2
    query_norm = np.sqrt(query_norm)

    dot_scores = accumulate_dot_scores(query_word_counts)
    for doc, score in dot_scores.items():
        cossim = score / (query_norm * doc_norms[doc])
        results.append((cossim, doc))

    results.sort(reverse=True, key=lambda x: x[0])
    return results


@app.route("/search")
def search():
    query = request.args.get("title")
    query = preprocessing.normalize_name(query)
    k = 50  # Number of playlists to examine
    top_playlists = index_search(
        query, preprocessing.inv_idx, preprocessing.idf, preprocessing.doc_norms
    )[:k]
    song_scores = {}
    for score, pid in top_playlists:
        for track in preprocessing.playlists[pid]["tracks"]:
            song = track["track_name"]
            if song not in song_scores:
                song_scores[song] = 0

            song_scores[song] += score

    ranked_songs = list(song_scores.items())
    ranked_songs.sort(key=lambda x: x[1], reverse=True)
    print(ranked_songs[:50])
    return ranked_songs[:15]
    # app.run(debug=True)
