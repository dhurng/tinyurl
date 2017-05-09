"""
Design a service like tiny url

String mapping Algorithm to map long strings to short strings ( Base 62)
 A simple web framework (Flask, Tornado) that redirects a short URL to Original URL

 Can remember the URL. Easy to maintain.
Can use the links where there are restrictions in text length Ex. Twitter.
"""
from flask import Flask, redirect, url_for, request, render_template
from math import floor
from sqlite3 import OperationalError
import string, sqlite3
from urlparse import urlparse


def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INT PRIMARY KEY     AUTOINCREMENT,
        URL  TEXT    NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass

# Base62 Algorithm to encode and decode
def convert_Base62(num, b = 62):
    if b <= 0 or b > 62:
        return 0
    # all 62 possibilities
    base = string.digits + string.lowercase + string.uppercase

    index = num % b
    # determine character
    res = base[index];
    q = floor(num / b)

    while q:
        index = q % b
        q = floor(q / b)
        res = base[int(index)] + res
    return res

def convert_Base10(num, b = 62):
    base = string.digits + string.lowercase + string.uppercase

    limit = len(num)
    res = 0
    # xrange of efficiency
    for i in xrange(limit):
        res = b * res + base.find(num[i])
    return res

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        original_url = request.form.get('url')
        if urlparse(original_url).scheme == '':
            original_url = 'http://' + original_url
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()

            insert_row = """
                INSERT INTO WEB_URL (URL)
                    VALUES ('%s')
                """%(original_url)

            result_cursor = cursor.execute(insert_row)
            encoded_string = toBase62(result_cursor.lastrowid)

        return render_template('home.html',short_url= host + encoded_string)
    return render_template('home.html')

@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded_string = toBase10(short_url)
    redirect_url = 'http://localhost:5000'
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        select_row = """
                SELECT URL FROM WEB_URL
                    WHERE ID=%s
                """%(decoded_string)
        result_cursor = cursor.execute(select_row)
        try:
            redirect_url = result_cursor.fetchone()[0]
        except Exception as e:
            print e
    return redirect(redirect_url)


if __name__ == '__main__':
    table_check()
    app.run(debug=True)