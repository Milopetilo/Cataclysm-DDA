#!/usr/bin/env python3

"""
Can be run in /json and /mods, to run on specific maps
just temporarily move them to their own folder.
"""
import argparse
import json
import os
import re

args = argparse.ArgumentParser()
args.add_argument("dir", action="store", help="specify json directory")
args_dict = vars(args.parse_args())

failures = set()
containers_removed_dic = { }


def gen_new(dir_path):
    change = False
    with open(dir_path, "r", encoding="utf-8") as json_file:
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError:
            failures.add(
                "Json Decode Error at:\n" +
                dir_path +
                "\nEnsure that the file is a JSON"
                "file consisting of an array of objects!"
            )
            return None
        for jo in json_data:
            if (isinstance(jo, dict)):
                if (
                    ("type" in jo and "container" in jo and "id" in jo) and
                    (jo["type"] == "COMESTIBLE" or jo["type"] == "AMMO" or jo["type"] == "GENERIC")

                ):
                    containers_removed_dic[jo["id"]] = jo["container"]
                    del jo["container"]
                    change = True
    return json_data if change else None


def format_json(dir_path):
    file_path = os.path.dirname(__file__)
    format_path_linux = os.path.join(file_path, "../format/json_formatter.cgi")
    path_win = "../format/json_formatter.exe"
    format_path_win = os.path.join(file_path, path_win)
    if os.path.exists(format_path_linux):
        os.system(f"{format_path_linux} {dir_path}")
    elif os.path.exists(format_path_win):
        os.system(f"{format_path_win} {dir_path}")
    else:
        print("No json formatter found")


for root, directories, filenames in os.walk(args_dict["dir"]):
    for filename in filenames:
        path = os.path.join(root, filename)
        if path.endswith(".json"):
            new = gen_new(path)
            if new is not None:
                with open(path, "w", encoding="utf-8") as jf:
                    json.dump(new, jf, ensure_ascii=False)
                format_json(path)
output_list = []
for item in containers_removed_dic:
    output_list.append({ "type": "item_group",
                         "id": item + "_" + containers_removed_dic[item],
                         "//": "Auto-generated itemgroup, might be incorrect",
                         "subtype": "collection",
                         "container-item": "" + containers_removed_dic[item],
                         "entries": [
                             { "item": item, "prob": 100 }
                         ] })
    file_path = os.path.dirname(__file__)
    output_path = os.path.join(file_path, "../container_itemgroups.json")
    with open(output_path, "w") as output:
        json.dump(output_list, output, indent=4)

for root, directories, filenames in os.walk(args_dict["dir"]):
    for filename in filenames:
        path = os.path.join(root, filename)
        if path.endswith(".json") and "itemgroups" in path:
            with open(path, "r", encoding="utf-8") as f:
                file_content = f.read()
                print("Working on file: " + path)
                for key in containers_removed_dic:
                    pattern = r'"item": "' + re.escape(str(key)) + '"'
                    file_content = re.sub(pattern, r'"group": "' + key + "_" + containers_removed_dic[key] + '"',
                                          file_content)
            with open(path, "w", encoding="utf-8") as jf:
                jf.write(file_content)
                format_json(path)
format_json(os.path.join(os.path.dirname(__file__), "../container_itemgroups.json"))
for statement in failures:
    print(statement)
