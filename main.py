import json
from corpus_functions import create_annotated_libraries, create_folder_structure, normalize_fucked_encoding
from tqdm import tqdm

class Clause():
    def __init__(self, serv_prov: str, grade: str, text: str, tags=None):
        self.serv_prov = serv_prov
        self.grade = grade
        self.text = text
        self.tags = tags

    def collect_tags(self, clause: dict, number_of_tags: int, tag_key: str = "tag"):
        if tag_key in clause.keys():
            self.tags.append(clause[f"{tag_key}"])
            for tag_num in range(2, number_of_tags + 1):
                if f"{tag_key}{tag_num}" in clause.keys():
                    self.tags.append(clause[f"{tag_key}{tag_num}"])

        elif "explanation" in clause.keys():
            tags = clause["explanation"].split(", ")
            for t in tags:
                if not bool(t):
                    tags.remove(t)
            stripped_tags = list(map(str.rstrip, tags))
            lowered_tags = list(map(str.lower, stripped_tags))
            self.tags = lowered_tags

        self.tags.insert(0, self.grade)

    def __str__(self):
        return f"Service: {self.serv_prov} \nGrade: {self.grade} \nText: {self.text} \nTags: {self.tags}"


if __name__ == "__main__":
    ds = json.load(open("balanced_dataset_fcasciola.json", encoding="UTF8"))
    categories = ["A", "J", "LAW", "PINC", "USE", "LTD", "CH", "CR", "TER"]
    root_path = r"C:\Users\smarotta\Desktop\scudo_ann"
    folders = create_folder_structure(root_path)

    for cat in categories:
        for idx, clause in enumerate(tqdm(ds[cat])):
            clause_obj = Clause(clause["serv_prov"], clause["grade"], normalize_fucked_encoding(clause["clause"]), tags=[])
            clause_obj.collect_tags(clause=clause, number_of_tags=5, tag_key="tag")

            # print(f"{clause_obj}\n")
            create_annotated_libraries(
                folders=folders,
                filename=f"{clause_obj.grade}_{idx+2}",
                text=clause_obj.text,
                annotations=clause_obj.tags
            )
            clause_obj = None

