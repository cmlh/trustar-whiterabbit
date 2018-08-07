import logging
from flask import Flask
from whiterabbit import WhiteRabbit

app = Flask(__name__, static_url_path='/static/')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


@app.route("/")
def get_index():
    return app.send_static_file('index.html')


@app.route("/malware/<family>")
def get_malware_family(family):
    return whiterabbitTool.get_malware_family(family)


@app.route("/malware")
def get_malware_families():
    return whiterabbitTool.get_malware_families()


@app.route("/graph/<family>")
def get_graph(family):
    return whiterabbitTool.get_graph(family)


@app.route("/balances/<family>")
def get_balances(family):
    return whiterabbitTool.get_balances(family)


@app.route("/import")
def import_ransomware_seeds():
    return whiterabbitTool.import_ransomware_seeds()


if __name__ == '__main__':

    """
    Runs Flask app and parses command line arguments
    """
    logger.info("-------------< WhiteRabbit Application >-------------")

    # Start WhiteRabbit
    whiterabbitTool = WhiteRabbit()
    app.run(host='0.0.0.0', debug=True, port=5009)
    # app.run(host='localhost', debug=True, port=5009)
