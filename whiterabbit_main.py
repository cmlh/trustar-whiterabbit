import logging
from flask import Flask
from whiterabbit import WhiteRabbit

app = Flask(__name__, static_url_path='/static/')
whiterabbitTool = WhiteRabbit()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


@app.route("/")
def get_index():
    return app.send_static_file('index.html')


@app.route("/malware")
def get_malware_families():
    return whiterabbitTool.get_malware_families()


@app.route("/balances/<family>")
def get_cluster_balances(family):
    return whiterabbitTool.get_cluster_balances(family)


if __name__ == '__main__':

    """
    Runs Flask app and parses command line arguments
    """
    logger.info("-------------< WhiteRabbit Application >-------------")

    # Start WhiteRabbit
    app.run(host='0.0.0.0', debug=True, port=5009)
