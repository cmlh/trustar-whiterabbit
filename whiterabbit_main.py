#!/usr/bin/env python
import logging
from flask import Flask, request
from whiterabbit import WhiteRabbit

app = Flask(__name__, static_url_path='/static/')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


@app.route("/")
def get_index():
    return app.send_static_file('index.html')


@app.route("/malware/<family>")
def get_malware_family(family):
    return whiterabbit.get_malware_family(family)


@app.route("/malware")
def get_malware_families():
    return whiterabbit.get_malware_families()


@app.route("/graph/<family>")
def get_graph(family):
    return whiterabbit.get_graph(family)


@app.route("/search")
def get_search():
    query = request.args["q"]
    if query:
        logger.debug("Searching for %s", query)
        return whiterabbit.get_search(query)
    else:
        logger.debug("No search term passed")
        return []


if __name__ == '__main__':

    """
    Runs Flask app and parses command line arguments
    """
    logger.info("-------------< WhiteRabbit Application >-------------")

    # Start WhiteRabbit
    whiterabbit = WhiteRabbit()

    app.run(debug=True, port=5009)
