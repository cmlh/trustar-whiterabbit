# TruSTAR WhiteRabbit
This tool clusters Bitcoin (BTC) seed addresses and other threat intelligence data involved in ransomware
attacks in order to provide historical trends. Users can visualize daily, weekly, and monthly activity in these
clusters and correlate them to infrastructure (IPs, URLs, hashes) used off the blockchain as well as Google
trends.

## Setup

WhiteRabbit runs on `python 3.6.x`.

1. Set up Neo4j Docker image.

`docker-compose up neo4j`

2. Set up Virtual Environment.

`python3 -m venv .venv-whiterabbit`

`source .venv-whiterabbit/bin/activate`

3. Install Python dependencies.

`pip install -r requirements.txt`

## Running WhiteRabbit

`python3 whiterabbit_main.py --seeds import/seed_ransom_addresses.csv`

## Configurations

## Logging

Logging can be configured from `config/logging.conf`
