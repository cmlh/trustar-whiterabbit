import csv
import logging
from py2neo import Graph
from blocksciTool import BlockSciTool


class ComputeClusters:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        """Initialize the BlockSci Chain Neo4j graph."""
        self.logger.info("Initializing BlockSci blockchain")
        self.chain = BlockSciTool()

        self.logger.info("Connecting to Neo4j data store")
        try:
            self.graph = Graph(password="rabbithole", bolt=False)
        except Exception as e:
            self.logger.error("Connection to Neo4j data store failed")
            self.logger.error(e)

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
                            # Save metadata about the cluster in Neo4j
                            self.save_cluster(seed=address, cluster=cluster_by_address)

                            # Save addresses in Neo4j
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

    def save_cluster(self, seed, cluster):
        self.logger.info("Saving cluster metadata for seed %s", seed)
        balance = cluster.balance()

        in_txes_count = cluster.in_txes_count()
        out_txes_count = cluster.out_txes_count()

        try:
            self.graph.run("MATCH (s:BTC_ADDRESS {address:{seed}}) " +
                           "SET s.updated = timestamp(), " +
                           "s.balance = {balance}, " +
                           "s.in_txes_count = {in_txes_count}, " +
                           "s.out_txes_count = {out_txes_count}",
                           {"seed": seed,
                            "balance": balance,
                            "in_txes_count": in_txes_count,
                            "out_txes_count": out_txes_count})
        except Exception as e:
            self.logger.error("Failed to save cluster metadata for address %s", seed)
            self.logger.error(e)

    def save_cluster_addresses(self, seed, addresses):
        self.logger.info("Saving %d cluster addresses for seed %s", len(addresses), seed)
        try:
            self.graph.run("MATCH (s:BTC_ADDRESS {address:{seed}}) "
                           "UNWIND { addresses } AS a "
                           "MERGE (addr:BTC_ADDRESS { address: a.address, first_tx_time: a.first_tx_time, first_tx_height: a.first_tx_height }) "
                           "ON CREATE SET addr.address = a.address "
                           "MERGE (addr)<-[:CLUSTER { updated: timestamp() }]-(s)",
                           {"seed": seed, "addresses": addresses})
        except Exception as e:
            self.logger.error("Failed to save cluster %d addresses for seed %s", len(addresses), seed)
            self.logger.error(e)

    def save_cluster_balances(self, seed, malware, df):
        self.logger.info("Saving cluster balances for seed %s and malware family %s", seed, malware)
        self.logger.info(df)
        self.logger.info("Saving to csv now.")
        df.to_csv("balances/%s-%s.csv".format(malware, seed), index=False)
