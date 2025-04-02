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


def gen_new(path):
    change = False
    with open(path, "r", encoding="utf-8") as json_file:
        try:
            json_data = json.load(json_file)
        except json.JSONDecodeError:
            failures.add(
                "Json Decode Error at:\n" +
                path +
                "\nEnsure that the file is a JSON"
                "file consisting of an array of objects!"
            )
            return None
        for jo in json_data:
            if isinstance(jo, dict):
                if (
                    jo["type"] == "MONSTER" and
                    "upgrades" in jo and
                    not isinstance(jo["upgrades"], bool) and
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
    return json_data if change else None


def format_json(path):
    file_path = os.path.dirname(__file__)
    format_path_linux = os.path.join(file_path, "../format/json_formatter.cgi")
    path_win = "../format/json_formatter.exe"
    format_path_win = os.path.join(file_path, path_win)
    if os.path.exists(format_path_linux):
        os.system(f"{format_path_linux} {path}")
    elif os.path.exists(format_path_win):
        os.system(f"{format_path_win} {path}")
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