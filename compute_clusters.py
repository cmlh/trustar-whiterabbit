import csv
import logging
from blocksci_tool import BlockSciTool


class ComputeClusters:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing BlockSci blockchain")
        self.chain = BlockSciTool()

    def compute_clusters(self):
        """Compute all clusters for the given seed ransomware BTC addresses."""
        self.logger.info("Computing clusters")
        try:
            seeds_by_family = {}
            with open("import/seed_addresses.csv", "r") as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                for row in reader:
                    if len(row) >= 4:
                        family = row[1]
                        seed = {"address": row[0], "first_seen": row[2]}
                        if family in seeds_by_family:
                            seeds_by_family[family].append(seed)
                        else:
                            seeds_by_family[family] = [seed]
            self.logger.debug("Found %d families with seeds", len(seeds_by_family))
            if len(seeds_by_family) > 0:
                # Build the cluster manager using the co-spend heuristic
                cluster = self.chain.cluster_by_cospend()
                self.logger.info("Co-spend cluster successfully built")
                for family, seeds in seeds_by_family.items():
                    self.logger.info("Found %d seeds for family %s", len(seeds), family)
                    for seed in seeds:
                        start = seed["first_seen"]
                        address = seed["address"]
                        self.logger.info("Finding cluster for address %s", address)
                        # Get the cluster for just the given address
                        cluster_by_address = self.chain.cluster_by_address(cluster=cluster, address=address)
                        if cluster_by_address:
                            # Save addresses in in CSV
                            cluster_addresses = self.chain.get_cluster_addresses(cluster_by_address)
                            if cluster_addresses:
                                self.save_cluster_addresses(seed=address, addresses=cluster_addresses)

                            # Save the historical balances, by block, in CSV
                            cluster_balances = self.chain.get_cluster_balances(cluster_by_address, start)
                            if cluster_balances:
                                self.save_cluster_balances(seed=address, malware=family, df=cluster_balances)
                return "Successfully computed cluster"
        except Exception as e:
            self.logger.error("Clustering failed")
            self.logger.error(e)
            return "Failed to cluster"

    def save_cluster_addresses(self, seed, addresses):
        self.logger.info("Saving %d cluster addresses for seed %s", len(addresses), seed)
        with open("balances/%s_addresses_cluster_%s.csv", 'wb') as csvfile:
            wr = csv.writer(csvfile)
            wr.writerow(addresses)

    def save_cluster_balances(self, seed, malware, df):
        self.logger.info("Saving cluster balances for seed %s and malware family %s", seed, malware)
        self.logger.info(df)
        self.logger.info("Saving to csv now.")
        df.to_csv("balances/%s_balance_cluster_%s.csv".format(malware, seed), index=False)
