import os
import csv
import logging
import pandas as pd
from json import dumps
from flask import Response


class WhiteRabbit:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_malware_families(self):
        """Return a list of the malware families."""
        self.logger.info("Fetching list of malware families")
        with open("import/seed_addresses.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            families_map = {row["malware"]: {"family": row["malware"], "first_seen": row["first_seen"]} for row in reader}
            families_list = list(families_map.values())
            sorted_families_list = sorted(families_list, key=lambda k:k['first_seen'])
        return Response(dumps(sorted_families_list), mimetype="application/json")

    def get_cluster_balances(self, family):
        """Fetch the precomputed historical balances for the given family."""
        self.logger.info("Getting history for family %s", family)
        if family:
            clusters_by_min_height = {}
            clusters_list = []
            csv_list = self.get_cluster_balance_files(family)
            for csv_file in csv_list:
                df = pd.read_csv(csv_file)
                chart_data = df.to_dict(orient='records')
                clusters_list.append(chart_data)
            # Sort list of clusters by their minimum block height
            for cluster in clusters_list:
                heights = [i['height'] for i in cluster]
                min_height = min(heights)
                clusters_by_min_height[min_height] = cluster
            sorted_clusters = sorted(clusters_by_min_height.items(), key=lambda k:k)
            sorted_clusters_list = [ item[1] for item in sorted_clusters ]
            return Response(dumps(list(sorted_clusters_list)), mimetype="application/json")
        return "Failed to fetch cluster balances"

    @staticmethod
    def get_cluster_balance_files(family):
        """Find the files in that directory with the malware family as the prefix"""
        csv_list = []
        for file in os.listdir("balances"):
            start_string = family.replace(" ", "_") + "_balance"
            if file.startswith(start_string) & file.endswith(".csv"):
                csv_list.append(os.path.join("balances", file))
        return csv_list
