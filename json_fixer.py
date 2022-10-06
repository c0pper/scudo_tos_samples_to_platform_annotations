import json

import corpus_functions

categories = ["A", "J", "LAW", "PINC", "USE", "LTD", "CH", "CR", "TER"]

ds = json.load(open("balanced_dataset_fcasciola.json", encoding="UTF8"))

for c in categories:
    for i in ds[c]:
        print(i["clause"])
        i["clause"] = corpus_functions.normalize_fucked_encoding(i["clause"])
        print(i["clause"])

json.dump(ds, open("balanced_dataset_fcasciola_encfix.json", "w", encoding="UTF8"), ensure_ascii=False)