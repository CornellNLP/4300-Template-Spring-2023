import json
import os
import csv
import sys
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
# MYSQL_USER = "root"
# MYSQL_USER_PASSWORD = "Xuannhi230902!"
# MYSQL_PORT = 3306
# MYSQL_DATABASE = "colleges"

MYSQL_USER = "root"
# MYSQL_USER_PASSWORD = "MayankRao16Cornell.edu"
MYSQL_USER_PASSWORD = "Xuannhi230902!"
MYSQL_PORT = 3306
MYSQL_DATABASE = "kardashiandb"
mysql_engine = MySQLDatabaseHandler(
    MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)


def sql_search(state_city, size, sort):
    lst = []
    if size == 'small':
        query_sql = f"""SELECT * FROM colleges WHERE ((state = '{state_city}' OR city = '{state_city}') AND (tot_enroll < 5000))"""
    elif size == 'medium':
        query_sql = f"""SELECT * FROM colleges WHERE (state = '{state_city}' OR city = '{state_city}' AND (tot_enroll BETWEEN 5000 AND 15000))"""
    elif size == 'large':
        query_sql = f"""SELECT * FROM colleges WHERE (state = '{state_city}' OR city = '{state_city}' AND (tot_enroll > 15000))"""
    else:
        query_sql = f"""SELECT * FROM colleges WHERE (state = '{state_city}' OR city = '{state_city}')"""
    data = mysql_engine.query_selector(query_sql)
    for elem in list(data):
        name = elem[0]
        city = elem[1]
        state = elem[2]
        website = elem[5]
        enroll = elem[6]
        # if website != "https://" + str(website):
        #     website = "https://" + str(website)
        # else:
        #     website = elem[5]
        lst.append(({'title': name, 'location': city + ", "+state,
                   'enrolled': enroll, 'website': website}))
    if sort == "Alphabetical":
        lst = sorted(lst, key=lambda d: d['title'])
    # elif sort_input == "Location":  #maybe we could incorporate text comparison element here
    #     lst = sorted(arr, key=lambda d: d['location'])
    elif sort == "Enrollment Size":
        lst = sorted(lst, key=lambda d: int(d['enrolled']))
    return lst


def sql_search2(region, size, sort):
    lst = []
    if size == 'small':
        if region == 'midwest':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('IL','IN','MI','OH','ND','SD','NE','KS','MN','IA','MO','WI') AND (tot_enroll < 5000)"""
        elif region == 'southwest':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('TX','OK','NM','AZ') AND (tot_enroll < 5000)"""
        elif region == 'west':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('AK','HI','CO','WY','MT', 'WA','NV', 'CA','ID','OR','UT') AND (tot_enroll < 5000)"""
        elif region == 'northeast':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('DE','PA','NY','NJ','VT','NH','ME','MA','CT','RI','MD') AND (tot_enroll < 5000)"""
        elif region == 'southeast':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('WV','VA','KY','TN','NC','SC','GA','AL','MS','AR','LA','FL') AND (tot_enroll < 5000)"""
    elif size == 'medium':
        if region == "midwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('IL','IN','MI','OH','ND','SD','NE','KS','MN','IA','MO','WI') AND (tot_enroll BETWEEN 5000 AND 15000)"""
        elif region == "southwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('TX','OK','NM','AZ') AND (tot_enroll BETWEEN 5000 AND 15000)"""
        elif region == "west":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('AK','HI','CO','WY','MT', 'WA','NV', 'CA','ID','OR','UT') AND (tot_enroll BETWEEN 5000 AND 15000)"""
        elif region == "northeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('DE','PA','NY','NJ','VT','NH','ME','MA','CT','RI','MD') AND (tot_enroll BETWEEN 5000 AND 15000)"""
        elif region == "southeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('WV','VA','KY','TN','NC','SC','GA','AL','MS','AR','LA','FL') AND (tot_enroll BETWEEN 5000 AND 15000)"""
    elif size == 'large':
        if region == "midwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('IL','IN','MI','OH','ND','SD','NE','KS','MN','IA','MO','WI') AND (tot_enroll > 15000)"""
        elif region == "southwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('TX','OK','NM','AZ') AND (tot_enroll > 15000)"""
        elif region == "west":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('AK','HI','CO','WY','MT', 'WA','NV', 'CA','ID','OR','UT') AND (tot_enroll > 15000)"""
        elif region == "northeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('DE','PA','NY','NJ','VT','NH','ME','MA','CT','RI','MD') AND (tot_enroll > 15000)"""
        elif region == "southeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('WV','VA','KY','TN','NC','SC','GA','AL','MS','AR','LA','FL') AND (tot_enroll > 15000)"""
    else:
        if region == "midwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('IL','IN','MI','OH','ND','SD','NE','KS','MN','IA','MO','WI')"""
        elif region == "southwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('TX','OK','NM','AZ')"""
        elif region == "west":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('AK','HI','CO','WY','MT', 'WA','NV', 'CA','ID','OR','UT')"""
        elif region == "northeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('DE','PA','NY','NJ','VT','NH','ME','MA','CT','RI','MD')"""
        elif region == "southeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('WV','VA','KY','TN','NC','SC','GA','AL','MS','AR','LA','FL')"""

    data = mysql_engine.query_selector(query_sql)
    for elem in list(data):
        name = elem[0]
        city = elem[1]
        state = elem[2]
        website = elem[5]
        enroll = elem[6]
        # if website != "https://" + str(website):
        #     website = "https://" + str(website)
        # else:
        #     website = elem[5]
        # print(website)

        lst.append(({'title': name, 'location': city + ", "+state,
                   'enrolled': enroll, 'website': website}))
    if sort == "Alphabetical":
        lst = sorted(lst, key=lambda d: d['title'])
    # elif sort_input == "Location":  #maybe we could incorporate text comparison element here
    #     lst = sorted(arr, key=lambda d: d['location'])
    elif sort == "Enrollment Size":
        lst = sorted(lst, key=lambda d: int(d['enrolled']))
    return lst


