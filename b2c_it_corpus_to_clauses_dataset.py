from pathlib import Path
import re
import pandas as pd

corpus_folder = Path("C:/Users/smarotta/OneDrive - Expert.ai S.p.A/SCUDO/B2C/materiali EUI/Corpus italiano/corpus_2022_it/original_xml/it")
xml_files = list(corpus_folder.glob('**/*.xml'))

ds = []
for f in xml_files:
    with open(f, "r", encoding="UTF8") as file:
        content = file.read()
        clauses = re.findall("(<\w+\d?>.*<\/\w+\d?>)", content)
        print(f.stem)
        clauses_list = []
        for c in clauses:
            text = re.findall(">(\w.*?)<\/", c)
            tags = re.findall("(<\w+\d?>)", c)
            # print(tags, text)
            clauses_list.append((tags, text))
        # print(clauses_list)
        for c in clauses_list:
            print(c)
            if c:
                if len(c[0]) == len(c[1]):  # as many tags as clauses
                    list_of_grade_clause_tup = list(zip(c[0], c[1]))
                    for i in list_of_grade_clause_tup:
                        item = {"filename": f.stem, "grade": i[0].replace("<", "").replace(">", ""), "clause": i[1]}
                        ds.append(item)
                        # print(item)
                elif len(c[0]) > len(c[1]):  # more tags 1 clause
                    try:
                        item = {"filename": f.stem, "grade": ", ".join(c[0]).replace("<", "").replace(">", ""), "clause": c[1][0]}
                        # print(item)
                        ds.append(item)
                    except IndexError:
                        print("Error: ", text)

    print("\n")
# print(ds)

df = pd.DataFrame.from_records(ds)
df.to_excel("b2c_ita.xlsx", index=False)