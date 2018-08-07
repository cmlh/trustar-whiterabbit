import blocksci
import logging
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


class BlockSciTool:

    CHAIN_PATH = "/home/ubuntu/bitcoin"
    # Every 5-15 minutes, a new block is mined.
    AVG_BLOCKS_PER_HOUR = 6
    AVG_BLOCKS_PER_DAY = AVG_BLOCKS_PER_HOUR * 24
    AVG_BLOCKS_PER_WEEK = AVG_BLOCKS_PER_DAY * 7
    AVG_BLOCKS_PER_MONTH = AVG_BLOCKS_PER_WEEK * 4 + 2 * AVG_BLOCKS_PER_HOUR
    AVG_BLOCKS_PER_YEAR = AVG_BLOCKS_PER_MONTH * 12

    def __init__(self):
        self.chain = blocksci.Blockchain(self.CHAIN_PATH)

    def cluster_by_cospend(self):
        """Use the BlockSci Multi-Input "Co-Spend" Heuristic"""
        logger.info("Clustering addresses by co-spend heuristic")
        heuristic = blocksci.heuristics.change.legacy() - blocksci.heuristics.change.legacy()
        cluster = blocksci.cluster.ClusterManager.create_clustering(location=self.CHAIN_PATH + "/clusters/cospend",
                                                                    chain=self.chain,
                                                                    heuristic=heuristic,
                                                                    should_overwrite=True)
        return cluster

    def cluster_by_address(self, cluster, address):
        """Perform clustering for the given address using the given heuristic and store
         the output using the .dat extension at the filepath given.
         """
        cluster_with_address = None
        btc_address = self.chain.address_from_string(address)
        if btc_address:
            cluster_with_address = cluster.cluster_with_address(address=btc_address)
        return cluster_with_address

    def get_cluster_addresses(self, cluster):
        """Return a list of addresses in the cluster with their current balance, type
        (e.g. public key, multi-signature address), first transaction datetime and
        block height."""
        cluster_addresses = []
        for address in cluster.addresses:
            try:
                addr_first_tx = address.first_tx
                addr_first_tx_time = addr_first_tx.block_time
                addr_first_tx_height = addr_first_tx.block_height
                addr_string = address.address_string
                cluster_addresses.append(({"address": addr_string,
                                           "first_tx_time": addr_first_tx_time,
                                           "first_tx_height": addr_first_tx_height}))
            except Exception as e:
                logger.error("Could not append address. Skipping.")
                logger.error(e)
        return cluster_addresses

    def get_cluster_balances(self, cluster=None, start=None):
        payments = cluster.txes()
        df_payments = self.get_payments_df(payments)
        heights = df_payments.sort_values(by="height")["height"].values
        balances = self.get_balances_via_heights_list(cluster=cluster, heights=heights)
        df = pd.DataFrame(balances, columns=["height", "balance"])
        df = self.get_dollars_df(df, "balance")
        return df

    def get_balances_via_heights_list(self, cluster=None, heights=None):
        return [(int(height), cluster.balance(int(height))) for height in heights]

    def get_payments_df(self, txes):
        payments = [(tx.block_height, tx.input_value) for tx in txes]
        df = pd.DataFrame(payments, columns=["height", "payment"])
        return self.get_dollars_df(df, "payment")

    def get_dollars_df(self, df=None, column_name=None):
        df.index = df["height"]
        converter = blocksci.CurrencyConverter()
        df = self.chain.heights_to_dates(df)
        df["usd"] = df.apply(lambda x: converter.satoshi_to_currency(x[column_name], self.chain[x["height"]].time), axis=1)
        df.index.name = "datetime"
        return df

    def get_lifetime(self, address):
        address_value = address.address_string
        first_block_time = address.first_tx.block_time
        first_block_height = address.first_tx.block_height
        last_time_block = address.in_txes()[-1].block_time
        last_block_height = address.in_txes()[-1].block_height
        life_time = address.in_txes()[-1].block_time - address.first_tx.block_time
        return (address_value,
                first_block_time,
                first_block_height,
                last_time_block,
                last_block_height,
                life_time)

    def get_lifetimes(self, addresses):
        return [self.get_lifetime(address) for address in addresses]
