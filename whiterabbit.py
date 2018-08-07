import os
import logging
import pandas as pd
from py2neo import Graph
from json import dumps
from flask import Response, jsonify

logger = logging.getLogger(__name__)
graph = Graph(password="rabbithole", bolt=False)
# graph = Graph(password="rabbithole")
# graph = Graph("0.0.0.0:7678/db/data", bolt=True, user="neo4j", password="rabbithole")


class WhiteRabbit(object):

    def __init__(self):
        logger.info("Connecting to Neo4j data store")
        try:
            self.graph = graph
        except Exception as e:
            logger.error("Connection to Neo4j data store failed")
            logger.error(e)

    @staticmethod
    def serialize_malware(malware):
        """Serialize the malware node from a Neo4j query result to be used by the client."""
        return {
            'family': malware['family'],
            'first_seen': malware['first_seen']
        }

    @staticmethod
    def serialize_seed(seed):
        """Serialize the BTC address node and seed ransomware relationship from a
        query result to be used by the client.
        """
        return {
            'address': seed[0],
            'source': seed[1]
        }

    def get_malware_families(self):
        """Return a list of the malware families in the database."""
        logger.info("Fetching list of malware families")
        results = self.graph.run("MATCH (m:MALWARE) RETURN m ORDER BY m.first_seen DESC")
        return Response(dumps({"malwareFamilies": [self.serialize_malware(record['m']) for record in results]}),
                        mimetype="application/json")

    def get_malware_family(self, family):
        """Return a list of the seed BTC addresses and their sources for the given malware family."""
        logger.info("Getting seed BTC addresses and their sources for %s", family)
        results = self.graph.run(
            "MATCH (m:MALWARE {family:{family}}) "
            "OPTIONAL MATCH (m)-[r:SEED]->(a:BTC_ADDRESS) "
            "RETURN m.family as family, collect([a.address,r.source]) as seeds "
            "LIMIT 1", {"family": family}).data()

        result = results[0]
        return Response(dumps({"family": result['family'],
                               "seeds": [self.serialize_seed(member) for member in result['seeds']]}),
                        mimetype="application/json")

    def get_balances(self, family):
        """Fetch the precomputed historical balances for the given family."""
        logger.info("Getting history for family %s", family)
        if family:
            balances_list = []
            # Find the file in that directory with the malware family as the prefix
            for file in os.listdir("balances"):
                if file.startswith(family) & file.endswith(".csv"):
                    balances_csv = os.path.join("balances", file)
                    logger.info(balances_csv)
                    df = pd.read_csv(balances_csv)
                    chart_data = df.to_dict(orient='records')
                    balances_list.append(chart_data)
            return Response(dumps(balances_list), mimetype="application/json")
        return "Failed to fetch balances"

    def get_graph(self, family):
        """Get a graph for the family where the nodes are the malware family, its
        seed addresses, and the clustered addresses; the links are the seed
        relationships and cluster relationships.
        """
        logger.info("Getting graph for family %s", family)
        results = []
        if family:
            results = self.graph.run(
                "MATCH (m:MALWARE {family:{family}})-[r:SEED]->(a:BTC_ADDRESS) "
                "WITH m.family as family, a.address as address, r.source as source "
                "LIMIT 100 "
                "RETURN family, collect([address, source]) as seeds "
                "LIMIT 1", {"family": family})
        nodes = []
        rels = []
        for record in results:
            nodes.append({"id": record["family"], "group": 1, "label": "malware"})
            for seed in record['seeds']:
                seed_address = {"id": seed[0], "group": 2, "label": "seed_address"}
                nodes.append(seed_address)
                rels.append({"source": record["family"], "target": seed[0], "value": 1})
        return Response(dumps({"nodes": nodes, "links": rels}),
                        mimetype="application/json")

    def import_ransomware_seeds(self):
        """
        Imports the BTC seed addresses with their associated malware family name and original source.
        """
        logger.info("Importing seed ransomware addresses")
        try:
            self.graph.run("CREATE INDEX ON :BTC_ADDRESS(address)")
            self.graph.run("CREATE INDEX ON :MALWARE(family)")
            self.graph.run(
                "USING PERIODIC COMMIT 500 "
                "LOAD CSV WITH HEADERS "
                "FROM 'file:///seed_addresses.csv' AS csvLine "
                "MERGE (m:MALWARE { family: csvLine.malware, first_seen: csvLine.first_seen }) "
                "MERGE (a:BTC_ADDRESS { address: csvLine.address }) "
                "MERGE (m)-[:SEED { source: csvLine.source }]->(a)")
            return "Successfully imported seed addresses."
        except Exception as e:
            logger.error("Failed to store seed addresses from CSV")
            logger.error(e)
            return "Failed to import"