def sql_search3(state_city, region, size, sort):
    lst = []
    if size == 'small':
        if region == 'midwest':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('IL','IN','MI','OH','ND','SD','NE','KS','MN','IA','MO','WI') AND (tot_enroll < 5000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == 'southwest':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('TX','OK','NM','AZ') AND (tot_enroll < 5000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == 'west':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('AK','HI','CO','WY','MT','WA','NV','CA','ID','OR','UT') AND (tot_enroll < 5000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == 'northeast':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('DE','PA','NY','NJ','VT','NH','ME','MA','CT','RI','MD') AND (tot_enroll < 5000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == 'southeast':
            query_sql = f"""SELECT * FROM colleges WHERE state IN('WV','VA','KY','TN','NC','SC','GA','AL','MS','AR','LA','FL') AND (tot_enroll < 5000) AND (state = '{state_city}' OR city = '{state_city}')"""
    elif size == 'medium':
        if region == "midwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('IL','IN','MI','OH','ND','SD','NE','KS','MN','IA','MO','WI') AND (tot_enroll BETWEEN 5000 AND 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "southwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN(TX','OK','NM','AZ') AND (tot_enroll BETWEEN 5000 AND 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "west":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('AK','HI','CO','WY','MT','WA','NV','CA','ID','OR','UT') AND (tot_enroll BETWEEN 5000 AND 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "northeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('DE','PA','NY','NJ','VT','NH','ME','MA','CT','RI','MD' ) AND (tot_enroll BETWEEN 5000 AND 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "southeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('WV','VA','KY','TN','NC','SC','GA','AL','MS','AR','LA','FL') AND (tot_enroll BETWEEN 5000 AND 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
    elif size == 'large':
        if region == "midwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('IL','IN','MI','OH','ND','SD','NE','KS','MN','IA','MO','WI') AND (tot_enroll > 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "southwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN(TX','OK','NM','AZ') AND (tot_enroll > 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "west":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('AK','HI','CO','WY','MT','WA','NV','CA','ID','OR','UT') AND (tot_enroll > 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "northeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('DE','PA','NY','NJ','VT','NH','ME','MA','CT','RI','MD' ) AND (tot_enroll > 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "southeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('WV','VA','KY','TN','NC','SC','GA','AL','MS','AR','LA','FL') AND (tot_enroll > 15000) AND (state = '{state_city}' OR city = '{state_city}')"""
    else:
        if region == "midwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('IL','IN','MI','OH','ND','SD','NE','KS','MN','IA','MO','WI') AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "southwest":
            query_sql = f"""SELECT * FROM colleges WHERE state IN(TX','OK','NM','AZ') AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "west":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('AK','HI','CO','WY','MT','WA','NV','CA','ID','OR','UT') AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "northeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('DE','PA','NY','NJ','VT','NH','ME','MA','CT','RI','MD' ) AND (state = '{state_city}' OR city = '{state_city}')"""
        elif region == "southeast":
            query_sql = f"""SELECT * FROM colleges WHERE state IN('WV','VA','KY','TN','NC','SC','GA','AL','MS','AR','LA','FL') AND (state = '{state_city}' OR city = '{state_city}')"""
    data = mysql_engine.query_selector(query_sql)
    for elem in list(data):
        name = elem[0]
        city = elem[1]
        state = elem[2]
        website = elem[5]
        enroll = elem[6]
        # if website != "https://" + str(website):
        #     website = "https://" + str(website)
        # else:
        #     website = elem[5]
        lst.append(({'title': name, 'location': city + ", "+state,
                   'enrolled': enroll, 'website': website}))
    if sort == "Alphabetical":
        lst = sorted(lst, key=lambda d: d['title'])
    # elif sort_input == "Location":  #maybe we could incorporate text comparison element here
    #     lst = sorted(arr, key=lambda d: d['location'])
    elif sort == "Enrollment Size":
        lst = sorted(lst, key=lambda d: int(d['enrolled']))
    return lst
### MINIMUM EDIT DISTANCE ###


def insertion_cost(message, j):
    return 1


def deletion_cost(query, i):
    return 1


def substitution_cost(query, message, i, j):
    if query[i-1] == message[j-1]:
        return 0
    else:
        return 1


def edit_matrix(query, message, ins_cost_func, del_cost_func, sub_cost_func):
    """ Calculates the edit matrix

    Arguments
    =========

    query: query string,

    message: message string,

    ins_cost_func: function that returns the cost of inserting a letter,

    del_cost_func: function that returns the cost of deleting a letter,

    sub_cost_func: function that returns the cost of substituting a letter,

    Returns:
        edit matrix {(i,j): int}
    """

    m = len(query) + 1
    n = len(message) + 1

    chart = {(0, 0): 0}
    for i in range(1, m):
        chart[i, 0] = chart[i-1, 0] + del_cost_func(query, i)
    for j in range(1, n):
        chart[0, j] = chart[0, j-1] + ins_cost_func(message, j)
    for i in range(1, m):
        for j in range(1, n):
            chart[i, j] = min(
                chart[i-1, j] + del_cost_func(query, i),
                chart[i, j-1] + ins_cost_func(message, j),
                chart[i-1, j-1] + sub_cost_func(query, message, i, j)
            )
    return chart


def edit_distance(query, message, ins_cost_func, del_cost_func, sub_cost_func):
    """ Finds the edit distance between a query and a message using the edit matrix

    Arguments
    =========

    query: query string,

    message: message string,

    ins_cost_func: function that returns the cost of inserting a letter,

    del_cost_func: function that returns the cost of deleting a letter,

    sub_cost_func: function that returns the cost of substituting a letter,

    Returns:
        edit cost (int)
    """

    query = query.lower()
    message = message.lower()
    matrix = edit_matrix(query, message, ins_cost_func,
                         del_cost_func, sub_cost_func)
    return matrix[(len(query), len(message))]


def edit_distance_search(query, msgs, ins_cost_func, del_cost_func, sub_cost_func):
    """ Edit distance search

    Arguments
    =========

    query: string,
        The query we are looking for.

    msgs: list of dicts,
        Each message in this list has a 'text' field with
        the raw document.

    ins_cost_func: function that returns the cost of inserting a letter,

    del_cost_func: function that returns the cost of deleting a letter,

    sub_cost_func: function that returns the cost of substituting a letter,

    Returns
    =======

    result: list of (score, message) tuples.
        The result list is sorted by score such that the closest match
        is the top result in the list.

    """
    # YOUR CODE HERE
    result = []
    for msg in msgs:
        message = (msg['text']).lower()
        score = edit_distance(query, message, ins_cost_func,
                              del_cost_func, sub_cost_func)
        result.append((score, msg))
    result = sorted(result, key=lambda x: x[0])
    return result
#############################


@app.route("/")
def home():
    return render_template('base.html', title="sample html")


@app.route("/colleges")
def college_search():
    result = []
    state_city = request.args.get("title")
    size = request.args.get("size")
    region = request.args.get("location")
    if region == "":
        result = sql_search(state_city.upper(), size, request.args.get("sort"))
    elif state_city == "":
        result = sql_search2(region.lower(), size, request.args.get("sort"))
    elif region != "" and state_city != "":
        result = sql_search3(state_city.upper(),
                             region.lower(), size, request.args.get("sort"))
    for elem in result:
        if elem['website'][0:5] != 'https':
            elem['website'] = "https://" + str(elem['website'])
    if result == []:
        result = [{'messages': "College not found :("}]
        return result
    return result


# app.run(debug=True)
