# TruSTAR WhiteRabbit
This tool clusters Bitcoin (BTC) seed addresses and other threat intelligence data involved in ransomware
attacks in order to provide historical trends. Users can visualize daily, weekly, and monthly activity in these
clusters and correlate them to infrastructure (IPs, URLs, hashes) used off the blockchain as well as Google
trends.

## Running WhiteRabbit Locally

1. Set up Virtual Environment.

`python3 -m venv .venv-whiterabbit`

`source .venv-whiterabbit/bin/activate`

2. Install Python dependencies.

`pip3 install -r requirements.txt`

3. Run WhiteRabbit.

`python3 whiterabbit_main.py`

## Logging

Logging can be configured from `config/logging.conf`

## (Re)compute Clusters

WhiteRabbit runs on `python 3.5.x`.

1. Follow BlockSci instructions (https://citp.github.io/BlockSci/readme.html#quick-setup-using-amazon-ec2) 
for setting up an EC2 instance to run BlockSci. 

2. You can disregard the other steps if you only want to experiment or interested in 
one particular seed address. An easy way is to follow the instructions given by 
the `CryptoLocker_Analysis.ipynb` notebook. This notebook should live on the same server as BlockSci. 

3. Create a file named `seed_addresses.csv` in the `import` directory. Add the following columns to the 
csb file: `address,malware,first_seen,source`.  

4. If you would like to recompute the balances you need a to run the following on the EC2 instance 
running BlockSci. 

`python3 compute_clusters_main.py` 

The working directory for BlockSci is `/home/ubuntu/bitcoin` (We noticed that BlockSci works well with 
an `r4.2xlarge` instance as recommended by the developers of BlockSci. Make sure you shut down 
the EC2 instance after you finish computing).

5. Once clustering is done the script computes their balances and stores them to:
`balances/family_balance_cluster_#.csv`
These balances are computed at transaction times where their associated Bitcoin Addresses were part 
of the transaction inputs or outputs. The balance data has the following columns:
`date,height,balance,usd`
`date` is the time of the computed balance, `height` is the block height at which we computed
the balance, `balance` is the balance in Satoshis ( 1 BTC = 1e8 Satoshis), `usd` is the balance
in US Dollars. 

