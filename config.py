from pathlib import Path
import json

class Config:
    def __init__(self):
        with open(str(Path(__file__).parent) + "/secret.json") as f:
            self.overview = json.load(f)

    _start_panic_gifs = [
        "https://media.tenor.co/videos/64b8b60e40e40b674d96ebd625839e52/mp4",
        "https://media.tenor.co/videos/969d12eb6bf45cedc0e5be292aad9cdf/mp4",
        "https://media.tenor.co/videos/03b16236f66bb9c4627db19f76726bb2/mp4",
        "https://tenor.com/view/panic-time-to-panic-is-my-house-okay-simpsons-breaking-news-gif-12267791"
    ]

    _end_panic_gifs = [
        "https://tenor.com/view/chi-gif-4373114",
        "https://tenor.com/view/fine-this-is-fine-gif-11131666",
        "https://tenor.com/view/calm-down-gif-5362498",
        "https://tenor.com/view/victory-blunt-smoke-cigarette-celebrate-bryce-gif-14525627",
        "https://tenor.com/view/daddy-chill-calm-down-wait-gif-14383390"
    ]


