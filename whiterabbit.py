import logging
from py2neo import Graph
from json import dumps
from flask import Response, request

logger = logging.getLogger(__name__)
graph = Graph(password="rabbithole")


class WhiteRabbit(object):

    def __init__(self, ransom_seeds, scam_seeds):
        self.graph = graph
        self.ransom_seeds = ransom_seeds
        self.scam_seeds = scam_seeds
        self.current_family = None

    def _import_seeds(self, seed_type, seed_file_name):
        self.graph.run("CREATE INDEX ON :BTC_ADDRESS(address)")
        self.graph.run("CREATE INDEX ON :{}(family)".format(seed_type.upper()))
        self.graph.run(
            "USING PERIODIC COMMIT 500 " +
            "LOAD CSV WITH HEADERS " +
            "FROM 'file:///{}' AS csvLine ".format(seed_file_name) +
            "MERGE (m:SCAM { family: csvLine.{} }) ".format(seed_type.lower()) +
            "MERGE (a:BTC_ADDRESS { address: csvLine.address }) " +
            "MERGE (m)-[:SEED { source: csvLine.source }]->(a)")

    def start(self):
        if self.ransom_seeds:
            self.import_ransomware_seeds()
        if self.scam_seeds:
            self.import_scam_seeds()

    @staticmethod
    def serialize_malware_family(malware):
        return {
            # 'id': malware['id'],
            'family': malware['family'],
        }

    @staticmethod
    def serialize_btc_addr(btc_addr):
        return {
            # 'id': btc_addr['id'],
            # 'hash160': btc_addr['hash160'],
            'address': btc_addr[0],
            'source': btc_addr[1]
            # 'n_tx': btc_addr['n_tx'],
            # 'n_undredeemed': btc_addr['n_undredeemed'],
            # 'total_received': btc_addr['total_received'],
            # 'total_sent': btc_addr['total_sent'],
            # 'final_balance': btc_addr['final_balance']
        }

    @staticmethod
    def serialize_btc_txn(txn):
        return {
            # 'id': txn['id'],
            'hash': txn['hash'],
            'ver': txn['ver'],
            # 'vin_sz': txn['vin_sz'],
            # 'vout_sz': txn['vout_sz'],
            'lock_time': txn['lock_time'],
            # 'relayed_by': txn['relayed_by'],
            'size': txn['size'],
            'block_height': txn['block_height'],
            'tx_index': txn['tx_index']
        }

    def get_graph(self, family):
        logger.info("Getting graph for %s", family)
        results = self.graph.run(
            "MATCH (m:MALWARE {family:{family}})-[r:SEED]->(seed:BTC_ADDRESS) "
            "WITH m.family as family, seed.address as seed_address, r.source as source "
            "LIMIT 500 "
            "RETURN family, collect([seed_address, source]) as seeds "
            "LIMIT 1", {"family": family}).data()
        nodes = []
        rels = []
        for record in results:
            nodes.append({"id": record["family"], "group": 1, "label": "malware"})
            for seed in record['seeds']:
                seed_address = {"id": seed[0], "group": 2, "label": "seed_address"}
                nodes.append(seed_address)
                rels.append({"source": record["family"], "target": seed[0], "value": 1})
        return Response(dumps({"nodes": nodes, "links": rels}), mimetype="application/json")

    def get_search(self, q):
        logger.info("Searching for %s", q)
        results = self.graph.run(
            "MATCH (malware:MALWARE) "
            "WHERE malware.family =~ {family} "
            "RETURN malware", {"family": "(?i).*" + q + ".*"}).data()
        return Response(dumps([self.serialize_malware_family(record['malware']) for record in results]),
                        mimetype="application/json")

    def get_malware_family(self, family):
        logger.info("Getting malware family for %s", family)
        results = self.graph.run(
            "MATCH (malware:MALWARE {family:{family}}) "
            "OPTIONAL MATCH (malware)-[r:SEED]->(seed:BTC_ADDRESS) "
            "RETURN malware.family as family, collect([seed.address,r.source]) as seeds "
            "LIMIT 1", {"family": family}).data()

        result = results[0]
        self.current_family = result["family"]
        return Response(dumps({"family": result['family'],
                               "seeds": [self.serialize_btc_addr(member) for member in result['seeds']]}),
                        mimetype="application/json")

    def get_malware_families(self):
        results = self.graph.run("MATCH (malware:MALWARE) RETURN malware.family as family").data()
        return Response(dumps({"malwareFamilies": results}), mimetype="application/json")

    def import_ransomware_seeds(self):
        """
        Imports the BTC ransomware seed addresses with their associated family name and original source.
        """
        logger.info("Importing seed ransomware addresses")
        self._import_seeds(seed_type='malware', seed_file_name='seed_ransom_addresses.csv')

    def import_scam_seeds(self):
        """
        Imports the BTC scam seed addresses with their associated family name and original source.
        """
        logger.info("Importing seed scam addresses")
        self._import_seeds(seed_type='scam', seed_file_name='seed_scam_addresses.csv')
