from random import choice


class JoachimMessages:
    def __init__(self, db, config):
        self.config = config
        self.db = db

    def pdp_message(self):
        return self.config.pdp_message()

    def jap_message(self):
        return self.config.jap_message()

    def raspberry_message(self):
        return self.config.raspberry_message()

    def overview_message(self, mess_type, values):
        return choice(self.config.overview[mess_type]) + "\n" + "\n".join(
            [f"{next(values)} razy w ostatnich {value} minutach " for index, value in
             enumerate(self.config.joachim_timestamps)])
