import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import numpy as np

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = "MayankRao16Cornell.edu"
MYSQL_PORT = 3306
MYSQL_DATABASE = "kardashiandb"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded, 
# but if you decide to use SQLAlchemy ORM framework, 
# there's a much better and cleaner way to do this
def sql_search(episode):
    query_sql = f"""SELECT * FROM episodes WHERE LOWER( title ) LIKE '%%{episode.lower()}%%' limit 10"""
    keys = ["id","title","descr"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys,i)) for i in data])

@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return sql_search(text)

def edit_distance(query, message):
    query = query.lower()
    message = message.lower()
    m = len(query) + 1
    n = len(message) + 1
    delete = 1
    insert = 1
    substitute = 1

    edit_matrix = np.zeros((m,n))
    for i in range(1, m): 
        edit_matrix[i][0] = edit_matrix[i-1][0] + delete
    for j in range(1, n): 
        edit_matrix[0][j] = edit_matrix[0][j-1] + insert
    for i in range(1, m):
        for j in range(1, n):
            edit_matrix[i][j] = min(
                edit_matrix[i-1][j] + delete,
                edit_matrix[i][j-1] + insert,
                0 if query == message else edit_matrix[i-1][j-1] + substitute
            )
    return edit_matrix[m-1][n-1]

def location_search():
    location_query = request.args.get("location")
    query_sql = "SELECT * FROM locations"
    data = mysql_engine.query_selector(query_sql)
    results = []
    for l in data:
        edit_distance = edit_distance(location_query, l)
        results.append((edit_distance, l))
    results.sort(reverse=True)
    return (i[1] for i in results[:10])


# app.run(debug=True)