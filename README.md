# TruSTAR WhiteRabbit
This tool clusters Bitcoin (BTC) seed addresses and other threat intelligence data involved in ransomware
attacks in order to provide historical trends. Users can visualize daily, weekly, and monthly activity in these
clusters and correlate them to infrastructure (IPs, URLs, hashes) used off the blockchain as well as Google
trends.

## Recompute Clusters

WhiteRabbit runs on `python 3.5.x`.

1. Follow BlockSci instructions (https://citp.github.io/BlockSci/readme.html#quick-setup-using-amazon-ec2) 
for setting up an EC2 instance to run BlockSci.


## Running WhiteRabbit Locally

1. Set up Virtual Environment.

`python3 -m venv .venv-whiterabbit`

`source .venv-whiterabbit/bin/activate`

2. Install Python dependencies.

`pip3 install -r requirements.txt`

3. Run WhiteRabbit.

`python3 whiterabbit_main.py`

## Configurations

## Logging

Logging can be configured from `config/logging.conf`
