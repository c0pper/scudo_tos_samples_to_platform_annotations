import xml.etree.ElementTree as ET
from pathlib import Path
import regex
import os
import pandas as pd


def insert(originalfile, string):
    """
    Insert text at the beginning of file, used to prepend xml header
    :param originalfile:
    :param string:
    :return:
    """
    print(f"inserting at the top of {originalfile.name}")
    with open(originalfile, 'r', encoding="UTF8") as f:
        with open('newfile.txt', 'w', encoding="UTF8") as f2:
            f2.write(string)
            f2.write(f.read())
    os.remove(originalfile)
    os.rename('newfile.txt', originalfile)


def remove_extra_tags(tags_to_keep: list, text: str):
    """
    Remove extra tags from document to avoid confusing the xml parser with sub tags for which the main text is not extracted
    :param tags_to_keep:
    :param text:
    :return:
    """
    print(f"removing extra tags except {tags_to_keep}")
    tags = ["a", "ch", "cr", "j", "law", "ltd", "pinc", "ter", "use"]
    if not any(x in tags_to_keep for x in tags):
        raise Exception("tag_to_keep not in tags")
    else:
        tags = [item for item in tags if item not in tags_to_keep]
        # print(tags)
        for t in tags:
            pattern_open = f"<{t}.*?>"
            pattern_close = f"<\/{t}\d?>"
            text = regex.sub(pattern_open, "", text)
            text = regex.sub(pattern_close, "", text)

    return text


def clean_file(file, tags_to_keep: list):
    """

    :param file:  file contratto xml non valido
    :param tags_to_keep: lista di tipologie di clausola da tenere in considerazione
    :return: file xml valido
    """
    print(f"cleaning {file.name}")
    with open(file, 'r+', encoding="UTF8") as f:
        lines = f.readlines()
        first_line = lines[0]
        last_line = lines[-1]

    if "xml" not in first_line:
        insert(file, """<?xml version="1.0" encoding="UTF-8"?>\n<contract>\n""")

    with open(file, 'r+', encoding="UTF8") as f:
        filedata = f.read()

    # Removing question mark that messes with xml parser
    tags = ["a?", "ch?", "cr?", "j?", "law?", "ltd?", "pinc?", "ter?", "use?"]
    for t in tags:
        new = t[:-1]  # + "_"
        filedata = filedata.replace(t, new)

    # replace char that break xml parser
    filedata = filedata.replace("&", "and").replace("< ", "<").replace(" >", ">").replace("", "")

    lt = '(<)(?!(a|ch|cr|j|law|ltd|pinc|ter|use|contract|\?|/))'
    gt = '(?<!(a.?|ch.?|cr.?|j.?|law.?|ltd.?|pinc.?|ter.?|use.?|contract|\?|/|"))(>)'
    quest_mark = '(?<==)(\?)'

    filedata = regex.sub(lt, "less than ", filedata)
    filedata = regex.sub(gt, "greater than ", filedata)
    filedata = regex.sub(quest_mark, "\"UNKNOWN\"", filedata)

    filedata = remove_extra_tags(tags_to_keep, filedata)

    # Write the file out again
    with open(file, 'w', encoding="UTF8") as f:
        f.write(filedata)
        if "</contract>" not in last_line:
            f.write("\n</contract>")


def get_clauses_from_contract(xmlfile: Path, tags_to_keep: list) -> list:
    """

    :param xmlfile: file contratto xml
    :param tags_to_keep: lista di tipologie di clausola da tenere in considerazione
    :return: lista di dizionari di singole clausole trovate nel file in input
    """
    print(f"getting clauses from {xmlfile.name}")
    print(xmlfile.name)
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    clauses_dicts_list = []
    for e in list(root):
        if not e.text:  # se il testo è all interno di un altro tag innestato nel principale
            if e[0].text:
                text = e[0].text.replace("\n", " ")
        else:
            text = e.text.replace("\n", " ")
        clause_dict = {"filename": xmlfile.name, "clause_type": e.tag, "text": text}
        for k, v in e.attrib.items():
            clause_dict[k.lower()] = v
        if len(list(e)):
            for sub_e in list(e):
                clause_dict2 = {"filename": xmlfile.name, "clause_type": sub_e.tag, "text": text}
                for k, v in sub_e.attrib.items():
                    clause_dict2[k.lower()] = v
        if e.tag in tags_to_keep:
            # print(e.tag, e.text, e.attrib)
            clauses_dicts_list.append(clause_dict)
            # print({"tag": e.tag, "text": e.text, "tags": e.attrib})
    print(f"found clauses:\n{clauses_dicts_list}")
    return clauses_dicts_list


def join_references(clauses_dicts_list: list):
    # for c in clauses_dicts_list:
    #     if "id" in c.keys():
    #         if "ref" not in c.keys():  # if father is not a child itself
    #             for c2 in clauses_dicts_list:  # check if every clause has reference (is child)
    #                 if "ref" in c2.keys():
    #                     if c["id"] == c2["ref"]:  # check if found reference matches the father id
    #                         print(f"father: {c['id']} {c['text']} | child: {c2['id']} {c2['text']}")

    children = []
    for c in clauses_dicts_list:
        if "id" in c.keys():
            if "ref" in c.keys():  # is a child
                # print({"id": c["id"], "text": c["text"], "ref": c["ref"]})
                children.append({"id": c["id"], "text": c["text"], "ref": c["ref"]})
    for ch in children:  # last piece
        for cl in clauses_dicts_list:  # middle piece
            if "id" in cl.keys():
                if ch["ref"] == cl["id"]:
                    if "ref" in cl.keys():  # se la clausola che consideriamo padre ha anch'essa un padre
                        for father_clause in clauses_dicts_list:  # first piece
                            if "id" in father_clause.keys():
                                if cl["ref"] == father_clause["id"]:
                                    print("3 layers", father_clause["id"], father_clause["text"], cl["id"], cl["text"], ch["id"], ch["text"])
                    else:
                        print("2 layers", cl["id"], cl["text"], ch["id"], ch["text"])



def main(xml_folder: Path, tags_to_keep: list):
    xml_files = list(xml_folder.glob('**/*.xml'))
    print(f"starting:\nXML folder: {xml_folder}\ntags to keep:{tags_to_keep}")

    df_list = []
    for f in xml_files:
        # print(f.name)
        clean_file(f, tags_to_keep)
        list_of_clauses_in_f = get_clauses_from_contract(f, tags_to_keep)
        join_references(list_of_clauses_in_f)
        if list_of_clauses_in_f:
            for c in list_of_clauses_in_f:
                df_list.append(c)
        print("\n\n")

    # print([i for i in df_list])
    df = pd.DataFrame.from_records(df_list)
    # print(df)
    # df.to_excel(f"files/{xml_folder.name}.xlsx", index=False)


if __name__ == "__main__":
    ter_contracts_folder = Path(
        "C:/Users/smarotta/OneDrive - Expert.ai S.p.A/SCUDO/B2B/B2B eng xml/Termination_24_10_2022")

    main(xml_folder=ter_contracts_folder, tags_to_keep=["ter"])
