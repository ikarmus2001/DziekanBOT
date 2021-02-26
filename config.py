from pathlib import Path
from random import choice
import json


class Config:
    def __init__(self):
        self.config_path = str(Path(__file__).parent) + "/new_config.json"

        with open(self.config_path) as f:
            self.data = json.load(f)

    def has_permission(self, command_to_execute, message):
        command_power = self.data["perms"][command_to_execute]
        if command_power == 0:
            return True

        user_roles = message.author.roles
        print(user_roles)

        for crt_power in range(command_power, 4):
            if any(user_role.id in self.data["perms_roles"][str(crt_power)] for user_role in user_roles):
                return True
        return False

    def config_save(self):
        with open(self.config_path, mode="w") as f:
            json.dump(self.data, f, indent=4)

    @property
    def token(self):
        return self.data["token"]

    @property
    def prefix(self):
        return self.data["prefix"]

    # Paniczka section
    @property
    def gif_per_channel(self):
        return 4

    def start_panic_gifs(self, number_of_gifs):
        assert len(self.data["panic"]["start_panic_gifs"]) >= number_of_gifs
        i = 0
        yielded_gifs = set()

        while i < number_of_gifs:
            if (gif := choice(self.data["panic"]["start_panic_gifs"])) not in yielded_gifs:
                yielded_gifs.add(gif)
                i += 1
                yield gif

    def end_panic_gifs(self, number_of_gifs):
        assert len(self.data["panic"]["end_panic_gifs"]) >= number_of_gifs
        i = 0
        yielded_gifs = set()

        while i < number_of_gifs:
            if (gif := choice(self.data["panic"]["end_panic_gifs"])) not in yielded_gifs:
                yielded_gifs.add(gif)
                i += 1
                yield gif
