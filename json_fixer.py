import json
from platform_utils.functions import normalize_fucked_encoding


categories = ["A", "J", "LAW", "PINC", "USE", "LTD", "CH", "CR", "TER"]

ds = json.load(open("balanced_dataset_fcasciola.json", encoding="UTF8"))

for c in categories:
    for i in ds[c]:
        print(i["clause"])
        i["clause"] = normalize_fucked_encoding(i["clause"])
        print(i["clause"])
        if "tag" in i.keys():
            i["tag"] = i["tag"].replace("_", "")
            for tag_num in range(2, 6):
                if f"tag{tag_num}" in i.keys():
                    i[f"tag{tag_num}"] = i[f"tag{tag_num}"].replace("_", "")

json.dump(ds, open("balanced_dataset_fcasciola_encfix.json", "w", encoding="UTF8"), ensure_ascii=False)