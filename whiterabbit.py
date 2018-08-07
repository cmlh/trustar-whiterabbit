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
            families = {row["malware"]: {"family": row["malware"], "first_seen": row["first_seen"]} for row in reader}
        return Response(dumps(list(families.values())), mimetype="application/json")

    def get_balances(self, family):
        """Fetch the precomputed historical balances for the given family."""
        self.logger.info("Getting history for family %s", family)
        if family:
            balances_list = []
            # Find the file in that directory with the malware family as the prefix
            for file in os.listdir("balances"):
                start_string = family.replace(" ", "_") + "_balance"
                if file.startswith(start_string) & file.endswith(".csv"):
                    balances_csv = os.path.join("balances", file)
                    self.logger.info(balances_csv)
                    df = pd.read_csv(balances_csv)
                    chart_data = df.to_dict(orient='records')
                    balances_list.append(chart_data)
            return Response(dumps(balances_list), mimetype="application/json")
        return "Failed to fetch balances"
