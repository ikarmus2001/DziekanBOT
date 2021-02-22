from pathlib import Path
from random import choice
import json


class Config:
    def __init__(self):
        self.config_path = str(Path(__file__).parent) + "/new_config.json"

        with open(self.config_path) as f:
            self.data = json.load(f)

    async def has_permision(self, command_to_execute, message):
        return True

    def config_save(self):
        with open(self.config_path, mode="w") as f:
            json.dump(self.data, f, indent=4)

    def pdp_message(self):
        return choice(self.data["joachim"]["alert"]["pdp"])

    def jap_message(self):
        return choice(self.data["joachim"]["alert"]["japan"])

    def raspberry_message(self):
        return choice(self.data["joachim"]["alert"]["raspberry"])

    @property
    def joachim_timeout(self):
        return self.data["joachim"]["timeout"]

    @property
    def joachim_timestamps(self):
        return self.data["joachim"]["timestamps"]

    @property
    def token(self):
        return self.data["token"]

    @property
    def prefix(self):
        return self.data["prefix"]

    @property
    def overview(self):
        return self.data["joachim"]["overview"]

    @property
    def start_panic_gif(self):
        return choice(self.data["panic"]["start_panic_gifs"])

    @property
    def end_panic_gif(self):
        return choice(self.data["panic"]["end_panic_gifs"])
