import logging
import psycopg2
import psycopg2.extras
from blocksciTool import BlockSciTool
# from json import dumps
# from flask import Response

logger = logging.getLogger(__name__)


class WhiteRabbit(object):

    def __init__(self, seeds):
        self.seeds = seeds
        logger.info("Initializing BlockSci blockchain")
        self.chain = BlockSciTool()
        logger.info("Connecting to PostgreSQL data store")
        try:
            self.connection = psycopg2.connect(host='localhost',
                                               dbname='whiterabbit',
                                               user='alice',
                                               password='rabbithole',
                                               connect_timeout=3)
            self.cursor = None
            self.import_seeds()
        except Exception as error:
            logger.error("Connection to PostgreSQL data store failed with error: %s", str(error))

    def compute_cluster_by_address(self, address):
        self.chain.cluster_by_no_change(address)

    def compute_clusters(self):
        logger.info("Computing clusters")
        seeds_by_family = self.get_seeds_by_family()
        for seeds in seeds_by_family:
            for seed in seeds:
                # Compute cluster
                self.compute_cluster_by_address(seed)

    def get_seeds_by_family(self, malware=None):
        logger.info("Fetching seed addresses families")
        try:
            if malware:
                query = "SELECT * " \
                        "FROM whiterabbit.seeds " \
                        "WHERE s_malware = \'{}\' " \
                        "GROUP BY s_malware;".format(malware)
            else:
                query = "SELECT * " \
                        "FROM whiterabbit.seeds " \
                        "GROUP BY s_malware;"
            logger.debug(query)
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as error:
            logger.error("Failed to fetch seed addresses with error: %s", str(error))
            return []

    def get_malware_families(self):
        logger.info("Fetching malware families")
        try:
            query = "SELECT DISTINCT s_malware FROM whiterabbit.seeds;"
            logger.debug(query)
            self.cursor.execute(query)
            self.cursor.fetchall()
        except Exception as error:
            logger.error("Failed to fetch malware families with error: %s", str(error))

    def import_seeds(self):
        """
        Imports the BTC seed addresses with their associated malware family name and original source.
        """
        logger.info("Importing seed addresses for malware families from CSV")
        try:
            query = "CREATE TABLE IF NOT EXISTS whiterabbit.seeds (" \
                    "s_id BIGINT NOT NULL, " \
                    "s_address VARCHAR NOT NULL, " \
                    "s_malware VARCHAR NOT NULL, " \
                    "s_start VARCHAR, " \
                    "s_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_DATE, " \
                    "s_last_computed TIMESTAMP WITH TIME ZONE, " \
                    "CONSTRAINT pk_seeds PRIMARY KEY (s_id), " \
                    "UNIQUE (s_address, s_malware)" \
                    "); " \
                    "COPY whiterabbit.seeds(s_address,s_malware,s_start) " \
                    "FROM 'seed_addresses.csv' DELIMITER ',' CSV;"
            logger.debug(query)
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as error:
            logger.error("Failed to store seed addresses from CSV with error: %s", str(error))
