#!/usr/bin/env python
import logging
import argparse
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
    try:
        q = request.args["q"]
        if q:
            return whiterabbit.get_search(q)
    except KeyError:
        return []


def parse_cmd_line_args():
    """
    Process the command line arguments given while starting the script
    """
    parser = argparse.ArgumentParser("WhiteRabbit")
    parser.add_argument("-s",
                        "--seeds",
                        help="Path to BTC seed ransomware addresses CSV",
                        required=False)
    args = parser.parse_args()
    return args


def signal_handler(signum, frame):
    """ Handles Signals
    :param signum: Signal Number
    :param frame: frame
    :return:
    """
    logger.info("Received signal {}".format(signum))
    # whiterabbit.stop()


if __name__ == '__main__':

    """
    Runs Flask app and parses command line arguments
    """
    logger.info("-------------< WhiteRabbit Application >-------------")

    # Get command line arguments
    args = parse_cmd_line_args()
    seeds = args.seeds
    if seeds:
        logger.info("Seeds found: %s", seeds)

    # Start TruStash
    whiterabbit = WhiteRabbit(seeds)
    whiterabbit.start()

    app.run(debug=True, port=8080)
