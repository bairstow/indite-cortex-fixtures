"""Record GGG Currency Exchange hours for indite-cortex-v2's exchange tests.

Usage: python -I tools/record-exchange-hours.py <out-dir> <league> <from-iso> <to-iso>
       python -I tools/record-exchange-hours.py --raw <out-file> <hour-iso>

Each hour is written as <out-dir>/<unix-hour>.json in GGG's response shape
({"next_change_id", "markets"}), keeping only the named league's markets whose
two ids are both in BASKET. --raw writes one hour's response unfiltered.
One request at a time, with a descriptive User-Agent. Existing files are kept.
"""

import datetime
import json
import os
import sys
import time
import urllib.request

URL = "https://web.poecdn.com/api/currency-exchange/{}"
UA = "indite-cortex/2 (read-only exchange archive; fixtures recorder)"
BASKET = {
    "Metadata/Items/Currency/CurrencyRerollRare",
    "Metadata/Items/Currency/CurrencyModValues",
    "Metadata/Items/DivinationCards/DivinationCardDeck",
    "Metadata/Items/Currency/HarvestSeedGreen",
    "Metadata/Items/Currency/HarvestSeedBlue",
    "Metadata/Items/Currency/HarvestSeedRed",
    "Metadata/Items/Currency/CurrencyDuplicate",
}


def hour(iso):
    t = datetime.datetime.fromisoformat(iso).replace(tzinfo=datetime.timezone.utc)
    return int(t.timestamp()) // 3600 * 3600


def fetch(h):
    req = urllib.request.Request(URL.format(h), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main(argv):
    if argv[0] == "--raw":
        out, h = argv[1], hour(argv[2])
        with open(out, "w", encoding="utf-8") as f:
            json.dump(fetch(h), f)
        return
    out, league, start, end = argv[0], argv[1], hour(argv[2]), hour(argv[3])
    os.makedirs(out, exist_ok=True)
    for h in range(start, end, 3600):
        path = os.path.join(out, f"{h}.json")
        if os.path.exists(path):
            continue
        d = fetch(h)
        markets = [m for m in d["markets"]
                   if m["league"] == league and set(m["market_pair"]) <= BASKET]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"next_change_id": d["next_change_id"], "markets": markets}, f,
                      separators=(",", ":"))
        time.sleep(0.2)


if __name__ == "__main__":
    main(sys.argv[1:])
