from pathlib import Path
import json
import pandas as pd

ann_folder = Path("C:/Users/smarotta/Downloads/training_senza_nowarning_e_fulldiscr/ann")
test_folder = Path("C:/Users/smarotta/Downloads/training_senza_nowarning_e_fulldiscr/test")

ann_files = list(ann_folder.glob('**/*.ann'))
test_files = list(test_folder.glob('**/*.txt'))

new_ds = []
for a in ann_files:
    item = {"filename": a.stem}
    for t in test_files:
        if a.stem == t.stem:
            with open(t, "r", encoding="UTF8") as test:
                print(test)
                item["clause"] = test.read().strip()
                print(item)
            with open(a, "r", encoding="UTF8") as ann:
                tags = []
                for l in ann.readlines():
                    # print(l.split(("\t\t"))[-1])
                    tags.append(l.split(("\t\t"))[-1].strip())
                print(tags)
                item["grade"] = tags[0]
                item["tags"] = ", ".join(tags[1:])
            print("\n")
    print(tags)
    new_ds.append(item)
print(new_ds)
final = json.dumps(new_ds, indent=4)


if __name__ == "__main__":
    df = pd.DataFrame.from_records(new_ds)
    df.to_excel("files/new_ds.xlsx", index=False)
    print(df)
