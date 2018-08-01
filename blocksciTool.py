import blocksci
import logging
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


class BlockSciTool:

    CHAIN_PATH = "/home/ubuntu/bitcoin"
    LATEST_BLOCK = 532379
    # Every 5-15 minutes, a new block is mined.
    AVG_BLOCKS_PER_HOUR = 6
    AVG_BLOCKS_PER_DAY = AVG_BLOCKS_PER_HOUR * 24
    AVG_BLOCKS_PER_WEEK = AVG_BLOCKS_PER_DAY * 7
    AVG_BLOCKS_PER_MONTH = AVG_BLOCKS_PER_WEEK * 4 + 2 * AVG_BLOCKS_PER_HOUR
    AVG_BLOCKS_PER_YEAR = AVG_BLOCKS_PER_MONTH * 12

    def __init__(self):
        self.chain = blocksci.Blockchain(self.CHAIN_PATH)

    def cluster_by_change_legacy(self, seed):
        """
        Use the BlockSci Change Legacy Heuristic and Multi-Input Heuristic
        (https://citp.github.io/BlockSci/reference/heuristics/change.html#blocksci.heuristics.change.legacy)
        to cluster addresses that have been
        :param seed: seed address
        """
        heuristic = blocksci.heuristics.change.legacy()
        self.cluster_with_heuristic(seed, heuristic, self.CHAIN_PATH + "/clusters/change_legacy")

    def cluster_by_no_change(self, seed):
        """
        Use the BlockSci Multi-Input Heuristic
        :param seed: seed address
        """
        logger.info("Clustering address %s by no change heuristic", seed)
        heuristic = blocksci.heuristics.change.legacy() - blocksci.heuristics.change.legacy()
        self.cluster_with_heuristic(seed, heuristic, self.CHAIN_PATH + "/clusters/no_change")

    def cluster_with_heuristic(self, seed, heuristic, filepath):
        """
        Perform clustering for the given address using the given heuristic and store the output
        using the .dat extension at the filepath given.
        :param seed: seed address string to build cluster for
        :param heuristic: BlockSci heuristic to build cluster with
        :param filepath: location to store the output .dat file
        """
        address = self.chain.address_from_string(seed)
        cluster = blocksci.cluster.ClusterManager.create_clustering(filepath, self.chain, heuristic, True)

        cluster_with_address = cluster.cluster_with_address(address)

        # Can be expensive to compute when the cluster is large
        n_addresses = cluster_with_address.cluster_num
        logger.debug("Found %d addresses", n_addresses)

        balances = []
        addresses = []
        for address in cluster_with_address.addresses:
            # Divide by Satoshis
            the_balance = address.balance(self.LATEST_BLOCK) / 1e8
            if the_balance > 0.0:
                balances.append(the_balance)
                addresses.append(address)
                logger.debug("Address %s has %d BTC", address, the_balance)

    def get_cluster_balances(self, cluster, time_range):
        starting_block = self.LATEST_BLOCK - 4 * self.AVG_BLOCKS_PER_MONTH
        if time_range is None:
            time_range = range(starting_block, self.LATEST_BLOCK)

        time_balances = [(i, cluster.balance(i) / 1e8) for i in time_range]
        df = pd.DataFrame(time_balances, columns=["height", "balance"])
        df.index = df["height"]
        return time_balances
