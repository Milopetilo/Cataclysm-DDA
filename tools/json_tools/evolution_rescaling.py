#!/usr/bin/env python3

"""
Unifies "2", "3", "|" old gutters into "-" on maps using the roof_palette
which don't define their own terrain definition for said characters.
Prints the names of maps that use other palettes
alongside roof_palette to be corrected manually.
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
            if isinstance(jo, dict) and "type" in jo:
                if (
                    jo["type"] == "MONSTER" and
                    "upgrades" in jo and
                    not isinstance(jo["upgrades"], bool)
                ):
                    if "half_life" in jo["upgrades"]:
                        old_value = jo["upgrades"]["half_life"]
                        new_value = old_value * 4
                        jo["upgrades"]["half_life"] = new_value
                        change = True
                    if "age_grow" in jo["upgrades"]:
                        old_value = jo["upgrades"]["age_grow"]
                        new_value = old_value * 4
                        jo["upgrades"]["age_grow"] = new_value
                        change = True
                elif (
                    jo["type"] == "monstergroup" and
                    "monsters" in jo
                ):
                    for monster in jo["monsters"]:
                        if "starts" in monster:
                            old_starts = str(monster["starts"])
                            old_starts = re.match(r"(\d+)\s*(\D*)", old_starts)
                            old_starts_number = old_starts.group(1)
                            old_starts_text = old_starts.group(2).strip()
                            monster["starts"] = str(int(old_starts_number) * 4) + " " + old_starts_text
                            change = True
                        if "ends" in monster:
                            old_starts = str(monster["ends"])
                            old_starts = re.match(r"(\d+)\s*(\D*)", old_starts)
                            old_starts_number = old_starts.group(1)
                            old_starts_text = old_starts.group(2).strip()
                            monster["ends"] = str(int(old_starts_number) * 4) + " " + old_starts_text
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

for statement in failures:
    print(statement)
