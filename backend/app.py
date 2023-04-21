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
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)


total_playlists = 0
total_tracks = 0
inv_idx = {}  # (k, v): (term, (pid, tf=1))
playlists = {}  # (k, v): (pid, playlist JSON)
idf = {}
doc_norms = None


def process_mpd(path):
    """
    Process MPD to precompute inverted_index.
    """
    filenames = os.listdir(path)
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            if total_playlists % 1000000 == 0:
                print(filename)
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)

            for playlist in mpd_slice["playlists"]:
                playlists[playlist["pid"]] = playlist
                process_playlist(playlist)


def process_playlist(playlist):
    global total_playlists
    total_playlists += 1

    nname = normalize_name(playlist["name"])
    tokens = nltk.word_tokenize(nname)

    lemmatizer = nltk.WordNetLemmatizer()
    for tok in tokens:
        tok = lemmatizer.lemmatize(tok)
        if tok not in inv_idx:
            inv_idx[tok] = []
        inv_idx[tok].append(playlist["pid"])


def compute_idf(n_docs, min_df=2, max_df_ratio=0.2):
    for term, docs in inv_idx.items():
        count_docs = len(docs)
        if count_docs >= min_df and count_docs / n_docs <= max_df_ratio:
            idf[term] = math.log(n_docs / (1 + count_docs), 2)


def compute_doc_norms(n_docs):
    # Precompute the euclidean norm of each document.
    print(n_docs)
    norms = np.zeros(n_docs)
    for term, doc in inv_idx.items():
        for d in doc:
            t = idf.get(term, 0)
            norms[d] += t**2
    return np.sqrt(norms)


def accumulate_dot_scores(query_word_counts):
    doc_scores = {}
    for term, count in query_word_counts.items():
        if term in idf:
            for doc in inv_idx[term]:
                doc_scores[doc] = doc_scores.get(doc, 0) + (
                    idf[term] * count * idf[term]
                )
    return doc_scores


def normalize_name(name):
    """
    Normalizes a string by converting it to lowercase, removing special characters and extra spaces, and returning the result.
    """
    name = name.lower()
    name = re.sub(r"[.,\/#!$%\^\*;:{}=\_`~()@]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


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


@app.route("/start")
def start():
    pass


@app.route("/search")
def search():
    query = request.args.get("title")
    query = normalize_name(query)
    k = 50  # Number of playlists to examine
    top_playlists = index_search(query, inv_idx, idf, doc_norms)[:k]
    song_scores = {}
    for score, pid in top_playlists:
        for track in playlists[pid]["tracks"]:
            song = track["track_name"]
            if song not in song_scores:
                song_scores[song] = 0

            song_scores[song] += score

    ranked_songs = list(song_scores.items())
    ranked_songs.sort(key=lambda x: x[1], reverse=True)
    print(ranked_songs[:50])
    return ranked_songs[:15]
    # app.run(debug=True)


print("processing")
process_mpd("../data")
print("computing idf")
print(total_playlists)
compute_idf(total_playlists)
inv_idx = {key: val for key, val in inv_idx.items() if key in idf}
print("computing doc norms")
doc_norms = compute_doc_norms(total_playlists)
print("done")
