import json
from random import choice
from pathlib import Path


class JoachimMessages:
    def __init__(self, db,overview):
        self.overview = overview
        self.db = db

    def pdp_message(self):
        return "pdp_message"

    def jap_message(self):
        return "jap_message"

    def rasberry_message(self):
        return "rasberry_message"

    def overview_message(self, mess_type, values):
        return (
            choice(self.overview[mess_type])
            + f"""
            {values[0]} razy w ostatnich 5 min
            {values[1]} razy w ostatnich 10 min
            {values[2]} razy w ostatnich 15 min
            {values[3]} razy w ostatnich 30 min
            {values[4]} razy w ostatnich 60 min       
        """
        )
