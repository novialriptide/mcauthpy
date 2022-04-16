import requests
import json


def get_database() -> json:
    response = requests.get(
        "https://gitlab.bixilon.de/bixilon/minosoft/-/raw/master/src/main/resources/assets/minosoft/mapping/versions.json"
    )
    return response.json()


def get_packets(protocol_id: int) -> json:
    db = json.load(open("data/versions.json", "r"))

    if isinstance(db[str(protocol_id)]["packets"], int):
        packets = db[str(db[str(protocol_id)]["packets"])]

    elif isinstance(db[str(protocol_id)]["packets"], dict):
        packets = db[str(protocol_id)]

    return packets


if __name__ == "__main__":
    db = get_database()
    json.dump(db, open("data/versions.json", "w"), indent=4)
