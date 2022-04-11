import requests
import json
from lxml import html

URL = "https://wiki.vg/Protocol_version_numbers"
PATH = "protocol_versions.json"

response = requests.get(URL)
content = html.fromstring(response.text)

table = content.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody')

versions_data = []


def pack_data(release_name: str, version_number: int):
    global versions_data

    versions_data.append(
        {
            "release_name": release_name,
            "versions_number": version_number,
            "protocol_encryption_uses_server_id": None,
        }
    )


old_ver = None
for x in table[0]:
    if x[0] != "Release name":
        if len(x) >= 2:
            old_ver = x[1].text_content().strip()
            pack_data(x[0].text_content().strip(), old_ver)
        elif len(x) == 1:
            pack_data(x[0].text_content().strip(), old_ver)

json.dump(versions_data, open(PATH, "w"), indent=4)
