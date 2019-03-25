#!/usr/bin/python3
from flask import Flask, render_template, url_for, request
from elasticsearch import Elasticsearch

dest_hostname = 'elasticsearch'

app = Flask(__name__)
es = Elasticsearch([dest_hostname])

@app.route('/')
def index():
  msg = "Hello world!!\n" + "Access " + url_for('search') + " for elasticsearch demo"
  return msg

@app.route('/search', methods=["GET", "POST"])
def search():
  if request.method == "GET":
    hits = []
  if request.method == 'POST':
    account_number = request.form['account_number']
    if account_number is '':
      hits = []
    else:
      body = {
        "query": {
          "term": {
            "account_number": account_number
          }
        }
      }
      res = es.search(index="bank", body=body)
      hits = [dict(list(doc['_source'].items())) for doc in res['hits']['hits']]
  return render_template('search.html', search_results=hits)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
