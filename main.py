import json
from tqdm import tqdm
from datetime import datetime
from platform_utils.functions import create_libraries_zip, create_folder_structure, normalize_fucked_encoding, create_annotated_file

class Clause():
    def __init__(self, serv_prov: str, grade: str, text: str, tags=None):
        self.serv_prov = serv_prov
        self.grade = grade
        self.text = text
        self.tags = tags

    def collect_tags(self, clause: dict, number_of_tags: int, tag_key: str = "tag"):
        if tag_key in clause.keys():
            self.tags.append(clause[f"{tag_key}"].replace("_", ""))
            for tag_num in range(2, number_of_tags + 1):
                if f"{tag_key}{tag_num}" in clause.keys():
                    self.tags.append(clause[f"{tag_key}{tag_num}"].replace("_", ""))

        elif "explanation" in clause.keys():
            tags = clause["explanation"].split(",")
            stripped_tags = []
            for t in tags:
                stripped_tags.append(t.replace(" ", "").replace("_", ""))
            lowered_tags = []
            for t in stripped_tags:
                lowered_tags.append(t.lower())
            for t in lowered_tags:
                if not bool(t):
                    lowered_tags.remove(t)
            self.tags = lowered_tags

        self.tags.insert(0, self.grade)

    def __str__(self):
        return f"Service: {self.serv_prov} \nGrade: {self.grade} \nText: {self.text} \nTags: {self.tags}"


if __name__ == "__main__":
    ds = json.load(open("files/Fixed_08_11_2022_parsed.json", encoding="UTF8"))

    time = datetime.now().strftime('%d_%m_%y_%H_%M')
    categories = ["A", "J", "LAW", "PINC", "USE", "LTD", "CH", "CR", "TER"]
    root_path = r"C:\Users\smarotta\Desktop\scudo_ann"
    folders = create_folder_structure(root_path, timestamp=time)

    tax = []
    try:  # is the json divided in categories?
        for cat in categories:
            print("trying to iterate on categories")
            for idx, clause in enumerate(tqdm(ds[cat])):
                clause_obj = Clause(clause.get("serv_prov", ""),
                                    clause.get("grade", ""),
                                    normalize_fucked_encoding(clause.get("clause", "")),
                                    tags=[])
                clause_obj.collect_tags(clause=clause, number_of_tags=5, tag_key="tag")

                create_annotated_file(
                    folders=folders,
                    filename=f"{clause_obj.grade}_{idx+2}",
                    text=clause_obj.text,
                    annotations=clause_obj.tags
                )

                # for t in clause_obj.tags:
                #     tax.append(t)
        create_libraries_zip(folders=folders, timestamp=time)
    except KeyError:
        print("trying to iterate on Sheet1")
        for idx, clause in enumerate(tqdm(ds["Sheet1"])):
            clause_obj = Clause(
                clause.get("serv_prov", ""),
                clause.get("grade", ""),
                normalize_fucked_encoding(clause.get("clause", "")),
                tags=[])

            clause_obj.collect_tags(clause=clause, number_of_tags=5, tag_key="tag")

            create_annotated_file(
                folders=folders,
                filename=f"{clause_obj.grade}_{idx+2}",
                text=clause_obj.text,
                annotations=clause_obj.tags
            )
        create_libraries_zip(folders=folders, timestamp=time)
    except TypeError:
        for idx, clause in enumerate(tqdm(ds)):
            clause_obj = Clause(
                clause.get("serv_prov", ""),
                clause.get("grade", ""),
                normalize_fucked_encoding(clause.get("clause", "")),
                tags=[])

            clause_obj.collect_tags(clause=clause, number_of_tags=5, tag_key="tag")

            create_annotated_file(
                folders=folders,
                filename=f"{clause_obj.grade}_{idx+2}",
                text=clause_obj.text,
                annotations=clause_obj.tags
            )
        create_libraries_zip(folders=folders, timestamp=time)

